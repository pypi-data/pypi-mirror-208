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

from datetime import datetime, date
from logging import getLogger
from re import search
from typing import Optional

from bs4 import BeautifulSoup, element
from requests import Response, Session

from episoder.database import Episode, Show
from episoder.episoder import Database
from .parser import Parser


class Epguides(Parser):
    """Parser for episodes from epguides.com"""

    def __init__(self, session: Session) -> None:
        self._logger = getLogger('Epguides')
        self._session = session

    def __str__(self) -> str:
        return 'epguides.com parser'

    def __repr__(self) -> str:
        return 'Epguides()'

    def accept(self, url: str) -> bool:
        return 'epguides.com/' in url

    def _guess_encoding(self, response: Response) -> str:
        raw = response.raw.read()
        text = raw.decode('iso-8859-1')

        if 'charset=iso-8859-1' in text:
            return 'iso-8859-1'

        return 'utf8'

    def parse(self, show: Show, db: Database) -> None:
        response = self._session.get(show.url, timeout=10)
        response.encoding = self._guess_encoding(response)

        for line in response.text.split('\n'):
            self._parse_line(line, show, db)

        show.updated = datetime.now()
        db.commit()

    def _html_episode_title(self, soup: BeautifulSoup) -> str:
        cell = soup.find('td', class_='eptitle')
        if isinstance(cell, element.Tag):
            link = cell.find('a')
            if isinstance(link, element.Tag):
                return link.text.strip()
        return ''

    def _update_show_title(self, show: Show, line: str) -> None:
        # Name of the show
        res = search(r'<title>(.*)</title>', line)
        if res:
            title = res.groups()[0]
            show.name = title.split(' (a ')[0]

    def _update_show_status(self, show: Show, line: str) -> None:
        # Current status (running / ended)
        res = search(r'<span class="status">(.*)</span>', line)
        if res:
            text = res.groups()[0]
            if 'current' in text:
                show.status = Show.RUNNING
            else:
                show.status = Show.ENDED
        elif search(r'aired.*to.*[\d+]', line):
            show.status = Show.ENDED

        # Current status in new HTML version
        res = search(r'Status: (.*)<br', line)
        if res:
            text = res.groups()[0]
            if 'ended' in text:
                show.status = Show.ENDED
            else:
                show.status = Show.RUNNING

    def _get_date(self, val: str) -> date:
        day = val.replace('/', ' ')
        then = datetime.strptime(day, '%d %b %y')
        return then.date()

    def _load_html_episode(self, line: str) -> Optional[Episode]:
        soup = BeautifulSoup(line, 'html.parser')
        cells = soup.find_all('td', class_='epinfo')

        # We expect 3 cells, otherwise we refuse to go on
        if len(cells) < 3:
            return None

        # total episode number
        total_episodes = cells[0].text.split('.', 1)[0]
        try:
            total = int(total_episodes)
        except ValueError:
            # Some shows have specials (numbered separately)
            total = -1

        # season and episode number
        details = cells[1].text.split('-')
        if len(details) < 2:
            return None

        [season, epnum] = details

        # episode title
        title = self._html_episode_title(soup)

        # original air date
        day = cells[2].text
        if not day:
            # Drop episodes without date
            return None

        then = self._get_date(day)

        # prodnum is None, we don't have those
        return Episode(title, season, epnum, then, None, total)

    def _load_text_episode(self, line: str) -> Optional[Episode]:
        # Known formatting supported by this fine regex:
        # 4.     1-4        19 Jun 02  <a [..]>title</a>
        #   1.  19- 1   01-01    5 Jan 88  <a [..]>title</a>
        # 23     3-05       27/Mar/98  <a [..]>title</a>
        # 65.   17-10       23 Apr 05  <a [..]>title</a>
        # 101.   5-15       09 May 09  <a [..]>title</a>
        # 254.    - 5  05-254   15 Jan 92  <a [..]>title</a>
        res = search(r'^ *(\d+)\.? +(\d*)- ?(\d+) +([a-zA-Z0-9-]*)'
                     r' +(\d{1,2}[ /][A-Z][a-z]{2}[ /]\d{2}) *<a.*>(.*)</a>',
                     line)

        if not res:
            return None

        (total, season, epnum, prodnum, day, title) = res.groups()
        then = self._get_date(day)
        return Episode(title, season or 0, epnum, then, prodnum, total)

    def _parse_line(self, line: str, show: Show, db: Database) -> None:
        self._update_show_title(show, line)
        self._update_show_status(show, line)

        if search(r'<td class=.epinfo', line):
            episode = self._load_html_episode(line)
        else:
            episode = self._load_text_episode(line)

        if episode:
            self._logger.debug('Found episode %s', episode.title)
            db.add_episode(episode, show)
