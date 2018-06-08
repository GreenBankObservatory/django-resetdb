#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Reset the Django DB"""

from __future__ import print_function, unicode_literals

import argparse
import getpass
import logging
import os
import shlex
import subprocess
import sys
from tempfile import NamedTemporaryFile

import psycopg2

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings

logger = logging.getLogger(__name__)

DB = settings.DATABASES['default']

def shell(cmd, **kwargs):
    """Execute cmd, check exit code, return stdout"""
    logger.debug("$ %s", cmd)
    try:
        return subprocess.check_output(cmd, shell=True, **kwargs)
    except subprocess.CalledProcessError as error:
        # print(error, file=sys.stderr)
        # sys.exit(1)
        raise

def psql(sql, **kwargs):
    # TODO: How to handle admin user generically?
    return shell(
        'psql -U "{USER}" -h "{HOST}" -d "{NAME}" -c "{sql}"'
        .format(sql=sql, **DB), **kwargs
    )

class Command(BaseCommand):
    help = "Resets your database"

    def add_arguments(self, parser):
        parser.add_argument(
            "-c", "--clone",
            metavar="NAME_OR_PATH",
            help="Either the name of a database to clone or a SQL dump to load"
                 "into your database"
        )
        parser.add_argument(
            "-M", "--no-migrate",
            action="store_true",
            help="Don't apply migrations after resetting the DB"
        )
        parser.add_argument(
            "-f", "--force",
            action="store_true",
            help="Forcibly close other DB sessions to allow it to be dropped"
        )

    def handle(self, *args, **options):
        if options['verbosity'] > 1:
            logger.setLevel(logging.DEBUG)

        print("Resetting your database {!r}".format(DB['NAME']))
        self.clear_db(force=options['force'])

        if options['clone']:
            print(
                "Loading {!r} into your database {!r}"
                .format(options['clone'], DB['NAME'])
            )
            self.clone_psql_db(options['clone'])

        if not options['no_migrate']:
            print("Applying migrations")
            self.migrate()


    def db_exists(self):
        """Test if DATABASES['default'] exists"""
        logger.info("Checking to see if %s already exists", repr(DB['NAME']))
        try:
            # Hide stderr since it is confusing here
            psql("", stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            return False
        return True

    def dropdb(self, force=False):
        """Drop DATABASES['default']"""
        
        if force:
            logger.info("Terminating any other connections to %s on %s",
                        repr(DB['NAME']), repr(DB['HOST']))
            self.kill_other_psql_sessions()

        logger.info("Dropping database %s", repr(DB['NAME']))
        return shell(
            'dropdb -U "{USER}" -h "{HOST}" "{NAME}"'.format(**DB)
        )

    def createdb(self, ):
        """Create DATABASES['default']"""

        logger.info("Creating database %s", repr(DB['NAME']))
        # TODO: handle --encoding UTF8  --locale en_US.UTF-8
        return shell(
            'createdb '
            '-U "{USER}" -h "{HOST}" {NAME}'
            .format(**DB)
        )

    def pg_dump(self, db_name, backup_path):
        """Dump db_name to backup_path"""

        logger.info("Dumping %s to %s", repr(db_name), repr(backup_path))
        return shell(
            'pg_dump "{db_name}" -U "{USER}" -h "{HOST}" '
            '--schema=public --file={backup_path}'
            .format(
                db_name=db_name,
                backup_path=backup_path,
                **DB
            )
        )

    def populate_db(self, sql_path):
        """Load data in the `sql_path` file into DATABASES['default']"""

        logger.info("Populating DB %s from %s", repr(DB['NAME']), repr(sql_path))
        shell(
            'psql -U "{USER}" -h "{HOST}" -d "{NAME}" --file={sql_path}'
            .format(sql_path=sql_path, **DB)
        )

    def clear_db(self, force=False):
        """Drop and create DATABASES['default']"""

        # Drop database, if it exists
        if self.db_exists():
            try:
                self.dropdb(force)
            except subprocess.CalledProcessError as error:
                output = error.output.decode('utf-8')
                if "is being accessed by other users" in output:
                    logger.error(output)
                    logger.error(
                        "To forcibly terminate other sessions, run "
                        "this command again with --force"
                    )
                    sys.exit(1)
                else:
                    raise
        else:
            logger.info("Database %s does not currently exist; no need to drop",
                        repr(DB['NAME']))
        self.createdb()

    def clone_psql_db(self, db_to_clone):
        """Clone `db_to_clone` into DATABASES['default']"""
        # If db_to_clone is a path, assume it is a SQL dump...
        if os.path.isfile(db_to_clone):
            logger.info("Treating %s as a path to a SQL dump", repr(db_to_clone))
            # ...and use it to populate our database
            self.populate_db(db_to_clone)
        # Otherwise, assume it is a database name...
        else:
            logger.info("Treating %s as a database name", repr(db_to_clone))
            # ...create a temp file to dump it into...
            with NamedTemporaryFile(prefix="{}.sql.".format(db_to_clone)) as backup_file:
                # ...perform the dump...
                self.pg_dump(db_to_clone, backup_file.name)
                # ...and load the contents of the dump into our DB
                self.populate_db(backup_file.name)


    def kill_other_psql_sessions(self):
        """Kill any other active sessions on DATABASES['default']"""

        return psql("""
            SELECT procpid, pg_terminate_backend(procpid)
              FROM pg_stat_activity
              WHERE datname = current_database()
                AND procpid <> pg_backend_pid();"""
        )

    def migrate(self, ):
        call_command('migrate')
