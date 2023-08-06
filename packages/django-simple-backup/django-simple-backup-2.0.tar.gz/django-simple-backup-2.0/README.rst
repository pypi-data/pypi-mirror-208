This is a fork of the `django-backup app <https://github.com/chriscohoat/django-backup>`_

This app backs up database and the media directory on the local disk
in a plain directory, without subdirectories.

It does not set a goal of syncing files offsite.
To sync the files or do other post-processing,
please use a signal `backup_ready`
or an independent script.

To list and download the backup files via the web, 
try application `django-directory <https://pypi.python.org/pypi/django-directory/>`_

Installation
============
Add to the `INSTALLED_APPS` entry `'simple_backup',`.

Settings
========
`SIMPLE_BACKUP_DIRECTORY` - directory where the backups will be stored. Default value
is `'backups'`, relative to the current working directory. This setting can be over-ridden
with the option `--output-directory` (or shorter version `-o`)

`SIMPLE_BACKUP_DAYS` - number of days to keep the backup files. Default value is `None`.
If set, older files will be deleted automatically each time the new backup is made.
This walue can be over-ridden with a `--days` option to the command.

.. warning:: 
    To avoid accidental deletion of valuable files when the above setting/option is used,
    make sure that the backup directory contains only backups.

Commands
========
`backup` - backs up the site. See output of `python manage.py backup --help` for more information.

Signals
=======
The command `backup` sends a signal `simple_backups.signals.backup_ready` when
the backup is prepared and copied to the backups directory.
