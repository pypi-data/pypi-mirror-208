"""Signals for the simple_backup app.
`backup_ready` is sent when the backup file is created
by the `backup` management command.
"""
import django.dispatch

backup_ready = django.dispatch.Signal(providing_args=['path',])
