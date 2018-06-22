#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Drop the Django DB"""

from __future__ import print_function, unicode_literals

import logging
import subprocess
import sys

from django.core.management.base import BaseCommand

from django_resetdb.util import DB
from django_resetdb.dbops import pg_dump

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Dumps your database to a file"""

    help = "Dumps your database to a file"

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            nargs="?",
            default="./{}.sql".format(DB["NAME"]),
            help="Path to dump the database contents into",
        )

    def handle(self, *args, **options):
        if options["verbosity"] > 1:
            logging.getLogger(__name__.split(".")[0]).setLevel(logging.DEBUG)

        print("Dumping your database '{}' to '{}'".format(DB["NAME"], options["path"]))
        try:
            pg_dump(db_name=DB["NAME"], backup_path=options["path"])
        except subprocess.CalledProcessError as error:
            print("ERROR: {}".format(error), file=sys.stderr)
            sys.exit(1)
