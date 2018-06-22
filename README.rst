``django-resetdb``
==================

Developer-friendly database resets for Django.

.. NOTE:: This currently only works for PostgreSQL backends!

.. WARNING:: This has not been tested at all outside of the GBO computing environment. It *should* be generally useful, but proceed with caution...


Motivation
----------

You’re developing a Django project and you need to investigate a problem
in production. So, you need to clone the production database and take a
look at it.

In the olden days, this was a very manual process. You would try to find
a wiki page, forget where it is, try to remember the commands you needed
to do, probably forget some minor detail, and, eventually, you would get
your database clone.

Instead, you can now run a single command to either reset your database
to a blank state or clone another database (production or otherwise).

Installation
------------

Via internal PyPI
~~~~~~~~~~~~~~~~~

First you’ll need to make sure that your ``pip`` has knowledge of our
internal PyPI repository. Then simply:

::

    $ pip install django-resetdb

Manual Installation
~~~~~~~~~~~~~~~~~~~

::

    $ git clone https://github.com/GreenBankObservatory/django-resetdb
    $ ./django-resetdb/setup.py install

Configuration
-------------

Two settings will need to be configured before use:

1. Add ``django_resetdb`` to your ``INSTALLED_APPS``
   (``./manage.py help`` should now list ``django-resetdb``)
2. Add ``django_resetdb`` to your ``LOGGING``, if you want to access its
   verbose modes (optional)

Usage
-----

Reset to blank database
~~~~~~~~~~~~~~~~~~~~~~~

In its most basic form, ``resetdb`` will simply reset your database to a
blank state and apply migrations:

::

    $ ./manage.py resetdb

Reset to a database clone
~~~~~~~~~~~~~~~~~~~~~~~~~

This allows you to reset your database to a clone of another. You also
have the option of avoiding migrations at the end (we need this for DSS
currently, I think):

If you want to clone a database, you could simply provide the database
name you wish to clone:

::

    $ ./manage.py resetdb --clone DB_NAME --no-migrate

If there is an existing database backup you wish to reset to, you can
use that instead:

::

    $ ./manage.py resetdb --clone DB_DUMP_PATH --no-migrate

Drop database
~~~~~~~~~~~~~

Drop your default database:

::

    $ ./manage.py dropdb --force

Create database
~~~~~~~~~~~~~~~

Create your default database:

::

    $ ./manage.py createdb

Dump database
~~~~~~~~~~~~~

Dump your default database to a file:

::

    $ ./manage.py dumpdb PATH_TO_DUMP
