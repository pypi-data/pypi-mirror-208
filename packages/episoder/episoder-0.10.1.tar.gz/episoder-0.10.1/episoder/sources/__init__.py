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

from typing import Optional, List
import requests

from .epguides import Epguides
from .thetvdb import TVDB
from .tvcom import TVCom
from .parser import Parser

session = requests.Session()

PARSERS: List[Parser] = []


def setup_sources(user_agent: str, tvdb_api_key: str) -> None:
    session.headers.update({'User-Agent': user_agent})

    while len(PARSERS) > 0:
        PARSERS.pop()

    PARSERS.append(TVDB(session, tvdb_api_key))
    PARSERS.append(Epguides(session))
    PARSERS.append(TVCom())


def parser_for(url: str) -> Optional[Parser]:
    """Find the right parser for the given URL"""
    for parser in PARSERS:
        if parser.accept(url):
            return parser
    return None
