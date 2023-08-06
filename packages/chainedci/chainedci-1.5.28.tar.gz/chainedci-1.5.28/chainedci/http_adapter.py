# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0

"""HTTP adapter for chained py.

some simple functions used in the different classes
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, NoReturn

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry  import Retry

from chainedci.log import log

def generate_default_max_replies():
    """Generate the default max replies."""
    return Http.default_max_retries


def generate_default_backoff():
    """Generate the defaukt backoff."""
    return Http.default_backoff


@dataclass
class Http():
    """
    Http Class.

    This class is intended to configure requests with timeouts and retries.

    :param max_retries: the max retries number. Will be set to
        Http.default_max_retries if not given.
    :param backoff: the backoff factor. Will be set to Http.default_timeout if
        not given.
    :param session: the session with a right retry strategy configured

    :type max_retries: int
    :type backoff: int
    :type session: :class:`Session`

    The backoff factors allows you to change how long the processes will sleep
    between failed requests. The algorithm is as follows:

    {backoff factor} * (2 ** ({number of total retries} - 1))

    For example, if the backoff factor is set to:

    * 1 second the successive sleeps will be 0.5, 1, 2, 4, 8, 16, 32, 64, 128,
        256.
    * 2 seconds - 1, 2, 4, 8, 16, 32, 64, 128, 256, 512
    * 10 seconds - 5, 10, 20, 40, 80, 160, 320, 640, 1280, 2560

    :see also:
        https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html

    """

    # noqa: RST304 Unknown interpreted text role "class".
    default_max_retries: ClassVar[int] = 10 # pylint: disable=E1136
    default_backoff: ClassVar[int] = 1 # pylint: disable=E1136
    max_retries: int = field(default_factory=generate_default_max_replies)
    backoff: int = field(default_factory=generate_default_backoff)
    session: Session = field(init=False)

    def __post_init__(self) -> NoReturn:
        """Postinitialize the Http class.

        During, the postinitialization, the retry strategy is configured and
        create a session with this retry strategy.
        """
        log.debug(
            'will use %s retries and a backoff factore of %s seconds',
            self.max_retries,
            self.backoff,
        )
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff,
            status_forcelist=[401, 413, 429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        # this is post init in order to create the session
        self.session = Session()  # noqa: WPS601 Found shadowed class attribute
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
