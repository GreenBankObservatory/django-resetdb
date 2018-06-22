#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Drop the Django DB"""

from __future__ import print_function, unicode_literals

import logging
import subprocess
import sys

from django.core.management.base import BaseCommand

from django_resetdb.util import DB
from django_resetdb.resetdb import dropdb

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Drops your database"""

    help = "Drops your database"

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Forcibly close other DB sessions to allow it to be dropped",
        )

    def handle(self, *args, **options):
        if options["verbosity"] > 1:
            logger.setLevel(logging.DEBUG)

        print("Dropping your database {!r}".format(DB["NAME"]))
        try:
            dropdb(force=options["force"])
        except subprocess.CalledProcessError as error:
            print("ERROR: {}".format(error), file=sys.stderr)
            sys.exit(1)
