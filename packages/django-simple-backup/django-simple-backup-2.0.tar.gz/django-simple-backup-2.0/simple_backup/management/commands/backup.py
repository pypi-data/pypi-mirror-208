"""`backup` management command.
Backs up the database and media files.
"""
import os
import shutil
import time
import tempfile
from datetime import datetime

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.conf import settings
from django.contrib.sites.models import Site
from simple_backup.signals import backup_ready

def maybe_print(text, verbosity):
    """Prints to stdout if verbosity is True"""
    if verbosity:
        print(text)

def delete_old_backup_files(directory, days):
    """Deletes files in the directory older than `days` days"""
    file_names = os.listdir(directory)
    today = datetime.now()
    for name in file_names:
        file_path = os.path.join(directory, name)
        #won't delete a directory or non- .tar.gz files
        if name.endswith('.tar.gz') and os.path.isfile(file_path):
            stat = os.stat(os.path.join(directory, name))
            delta = today - datetime.fromtimestamp(stat.st_ctime)
            if delta.days > days:
                os.remove(file_path)

def get_backup_name():
    """Returns a name for the backup file
    using the current site name and the current date and time.
    Defaults to 'django_YYYYMMDD-HHMMSS'
    """
    if 'sites' in settings.INSTALLED_APPS:
        site_name = Site.objects.get_current().name
    else:
        site_name = 'django'
    return site_name + '_' + time.strftime('%Y%m%d-%H%M%S')

def get_safe_dirname(sourcedir):
    """Returns a safe name for the directory to be backed up.
    Works for Unix and hopefully Windows.
    """
    if not os.path.isabs(sourcedir):
        sourcedir = os.path.abspath(sourcedir)
    drive, dirname = os.path.splitdrive(sourcedir)
    dirname = dirname.replace(os.path.sep, '_')
    if drive:
        dirname = drive.strip(':') + '_' + dirname
    return dirname

def get_database_parameters():
    """Returns a list of tuples (name, params) with the parameters
    for each database in the settings."""
    params = []
    for name in settings.DATABASES.keys():
        params_for_name = {
            'engine': settings.DATABASES[name]['ENGINE'],
            'name': settings.DATABASES[name]['NAME'],
            'user': settings.DATABASES[name]['USER'],
            'password': settings.DATABASES[name]['PASSWORD'],
            'host': settings.DATABASES[name]['HOST'],
            'port': settings.DATABASES[name]['PORT']
        }
        params.append((name, params_for_name))
    return params

def backup_sqlite(params, outfile):
    """Backs up a sqlite database by copying the file"""
    os.system(f'cp {params["name"]} {outfile}')

def backup_mysql(params, outfile):
    """Backs up a mysql database using mysqldump"""
    args = ''
    user = params['user']
    password = params['password']
    host = params['host']
    port = params['port']
    if user:
        args += f"--user={user} "
    if password:
        args += f"--password={password} "
    if host:
        args += f"--host={host} "
    if port:
        args += f"--port={port} "
    args += params['name']
    os.system(f'mysqldump {args} > {outfile}')

def backup_postgresql(params, outfile):
    """Backs up a postgresql database using pg_dump"""
    args = ''
    user = params['user']
    password = params['password']
    host = params['host']
    port = params['port']
    if user:
        args += f"--username={user} "
    if host:
        args += f"--host={user} "
    if port:
        args += f"--port={port} "
    args += params['name']

    if password:
        command = f'PGPASSWORD={password} pg_dump {args} > {outfile}'
    else:
        command = f'pg_dump {args} -w > {outfile}'
    os.system(command)

def backup_database(params, outfile, verbosity):
    """Backs up a database of any supported engine"""
    engine = params['engine']
    name = params['name']
    if 'mysql' in engine:
        maybe_print(f'Backing up Mysql database {name}', verbosity)
        backup_mysql(params, outfile)
    elif engine in ('postgresql_psycopg2', 'postgresql') or 'postgresql' in engine:
        maybe_print(f'Backing up Postgresql database {name}', verbosity)
        backup_postgresql(params, outfile)
    elif 'sqlite3' in engine:
        maybe_print(f'Backing up Postgresql database {name}', verbosity)
        backup_sqlite(params, outfile)
    else:
        raise CommandError(f'Backup for the database {engine} engine not implemented')

def backup_databases(collect_dir, verbosity):
    """Backs up all the databases in the settings"""
    database_params = get_database_parameters()
    for name, params in database_params:
        outfile = os.path.join(collect_dir, name + '.sql')
        backup_database(params, outfile, verbosity)

def backup_media(collect_dir, verbosity):
    """Backs up the uploaded media files"""
    maybe_print(f"Backing up uploaded files from {settings.MEDIA_ROOT}", verbosity)
    #copy the uploaded media to the temp directory
    dest_dir = os.path.join(collect_dir, os.path.basename(settings.MEDIA_ROOT))
    shutil.copytree(settings.MEDIA_ROOT, dest_dir)

def backup_directories(collect_dir, directories, verbosity):
    """Backs up extra directories specified in `settings.SIMPLE_BACKUP_DIRECTORIES`"""
    comments = []
    for directory in directories:
        maybe_print(f"Backing up directory {directory}", verbosity)
        destdir = get_safe_dirname(directory)
        shutil.copytree(directory, os.path.join(collect_dir, destdir))
        comments.append(f'Directory {directory} copied to {destdir}')
    #write comments if there are any
    if comments:
        comments_file_path = os.path.join(collect_dir, 'README.txt')
        with open(comments_file_path, 'w', encoding='utf-8') as readme_file:
            readme_file.write('\n'.join(comments))

def clean_days_option(days):
    """Returns the number of days to keep backups"""
    try:
        return int(days)
    except ValueError as exc:
        if days:
            raise CommandError('value of --days must be an integer') from exc
        error_msg = 'value of SIMPLE_BACKUP_DAYS must be an Integer'
        raise ImproperlyConfigured(error_msg) from exc

# Based on: http://code.google.com/p/django-backup/
# Based on: http://www.djangosnippets.org/snippets/823/
# Based on: http://www.yashh.com/blog/2008/sep/05/django-database-backup-view/
class Command(BaseCommand):
    """`backup` management command"""
    help = "Backup database. Mysql, Postgresql and Sqlite engines are supported"

    def add_arguments(self, parser: CommandParser) -> None:
        """Adds arguments to the command
        * --directory
        * --without-media
        * --without-db
        """
        parser.add_argument('--directory', '-d', action='append', default=[], dest='directories',
            help='Extra directories to back up')
        parser.add_argument('--without-media', '-u', action='store_true', default=False,
            dest='without_media', help='Do not backup the media directory')
        parser.add_argument('--without-db', '-b', action='store_true', default=False,
            dest='without_db', help='Do not back up database')

    def handle(self, *args, **options):
        temp_dir = tempfile.mkdtemp()
        backup_name = get_backup_name()
        #collect all files into this directory
        collect_dir = os.path.join(temp_dir, backup_name)
        os.makedirs(collect_dir)

        #Backup documents?
        if not options['without_media']:
            backup_media(collect_dir, options['verbosity'])

        # Doing backup
        if not options['without_db']:
            backup_databases(collect_dir, options['verbosity'])

        #backing up extra directoris
        backup_directories(collect_dir, options['directories'], options['verbosity'])

        #compress backup
        maybe_print('Compressing backup file', options['verbosity'])
        outfile = os.path.join(temp_dir, backup_name + '.tar.gz')
        os.system(f'cd {temp_dir} && tar -czf {outfile} {backup_name}')

        #move file to the final location
        backups_dir = getattr(settings, 'SIMPLE_BACKUP_DIRECTORY', 'backups')
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)

        shutil.move(outfile, backups_dir)
        shutil.rmtree(temp_dir)

        days = options.get('days', getattr(settings, 'SIMPLE_BACKUP_DAYS', None))
        if days:
            days = clean_days_option(days)
            delete_old_backup_files(backups_dir, days)

        backup_file = os.path.join(backups_dir, os.path.basename(outfile))
        backup_ready.send(None, path=backup_file)
