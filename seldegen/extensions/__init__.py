"""
This subpackage contains classes interacting with browser extensions.

Most of the extension have different extension IDs, depending on the browser you use. Default IDs of
built-in extensions are provided for using in AdsPower. Even though AdsPower's SunBrowser is Chrome-based,
it has different extension IDs from Google Chrome. If you don't use AdsPower API to get and interact with its
driver, you need to change the ID of specific extension on your own.

For more information about extension IDs go to BrowserExtension documentation

:copyright: (c) 2023 by Alexey
:license: Apache 2.0, see LICENSE for more details.
"""

from .authenticator import Authenticator
from .capmonster import Capmonster
