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

from datetime import date, datetime
from unittest import TestCase

from episoder.database import Show
from episoder.episoder import Database
from episoder.sources import Epguides

from .util import MockResponse, LoggedRequest


class MockRequestHandler:
    def __init__(self):
        self.requests = []

    def get(self, url, headers={}, timeout=0):
        self.requests.append(LoggedRequest("GET", url, "", headers, ""))

        name = url.split("/").pop()

        if name == "test_iso_8859_1":
            charset = "iso-8859-1"
        else:
            charset = "utf8"

        with open("test/fixtures/epguides_%s.html" % name, "rb") as f:
            data = f.read()

        return MockResponse(data, charset)


class TestEpguides(TestCase):
    def setUp(self):
        self.req = MockRequestHandler()
        self.parser = Epguides(self.req)
        self.db = Database("sqlite://")

    def test_parser_name(self):
        self.assertEqual("epguides.com parser", str(self.parser))
        self.assertEqual("Epguides()", repr(self.parser))

    def test_accept(self):
        self.assertTrue(self.parser.accept("http://www.epguides.com/Lost"))
        self.assertFalse(self.parser.accept("http://epguides2.com/Lost"))
        self.assertFalse(self.parser.accept("http://www.tv.com/Lost"))

    def test_guess_encoding(self):
        res = self.req.get("http://epguides.com/test_iso_8859_1")
        self.assertEqual("iso-8859-1", self.parser._guess_encoding(res))

        res = self.req.get("http://epguides.com/bsg")
        self.assertEqual("utf8", self.parser._guess_encoding(res))

    def test_http_request(self):
        show = self.db.add_show(Show("none", url ="http://epguides.com/lost"))
        self.parser.parse(show, self.db)

        self.assertTrue(len(self.req.requests) > 0)
        req = self.req.requests[-1]

        self.assertEqual(req.url, "http://epguides.com/lost")

    def test_parse(self):
        show = self.db.add_show(Show("none", url="http://epguides.com/lost"))
        self.parser.parse(show, self.db)

        timediff = datetime.now() - show.updated
        self.assertTrue(timediff.total_seconds() < 1)

        self.assertEqual("Lost", show.name)
        self.assertEqual(Show.ENDED, show.status)

        episodes = self.db.get_episodes(date(1996,1,1), 99999)
        self.assertEqual(121, len(episodes))

        ep = episodes[0]
        self.assertEqual("Pilot (1)", ep.title)
        self.assertEqual(1, ep.season)
        self.assertEqual(1, ep.episode)
        self.assertEqual(date(2004, 9, 22), ep.airdate)

        ep = episodes[9]
        self.assertEqual("Raised by Another", ep.title)
        self.assertEqual(1, ep.season)
        self.assertEqual(10, ep.episode)
        self.assertEqual(date(2004, 12, 1), ep.airdate)

        ep = episodes[25]
        self.assertEqual("Man of Science, Man of Faith", ep.title)
        self.assertEqual(2, ep.season)
        self.assertEqual(1, ep.episode)
        self.assertEqual(date(2005, 9, 21), ep.airdate)

        self.db.clear()
        show = self.db.add_show(Show("none", url="http://epguides.com/bsg"))
        self.parser.parse(show, self.db)

        self.assertEqual("Battlestar Galactica (2003)", show.name)
        self.assertEqual(Show.ENDED, show.status)

        episodes = self.db.get_episodes(date(1996,1,1), 99999)
        self.assertEqual(73, len(episodes))

        ep = episodes[0]
        self.assertEqual("33", ep.title)
        self.assertEqual(1, ep.season)
        self.assertEqual(1, ep.episode)
        self.assertEqual(date(2005, 1, 14), ep.airdate)

    def test_format_2(self):
        """ Another format """
        show = self.db.add_show(Show("none", url="http://epguides.com/eureka"))
        self.parser.parse(show, self.db)

        self.assertEqual("Eureka", show.name)
        self.assertEqual(Show.ENDED, show.status)

        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertEqual(76, len(episodes))

        ep = episodes[0]
        self.assertEqual("Pilot", ep.title)
        self.assertEqual(1, ep.season)
        self.assertEqual(1, ep.episode)
        self.assertEqual(date(2006, 7, 18), ep.airdate)

        ep = episodes[9]
        self.assertEqual("Purple Haze", ep.title)
        self.assertEqual(1, ep.season)
        self.assertEqual(10, ep.episode)
        self.assertEqual(date(2006, 9, 19), ep.airdate)

        ep = episodes[27]
        self.assertEqual("Best in Faux", ep.title)
        self.assertEqual(3, ep.season)
        self.assertEqual(3, ep.episode)
        self.assertEqual(date(2008, 8, 12), ep.airdate)

    def test_format_3(self):
        """ Yet another format """
        url = "http://epguides.com/midsomer_murders"
        show = self.db.add_show(Show("none", url=url))
        self.parser.parse(show, self.db)

        self.assertEqual("Midsomer Murders", show.name)
        self.assertEqual(Show.RUNNING, show.status)

        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertEqual(101, len(episodes))

        episode = episodes[0]
        self.assertEqual(1, episode.season)
        self.assertEqual(1, episode.episode)
        self.assertEqual("Written in Blood", episode.title)
        self.assertEqual(date(1998, 3, 22), episode.airdate)

        episode = episodes[5]
        self.assertEqual(2, episode.season)
        self.assertEqual(2, episode.episode)
        self.assertEqual("Strangler's Wood", episode.title)
        self.assertEqual(date(1999, 2, 3), episode.airdate)

    def test_fancy_utf8_chars(self):
        """ This one contains an illegal character somewhere """
        url = "http://epguides.com/american_idol"
        show = self.db.add_show(Show("none", url=url))
        self.parser.parse(show, self.db)

        self.assertEqual("American Idol", show.name)
        self.assertEqual(Show.RUNNING, show.status)

        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertTrue(len(episodes) >= 11)

        episode = episodes[11]
        self.assertEqual("Pride Goeth Before The ‘Fro", episode.title)
        self.assertEqual(1, episode.season)
        self.assertEqual(12, episode.episode)

    def test_missing_season_number(self):
        """ This one lacks a season number somewhere """
        url = "http://epguides.com/48_hours_mistery"
        show = self.db.add_show(Show("none", url=url))
        self.parser.parse(show, self.db)

        self.assertEqual("48 Hours Mystery", show.name)
        self.assertEqual(Show.RUNNING, show.status)

        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertEqual(150, len(episodes))

        episode = episodes[0]
        self.assertEqual(19, episode.season)
        self.assertEqual(1, episode.episode)
        self.assertEqual("January 1988 Debut of 48 Hours",episode.title)
        self.assertEqual(date(1988, 1, 15), episode.airdate)
        self.assertEqual("01-01", episode.prodnum)

    def test_ended_show(self):
        """ This one is no longer on the air """
        url = "http://epguides.com/kr2008"
        show = self.db.add_show(Show("none", url=url))
        self.parser.parse(show, self.db)

        self.assertEqual("Knight Rider (2008)", show.name)
        self.assertEqual(Show.ENDED, show.status)

        episodes = self.db.get_episodes(date(1996,1,1), 99999)
        self.assertEqual(17, len(episodes))

        episode = episodes[3]
        self.assertEqual(1, episode.season)
        self.assertEqual(4, episode.episode)
        self.assertEqual("A Hard Day's Knight", episode.title)
        self.assertEqual(date(2008, 10, 15), episode.airdate)
        self.assertEqual("104", episode.prodnum)

    def test_encoding(self):
        """ This one has funny characters """
        url = "http://epguides.com/buzzcocks"
        show = self.db.add_show(Show("none", url=url))
        self.parser.parse(show, self.db)

        self.assertEqual("Never Mind the Buzzcocks", show.name)
        self.assertEqual(Show.RUNNING, show.status)

        episodes = self.db.get_episodes(date(1996,1,1), 99999)
        self.assertTrue(len(episodes) >= 21)
        episode = episodes[20]
        self.assertEqual(3, episode.season)
        self.assertEqual(4, episode.episode)
        title = "Zoë Ball, Louis Eliot, Graham Norton, Keith Duffy"
        self.assertEqual(title, episode.title)
        self.assertEqual(date(1998, 3, 20), episode.airdate)

    def test_with_anchor(self):
        """ This one has an anchor tag before the bullet for season 6 """
        url = "http://epguides.com/futurama"
        show = self.db.add_show(Show("none", url=url))
        self.parser.parse(show, self.db)

        self.assertEqual("Futurama", show.name)
        self.assertEqual(Show.ENDED, show.status)

        episodes = self.db.get_episodes(date(1996,1,1), 99999)
        self.assertEqual(124, len(episodes))

        episode = episodes.pop()
        self.assertEqual(7, episode.season)
        self.assertEqual(26, episode.episode)
        self.assertEqual("Meanwhile", episode.title)
        self.assertEqual(date(2013, 9, 4), episode.airdate)

    def test_with_trailer_and_recap(self):
        """ This one has [Trailer] and [Recap] in episode titles """
        url = "http://epguides.com/house"
        show = self.db.add_show(Show("none", url=url))
        self.parser.parse(show, self.db)

        self.assertEqual("House, M.D.", show.name)
        self.assertEqual(Show.ENDED, show.status)

        episodes = self.db.get_episodes(date(1996,1,1), 99999)
        self.assertEqual(176, len(episodes))

        episode = episodes[-3]
        self.assertEqual(8, episode.season)
        self.assertEqual(20, episode.episode)
        self.assertEqual("Post Mortem", episode.title)
        self.assertEqual(date(2012, 5, 7), episode.airdate)

        episode = episodes[-2]
        self.assertEqual("Holding On", episode.title)

    def test_encoding_iso8859_1(self):
        """ Explicitly test ISO 8859-1 encoding """
        url = "http://epguides.com/test_iso_8859_1"
        show = self.db.add_show(Show("none", url=url))
        self.parser.parse(show, self.db)

        self.assertEqual("Episoder ISO-8859-1 Tëst", show.name)

        episodes = self.db.get_episodes(date(1996,1,1), 99999)
        self.assertEqual(len(episodes), 1)

        episode = episodes[0]
        self.assertEqual("äöü", episode.title)

    def test_html_format_ended_with_missing_date(self):
        url = "http://epguides.com/lost_html"
        show = self.db.add_show(Show("none", url=url))
        self.parser.parse(show, self.db)

        timediff = datetime.now() - show.updated
        self.assertTrue(timediff.total_seconds() < 1)

        self.assertEqual("Lost", show.name)
        self.assertEqual(Show.ENDED, show.status)

        episodes = self.db.get_episodes(date(1996,1,1), 99999)
        self.assertEqual(127, len(episodes))

        ep = episodes[0]
        self.assertEqual("Pilot (1)", ep.title)
        self.assertEqual(1, ep.season)
        self.assertEqual(1, ep.episode)
        self.assertEqual(date(2004, 9, 22), ep.airdate)

        ep = episodes[9]
        self.assertEqual("Raised by Another", ep.title)
        self.assertEqual(1, ep.season)
        self.assertEqual(10, ep.episode)
        self.assertEqual(date(2004, 12, 1), ep.airdate)

        ep = episodes[26]
        self.assertEqual("Man of Science, Man of Faith", ep.title)
        self.assertEqual(2, ep.season)
        self.assertEqual(1, ep.episode)
        self.assertEqual(date(2005, 9, 21), ep.airdate)

        ep = episodes[-1]
        self.assertEqual("The Final Journey", ep.title)
        self.assertEqual(6, ep.season)
        self.assertEqual(0, ep.episode)
        self.assertEqual(date(2010, 5, 23), ep.airdate)

    def test_html_format(self):
        """ Yet another format """
        url = "http://epguides.com/lower_decks"
        show = self.db.add_show(Show("none", url=url))
        self.parser.parse(show, self.db)

        self.assertEqual("Star Trek: Lower Decks", show.name)
        self.assertEqual(Show.RUNNING, show.status)

        episodes = self.db.get_episodes(date(1988,1,1), 99999)
        self.assertEqual(11, len(episodes))

        episode = episodes[0]
        self.assertEqual(1, episode.season)
        self.assertEqual(1, episode.episode)
        self.assertEqual("Second Contact", episode.title)
        self.assertEqual(date(2020, 8, 6), episode.airdate)

        episode = episodes[1]
        self.assertEqual(1, episode.season)
        self.assertEqual(2, episode.episode)
        self.assertEqual("Envoys", episode.title)
        self.assertEqual(date(2020, 8, 13), episode.airdate)

        episode = episodes[5]
        self.assertEqual(1, episode.season)
        self.assertEqual(0, episode.episode)
        self.assertEqual("Star Trek Day 2020: Lower Decks Panel", episode.title)
        self.assertEqual(date(2020, 9, 8), episode.airdate)

        episode = episodes[10]
        self.assertEqual(1, episode.season)
        self.assertEqual(10, episode.episode)
        self.assertEqual("No Small Parts", episode.title)
        self.assertEqual(date(2020, 10, 8), episode.airdate)

    def test_empty_episode_lines_in_html_shows(self):
        """ This page has some epinfo table cells that should contain
        episode data but don't"""

        url = "http://epguides.com/doctor_who"
        show = self.db.add_show(Show("none", url=url))
        self.parser.parse(show, self.db)

        self.assertEqual("Doctor Who (2005)", show.name)
        self.assertEqual(Show.RUNNING, show.status)

        episodes = self.db.get_episodes(date(2005,3,26), 99999)
        self.assertEqual(161, len(episodes))

        episode = episodes[0]
        self.assertEqual(1, episode.season)
        self.assertEqual(1, episode.episode)
        self.assertEqual("Rose", episode.title)
        self.assertEqual(date(2005, 3, 26), episode.airdate)

        episode = episodes[12]
        self.assertEqual(1, episode.season)
        self.assertEqual(13, episode.episode)
        self.assertEqual("The Parting of the Ways", episode.title)
        self.assertEqual(date(2005, 6, 18), episode.airdate)

        episode = episodes[13]
        self.assertEqual(1, episode.season)
        self.assertEqual(0, episode.episode)
        self.assertEqual("Born Again", episode.title)
        self.assertEqual(date(2005, 11, 18), episode.airdate)

        episode = episodes[14]
        self.assertEqual(2, episode.season)
        self.assertEqual(0, episode.episode)
        # both are acceptable
        self.assertIn(episode.title, ["The Christmas Invasion",
                "Attack of the Graske"])
        self.assertEqual(date(2005, 12, 25), episode.airdate)

        episode = episodes[15]
        self.assertEqual(2, episode.season)
        self.assertEqual(1, episode.episode)
        self.assertEqual("New Earth", episode.title)
        self.assertEqual(date(2006, 4, 15), episode.airdate)

    def test_cancelled_show(self):
        """ This page shows a show that has been cancelled """

        url = 'http://epguides.com/picard'
        show = self.db.add_show(Show(u'none', url=url))
        self.parser.parse(show, self.db)

        self.assertEqual('Star Trek: Picard', show.name)
        self.assertEqual(Show.ENDED, show.status)
