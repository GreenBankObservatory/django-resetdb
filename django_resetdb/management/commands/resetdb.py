#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Reset the Django DB"""

from __future__ import print_function, unicode_literals

import logging
import subprocess
import sys

from django.core.management.base import BaseCommand
from django.core.management import call_command

from django_resetdb.util import DB
from django_resetdb.resetdb import cleardb, clone_psql_db

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Resets your database"""

    help = "Resets your database"

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--clone",
            metavar="NAME_OR_PATH",
            help="Either the name of a database to clone or a SQL dump to load"
            "into your database",
        )
        parser.add_argument(
            "-M",
            "--no-migrate",
            action="store_true",
            help="Don't apply migrations after resetting the DB",
        )
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Forcibly close other DB sessions to allow it to be dropped",
        )

    def handle(self, *args, **options):
        if options["verbosity"] > 1:
            logger.setLevel(logging.DEBUG)

        print("Resetting your database {!r}".format(DB["NAME"]))
        try:
            cleardb(force=options["force"])
        except (subprocess.CalledProcessError, ValueError) as error:
            print(error, file=sys.stderr)
            sys.exit(1)

        if options["clone"]:
            print(
                "Loading {!r} into your database {!r}".format(
                    options["clone"], DB["NAME"]
                )
            )
            try:
                clone_psql_db(options["clone"])
            except (subprocess.CalledProcessError, ValueError) as error:
                print("ERROR: {}".format(error), file=sys.stderr)
                sys.exit(1)

        if not options["no_migrate"]:
            print("Applying migrations")
            call_command("migrate")
