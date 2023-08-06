# episoder, https://code.ott.net/episoder
# -*- coding: utf8 -*-
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

from datetime import date, datetime
from json import loads
from unittest import TestCase

from episoder.database import Show
from episoder.episoder import Database
from episoder.sources.thetvdb import TVDB
from episoder.sources.thetvdb import InvalidLoginError, TVDBShowNotFoundError

from .util import MockResponse, LoggedRequest


class MockRequestHandler:

    def __init__(self):
        self.requests = []

    def load_fixture(self, name):
        with open("test/fixtures/tvdb_%s.json" % name, "rb") as file:
            data = file.read()

        return data

    def fixture(self, name, code):
        response = self.load_fixture(name)
        return MockResponse(response, "utf8", code)

    def get_search(self, url, headers, params):
        term = params.get("name")

        if term == "Frasier":
            return self.fixture("search_frasier", 200)
        elif term == "Friends":
            return self.fixture("search_friends", 200)

        return self.fixture("error_404", 404)

    def get_episodes(self, url, headers, params):
        id = int(url.split("/")[-2])
        p = params.get("page", 1)

        try:
            return self.fixture("test_show_%d_%d_eps" % (id,p), 200)
        except IOError:
            return self.fixture("error_404", 404)

    def get_show(self, url, headers, params):
        id = int(url.split("/")[-1])

        try:
            return self.fixture("test_show_%d" % id, 200)
        except IOError:
            return self.fixture("error_404", 404)

    def get(self, url, headers={}, params={}, timeout=0):
        req = LoggedRequest("GET", url, "", headers, params)
        self.requests.append(req)

        if url.startswith("https://api.thetvdb.com/search/series"):
            return self.get_search(url, headers, params)
        elif url.startswith("https://api.thetvdb.com/series"):
            if url.endswith("/episodes"):
                return self.get_episodes(url, headers, params)
            else:
                return self.get_show(url, headers, params)

        return MockResponse("{}", "utf8", 404)

    def post_login(self, body, headers):
        data = loads(body)
        key = data.get("apikey")

        if key == "fake-api-key":
            text = '{ "token": "fake-token" }'
            return MockResponse(text.encode("utf8"), "utf8", 200)

        text = '{"Error": "Not Authorized"}'
        return MockResponse(text.encode("utf8"), "utf8", 401)

    def post(self, url, body, headers = {}, timeout=0):
        req = LoggedRequest("POST", url, body, headers, {})
        self.requests.append(req)

        if url.startswith("https://api.thetvdb.com/login"):
            return self.post_login(body.decode("utf8"), headers)

        return MockResponse("{}", "utf8", 404)


class TestTVDB(TestCase):

    def setUp(self):
        logging.disable(logging.ERROR)

        self.db = Database("sqlite://")
        self.req = MockRequestHandler()
        self.tvdb = TVDB(self.req, 'fake-api-key')

    def test_auto_login_on_lookup(self):
        self.assertEqual("thetvdb.com parser (ready)", str(self.tvdb))
        self.assertEqual("TVDB <TVDBOffline>", repr(self.tvdb))

        self.tvdb.lookup("Frasier")
        self.assertEqual("thetvdb.com parser (authorized)", str(self.tvdb))
        self.assertEqual("TVDB <TVDBOnline>", repr(self.tvdb))

    def test_auto_login_on_parse(self):
        self.assertEqual("thetvdb.com parser (ready)", str(self.tvdb))
        self.assertEqual("TVDB <TVDBOffline>", repr(self.tvdb))

        show = self.db.add_show(Show("unnamed show", url="73739"))
        self.tvdb.parse(show, self.db)

        self.assertEqual("thetvdb.com parser (authorized)", str(self.tvdb))
        self.assertEqual("TVDB <TVDBOnline>", repr(self.tvdb))

    def test_login(self):
        self.tvdb.lookup("Frasier")

        reqs = len(self.req.requests)
        self.assertTrue(reqs > 0)

        req = self.req.requests[0]
        self.assertEqual(req.url, "https://api.thetvdb.com/login")
        self.assertEqual(req.method, "POST")
        self.assertEqual(req.body.decode("utf8"),
                        '{"apikey": "fake-api-key"}')
        headers = req.headers
        self.assertEqual(headers.get("Content-type"),"application/json")

    def test_login_failure(self):
        tvdb = TVDB(self.req, 'wrong-api-key')

        with self.assertRaises(InvalidLoginError):
            tvdb.lookup("Frasier")

        with self.assertRaises(InvalidLoginError):
            tvdb.lookup("Frasier")

    def test_search_no_hit(self):
        with self.assertRaises(TVDBShowNotFoundError):
            self.tvdb.lookup("NoSuchShow")

    def test_search_single(self):
        shows = list(self.tvdb.lookup("Frasier"))

        req = self.req.requests[-1]
        self.assertEqual(req.url, "https://api.thetvdb.com/search/series")
        self.assertEqual(req.params, {"name": "Frasier"})
        self.assertEqual(req.method, "GET")
        self.assertEqual(req.body, "")

        content_type = req.headers.get("Content-type")
        self.assertEqual(content_type, "application/json")

        auth = req.headers.get("Authorization")
        self.assertEqual(auth, "Bearer fake-token")

        self.assertEqual(len(shows), 1)
        self.assertEqual(shows[0].name, "Frasier")
        self.assertEqual(shows[0].url, "77811")

    def test_search_multiple(self):
        shows = list(self.tvdb.lookup("Friends"))

        self.assertEqual(len(shows), 3)
        self.assertEqual(shows[0].name, "Friends")
        self.assertEqual(shows[1].name, "Friends (1979)")
        self.assertEqual(shows[2].name, "Friends of Green Valley")

    def test_accept_url(self):
        self.assertTrue(self.tvdb.accept("123"))
        self.assertFalse(self.tvdb.accept("http://www.epguides.com/test"))

    def test_encoding_utf8(self):
        show = self.db.add_show(Show("unnamed show", url="73739"))
        self.assertTrue(self.tvdb.accept(show.url))

        self.tvdb.parse(show, self.db)

        self.assertEqual("Lost", show.name)
        self.assertEqual(Show.ENDED, show.status)

        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertEqual(len(episodes), 1)

        episode = episodes[0]
        self.assertEqual(episode.title, "Exposé")

    def test_null_values(self):
        show = self.db.add_show(Show("unnamed show", url="268156"))
        self.assertTrue(self.tvdb.accept(show.url))

        # this show has some null values that can confuse the parser
        self.tvdb.parse(show, self.db)
        self.assertEqual("Sense8", show.name)

    def test_parse(self):
        show = self.db.add_show(Show("unnamed show", url="260"))
        self.tvdb.parse(show, self.db)

        req = self.req.requests[-2]
        self.assertEqual(req.url, "https://api.thetvdb.com/series/260")
        self.assertEqual(req.params, {})
        self.assertEqual(req.method, "GET")
        self.assertEqual(req.body, "")

        content_type = req.headers.get("Content-type")
        self.assertEqual(content_type, "application/json")

        auth = req.headers.get("Authorization")
        self.assertEqual(auth, "Bearer fake-token")

        req = self.req.requests[-1]
        self.assertEqual(req.url,
                "https://api.thetvdb.com/series/260/episodes")
        self.assertEqual(req.params, {"page": 1})
        self.assertEqual(req.method, "GET")
        self.assertEqual(req.body, "")

        content_type = req.headers.get("Content-type")
        self.assertEqual(content_type, "application/json")

        auth = req.headers.get("Authorization")
        self.assertEqual(auth, "Bearer fake-token")

        self.assertEqual(show.name, "test show")
        self.assertEqual(show.status, Show.RUNNING)

        timediff = datetime.now() - show.updated
        self.assertTrue(timediff.total_seconds() < 1)

        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertEqual(len(episodes), 2)

        episode = episodes[0]
        self.assertEqual(episode.title, "Unnamed episode")
        self.assertEqual(episode.season, 0)
        self.assertEqual(episode.episode, 0)
        self.assertEqual(episode.airdate, date(1990, 1, 18))
        self.assertEqual(episode.prodnum, "UNK")
        self.assertEqual(episode.totalnum, 1)

        episode = episodes[1]
        self.assertEqual(episode.title, "The Good Son")
        self.assertEqual(episode.season, 1)
        self.assertEqual(episode.episode, 1)
        self.assertEqual(episode.airdate, date(1993, 9, 16))
        self.assertEqual(episode.totalnum, 2)

    def test_parse_paginated(self):
        show = self.db.add_show(Show("unnamed show", url="261"))

        self.tvdb.parse(show, self.db)

        self.assertEqual(show.status, Show.ENDED)
        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertEqual(len(episodes), 8)

        episode = episodes[0]
        self.assertEqual(episode.title, "First")

        episode = episodes[1]
        self.assertEqual(episode.title, "Second")

        episode = episodes[2]
        self.assertEqual(episode.title, "Third")

        episode = episodes[3]
        self.assertEqual(episode.title, "Fourth")

        episode = episodes[4]
        self.assertEqual(episode.title, "Fifth")

        episode = episodes[5]
        self.assertEqual(episode.title, "Sixth")

        episode = episodes[6]
        self.assertEqual(episode.title, "Seventh")

        episode = episodes[7]
        self.assertEqual(episode.title, "Eighth")

    def test_parse_invalid_show(self):
        show = self.db.add_show(Show("test show", url="293"))

        with self.assertRaises(TVDBShowNotFoundError):
            self.tvdb.parse(show, None)

    def test_parse_show_with_invalid_data(self):
        show = self.db.add_show(Show("unnamed show", url="262"))

        self.tvdb.parse(show, self.db)
        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertEqual(len(episodes), 2)

    def test_parse_show_without_episodes(self):
        show = self.db.add_show(Show("unnamed show", url="263"))

        self.tvdb.parse(show, self.db)

        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertEqual(len(episodes), 0)

    def test_parse_show_with_data_0000_00_00(self):
        show = self.db.add_show(Show("unnamed show", url="75397"))

        self.tvdb.parse(show, self.db)
        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertEqual(len(episodes), 1)

    def test_parse_show_without_data(self):
        """ page 2 of this show's list of episodes has no data """
        show = self.db.add_show(Show("unnamed show", url="295640"))

        self.tvdb.parse(show, self.db)
        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertTrue(len(episodes) > 0)
