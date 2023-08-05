"""Intercept requests to ensure that HTTPS is reported correctly.

"""

from __future__ import unicode_literals

from .urllib3 import intercept_urllib3


def intercept_requests(profiler, mod):
    # requests ships with its own version of urllib3, so we need to manually intercept it.
    intercept_urllib3(profiler, mod.packages.urllib3)
