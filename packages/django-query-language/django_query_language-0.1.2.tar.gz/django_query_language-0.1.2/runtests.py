#!/usr/bin/env python
import os
import sys
import pytest


def runtests():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    sys.exit(pytest.main())


if __name__ == '__main__':
    runtests()
