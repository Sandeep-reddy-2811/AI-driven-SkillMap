#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    # This line tells Python to look for modules inside the backend folder
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and "
            "your virtual environment is activated."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()