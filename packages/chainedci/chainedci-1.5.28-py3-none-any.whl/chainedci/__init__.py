#!/usr/bin/env python3
"""Chained CI engine."""


from chainedci.config import init_ini, getConfig
from chainedci.log import init_log, log
from chainedci.version import __version__

init_ini()
init_log(getConfig('ini'))
log.info("---- ChainedCI v%s initialization -----", __version__)
