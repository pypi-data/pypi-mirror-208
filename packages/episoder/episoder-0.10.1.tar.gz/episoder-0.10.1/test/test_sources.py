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

from unittest import TestCase

from episoder.sources import TVDB, Epguides, TVCom, parser_for, setup_sources
from episoder.sources import session

class TestSources(TestCase):

    def test_parser_for(self):
        setup_sources('', '')

        parser1 = parser_for('12345')
        self.assertTrue(isinstance(parser1, TVDB))

        parser2 = parser_for('12345')
        self.assertTrue(isinstance(parser2, TVDB))

        self.assertEqual(parser1, parser2)

        parser = parser_for('http://www.epguides.com/test/')
        self.assertTrue(isinstance(parser, Epguides))

        parser = parser_for('http://www.tv.com/test/')
        self.assertTrue(isinstance(parser, TVCom))

        parser = parser_for('http://www.googe.com/')
        self.assertIsNone(parser)

    def test_setup_sources_defines_user_agent(self):
        """ Make sure that the call to 'setup_sources' defines the correct
        user agent for our requests"""

        self.assertNotEqual(session.headers.get('User-Agent'), 'episoder/test')
        setup_sources('episoder/test', '')
        self.assertEqual(session.headers.get('User-Agent'), 'episoder/test')

    def test_setup_sources_sets_tvdb_api_key(self):
        """ Make sure that the call to 'setup_sources' defines the correct
        API key for the tvdb parser"""

        setup_sources('', '')
        parser = parser_for('12345')
        self.assertEqual(parser._api_key, '')

        setup_sources('', 'test-key-000')
        parser = parser_for('12345')
        self.assertEqual(parser._api_key, 'test-key-000')
