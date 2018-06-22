"""Utility functions for django_resetdb"""

from __future__ import print_function, unicode_literals

import logging
import subprocess

from django.conf import settings

logger = logging.getLogger(__name__)


DB = settings.DATABASES["default"]


def shell(cmd, **kwargs):
    """Execute cmd, check exit code, return stdout"""
    logger.debug("$ %s", cmd)
    return subprocess.check_output(cmd, shell=True, **kwargs)


def psql(sql, **kwargs):
    """Shortcut to execute `psql`"""
    # TODO: How to handle admin user generically?
    return shell(
        'psql -U "{USER}" -h "{HOST}" -d "{NAME}" -c "{sql}"'.format(sql=sql, **DB),
        **kwargs
    )


def kill_other_psql_sessions():
    """Kill any other active sessions on DATABASES['default']"""

    return psql(
        """
        SELECT procpid, pg_terminate_backend(procpid)
          FROM pg_stat_activity
          WHERE datname = current_database()
            AND procpid <> pg_backend_pid();
    """
    )
