# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
from apihelper import ApiHelper
from favorites import Favorites
from resumepoints import ResumePoints

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcgui = __import__('xbmcgui')
xbmcplugin = __import__('xbmcplugin')
xbmcvfs = __import__('xbmcvfs')

addon = xbmcaddon.Addon()
addon.settings['useresumepoints'] = 'true'


class TestResumePoints(unittest.TestCase):

    _favorites = Favorites()
    _resumepoints = ResumePoints()
    _apihelper = ApiHelper(_favorites, _resumepoints)

    @unittest.skipUnless(addon.settings.get('username'), 'Skipping as VRT username is missing.')
    @unittest.skipUnless(addon.settings.get('password'), 'Skipping as VRT password is missing.')
    def test_get_watchlater_episodes(self):
        ''' Test items, sort and order '''
        episode_items, sort, ascending, content = self._apihelper.list_episodes(page=1, variety='watchlater')
        self.assertTrue(episode_items)
        self.assertEqual(sort, 'dateadded')
        self.assertFalse(ascending)
        self.assertEqual(content, 'episodes')

    @unittest.skipUnless(addon.settings.get('username'), 'Skipping as VRT username is missing.')
    @unittest.skipUnless(addon.settings.get('password'), 'Skipping as VRT password is missing.')
    def test_get_continue_episodes(self):
        ''' Test items, sort and order '''
        episode_items, sort, ascending, content = self._apihelper.list_episodes(page=1, variety='continue')
        self.assertTrue(episode_items)
        self.assertEqual(sort, 'dateadded')
        self.assertFalse(ascending)
        self.assertEqual(content, 'episodes')

    @unittest.skipUnless(addon.settings.get('username'), 'Skipping as VRT username is missing.')
    @unittest.skipUnless(addon.settings.get('password'), 'Skipping as VRT password is missing.')
    def test_update_watchlist(self):
        self._resumepoints.refresh(ttl=0)
        assetuuid, first_entry = next(iter(self._resumepoints._resumepoints.items()))  # pylint: disable=protected-access
        print('%s = %s' % (assetuuid, first_entry))
        url = first_entry.get('value').get('url')
        self._resumepoints.watchlater(uuid=assetuuid, title='Foo bar', url=url)
        self._resumepoints.unwatchlater(uuid=assetuuid, title='Foo bar', url=url)
        self._resumepoints.refresh(ttl=0)
        assetuuid, first_entry = next(iter(self._resumepoints._resumepoints.items()))  # pylint: disable=protected-access
        print('%s = %s' % (assetuuid, first_entry))

    def test_assetpath_to_uuid(self):
        self.assertEqual(None, self._resumepoints.assetpath_to_uuid(None))

        assetpath = '/content/dam/vrt/2019/08/14/woodstock-depot_WP00157456'
        uuid = 'contentdamvrt20190814woodstockdepotwp00157456'
        self.assertEqual(uuid, self._resumepoints.assetpath_to_uuid(assetpath))


if __name__ == '__main__':
    unittest.main()
