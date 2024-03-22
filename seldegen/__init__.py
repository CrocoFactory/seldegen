"""
seldegen
~~~~~~~~~~~~~~
The package for interacting with socials directed to web3-based projects.
Author github - https://github.com/blnkoff

Note that not every social can be authorized or connected. At the moment, in such case as invalid credentials,
authentication by phone number the package fails to cope.

If you will use BrowserExtension-based classes, you need to know about extension IDs.

Most of the extension have different extension IDs, depending on the browser you use. Default IDs of
built-in extensions are provided for using in Chrome.

For more information about extension IDs go to BrowserExtension documentation

:copyright: (c) 2023 by Alexey
:license: MIT, see LICENSE for more details.
"""

from .abc import *
from .dapps import *
from .context import *
from .captcha_solver import *
from .extensions import *
from .email import *
from .socials import *
from .wallets import *
