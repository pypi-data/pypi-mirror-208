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

from abc import ABC, abstractmethod
from json import dumps
from logging import getLogger
from datetime import datetime, date
from typing import Dict, List, Tuple

from requests import Session

from episoder.database import Episode, Show
from episoder.episoder import Database
from .parser import Parser


class TVDBState(ABC):
    @abstractmethod
    def login(self, key: str) -> None:
        """Authenticate to the backend"""

    @abstractmethod
    def lookup(self, text: str) -> List[Show]:
        """Find show(s) by name"""

    @abstractmethod
    def parse(self, show: Show, db: Database) -> None:
        """Load episodes with this parser"""


class InvalidLoginError(Exception):
    pass


class TVDBShowNotFoundError(Exception):
    pass


class TVDBNotLoggedInError(Exception):
    pass


class TVDB(Parser):
    """Parser for episodes from thetvdb.com"""

    def __init__(self, session: Session, api_key: str) -> None:
        self._session = session
        self._api_key = api_key
        self._state: TVDBState = TVDBOffline(self, session)

    def __str__(self) -> str:
        return str(self._state)

    def __repr__(self) -> str:
        return f'TVDB {repr(self._state)}'

    def lookup(self, text: str) -> List[Show]:
        self._state.login(self._api_key)
        return self._state.lookup(text)

    def parse(self, show: Show, db: Database) -> None:
        self._state.login(self._api_key)
        self._state.parse(show, db)

    def change(self, state: TVDBState) -> None:
        self._state = state

    def accept(self, url: str) -> bool:
        return url.isdigit()


class TVDBOffline(TVDBState):
    def __init__(self, tvdb: TVDB, session: Session) -> None:
        self._tvdb = tvdb
        self._log = getLogger('TVDB (offline)')
        self._session = session

    def __str__(self) -> str:
        return 'thetvdb.com parser (ready)'

    def __repr__(self) -> str:
        return '<TVDBOffline>'

    def _post_login(self, data: Dict[str, str]) -> str:
        url = 'https://api.thetvdb.com/login'
        head = {'Content-type': 'application/json'}
        body = dumps(data).encode('utf8')
        response = self._session.post(url, body, headers=head, timeout=10)
        data = response.json()

        if response.status_code == 401:
            raise InvalidLoginError(data.get('Error'))

        self._log.info('Successful login')
        return data['token']

    def lookup(self, _: str) -> List[Show]:
        raise TVDBNotLoggedInError()

    def login(self, key: str) -> None:
        body = {'apikey': key}
        token = self._post_login(body)
        self._tvdb.change(TVDBOnline(token, self._session))

    def parse(self, _: Show, __: Database) -> None:
        raise TVDBNotLoggedInError()


class TVDBOnline(TVDBState):
    def __init__(self, token: str, session: Session) -> None:
        self._token = token
        self._log = getLogger('TVDB (online)')
        self._session = session

    def __str__(self) -> str:
        return 'thetvdb.com parser (authorized)'

    def __repr__(self) -> str:
        return '<TVDBOnline>'

    def _get(self, url: str, params: Dict) -> Dict:
        url = f'https://api.thetvdb.com/{url}'
        head = {'Content-type': 'application/json',
                'Authorization': f'Bearer {self._token}'}

        response = self._session.get(url, headers=head, params=params,
                                     timeout=10)
        data = response.json()

        if response.status_code == 404:
            raise TVDBShowNotFoundError(data.get('Error'))

        return data

    def _get_episodes(self, show: Show,
                      page: int) -> Tuple[List[Episode], Dict]:
        show_id = int(show.url)
        opts = {'page': page}
        result = self._get(f'series/{ show_id }/episodes', opts)
        return (result.get('data') or [], result.get('links', {}))

    def lookup(self, text: str) -> List[Show]:
        def mkshow(entry: Dict) -> Show:
            name = entry.get('seriesName')
            url = str(entry.get('id')).encode('utf8').decode('utf8')
            return Show(name, url=url)

        matches = self._get('search/series', {'name': text})
        return list(map(mkshow, matches.get('data', {})))

    def login(self, _: str) -> None:
        pass

    def _fetch_episodes(self, show: Show, page: int) -> List[Episode]:
        def airdate(row: Dict) -> date:
            aired = row.get('firstAired', '1970-01-01')

            if aired == '0000-00-00':
                return datetime(1970, 1, 1)

            return datetime.strptime(aired, '%Y-%m-%d').date()

        def mkepisode(row: Dict) -> Episode:
            num = int(row.get("airedEpisodeNumber", "0") or 0)
            name = row.get('episodeName') or 'Unnamed episode'
            season = int(row.get('airedSeason', '0') or 0)
            aired = airdate(row)
            pnum = 'UNK'

            self._log.debug('Found episode %s', name)
            return Episode(name, season, num, aired, pnum, 0)

        def is_valid(row: Dict) -> bool:
            return row.get("firstAired") not in [None, ""]

        (data, links) = self._get_episodes(show, page)
        valid = filter(is_valid, data)
        episodes = [mkepisode(row) for row in valid]

        # handle pagination
        next_ = links.get("next") or 0
        if next_ > page:
            try:
                more = self._fetch_episodes(show, next_)
                episodes.extend(more)
            except TVDBShowNotFoundError:
                msg = "Error parsing %s: failed to load page %d"
                self._log.error(msg, show.name, next_)

        return episodes

    def parse(self, show: Show, db: Database) -> None:
        result = self._get(f'series/{ int(show.url) }', {})
        data = result.get('data', {})

        # update show data
        show.name = data.get('seriesName', show.name)
        show.updated = datetime.now()

        self._log.debug("Updating show '%s'", show.name)

        if data.get('status') == 'Continuing':
            show.status = Show.RUNNING
        else:
            show.status = Show.ENDED

        # load episodes
        try:
            episodes = self._fetch_episodes(show, 1)
        except TVDBShowNotFoundError:
            return

        for (idx, episode) in enumerate(sorted(episodes)):
            episode.totalnum = idx + 1
            db.add_episode(episode, show)

        db.commit()
