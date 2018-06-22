"""Primary logic for django_resetdb"""

from __future__ import print_function, unicode_literals

import os
import logging
import subprocess
from tempfile import NamedTemporaryFile


from .util import DB, kill_other_psql_sessions, psql, shell

logger = logging.getLogger(__name__)


def db_exists():
    """Test if DATABASES['default'] exists"""
    logger.info("Checking to see if %s already exists", repr(DB["NAME"]))
    try:
        # Hide stderr since it is confusing here
        psql("", stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return False
    return True


def dropdb(force=False):
    """Drop DATABASES['default']"""

    if force:
        logger.info(
            "Terminating any other connections to %s on %s",
            repr(DB["NAME"]),
            repr(DB["HOST"]),
        )
        kill_other_psql_sessions()

    logger.info("Dropping database %s", repr(DB["NAME"]))
    return shell('dropdb -U "{USER}" -h "{HOST}" "{NAME}"'.format(**DB))


def createdb():
    """Create DATABASES['default']"""

    logger.info("Creating database %s", repr(DB["NAME"]))
    # TODO: handle --encoding UTF8  --locale en_US.UTF-8
    return shell("createdb " '-U "{USER}" -h "{HOST}" {NAME}'.format(**DB))


def pg_dump(db_name, backup_path):
    """Dump db_name to backup_path"""

    logger.info("Dumping %s to %s", repr(db_name), repr(backup_path))
    return shell(
        'pg_dump "{db_name}" -U "{USER}" -h "{HOST}" '
        "--schema=public --file={backup_path}".format(
            db_name=db_name, backup_path=backup_path, **DB
        )
    )


def populate_db(sql_path):
    """Load data in the `sql_path` file into DATABASES['default']"""

    logger.info("Populating DB %s from %s", repr(DB["NAME"]), repr(sql_path))
    shell(
        'psql -U "{USER}" -h "{HOST}" -d "{NAME}" --file={sql_path}'.format(
            sql_path=sql_path, **DB
        )
    )


def cleardb(force=False):
    """Drop and create DATABASES['default']"""

    # Drop database, if it exists
    if db_exists():
        try:
            dropdb(force)
        except subprocess.CalledProcessError as error:
            output = error.output.decode("utf-8")
            if "is being accessed by other users" in output:
                raise ValueError(
                    "{}\n"
                    "To forcibly terminate other sessions, run "
                    "this command again with --force"
                    .format(output)
                )
            else:
                raise
    else:
        logger.info(
            "Database %s does not currently exist; no need to drop", repr(DB["NAME"])
        )
    createdb()


def clone_psql_db(db_to_clone):
    """Clone `db_to_clone` into DATABASES['default']"""
    # If db_to_clone is a path, assume it is a SQL dump...
    if os.path.isfile(db_to_clone):
        logger.info("Treating %s as a path to a SQL dump", repr(db_to_clone))
        # ...and use it to populate our database
        populate_db(db_to_clone)
    # Otherwise, assume it is a database name...
    else:
        logger.info("Treating %s as a database name", repr(db_to_clone))
        # ...create a temp file to dump it into...
        with NamedTemporaryFile(prefix="{}.sql.".format(db_to_clone)) as backup_file:
            # ...perform the dump...
            pg_dump(db_to_clone, backup_file.name)
            # ...and load the contents of the dump into our DB
            populate_db(backup_file.name)
