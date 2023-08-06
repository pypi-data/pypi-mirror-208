# episoder, https://code.ott.net/episoder
#
# Copyright (C) 2004-2023 Stefan Ott. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from re import match

from episoder.database import Show
from episoder.episoder import Database
from .parser import Parser


class TVCom(Parser):
    """Parser for episodes from tv.com"""

    def __init__(self) -> None:
        self._log = logging.getLogger('TVCom')

    def __str__(self) -> str:
        return 'dummy tv.com parser to detect old urls'

    def __repr__(self) -> str:
        return 'TVCom()'

    def accept(self, url: str) -> bool:
        exp = 'http://(www.)?tv.com/.*'
        return match(exp, url) is not None

    def parse(self, show: Show, _: Database) -> None:
        self._log.error("The url %s is no longer supported", show.url)
