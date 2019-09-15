# -*- coding: utf-8 -*-
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime, timedelta
import unittest
import dateutil.tz
import addon


xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcgui = __import__('xbmcgui')
xbmcplugin = __import__('xbmcplugin')
xbmcvfs = __import__('xbmcvfs')

plugin = addon.plugin
now = datetime.now(dateutil.tz.tzlocal())
lastweek = now + timedelta(days=-7)


class TestRouter(unittest.TestCase):

    def test_main_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/', '0', ''])
        self.assertEqual(plugin.url_for(addon.main_menu), 'plugin://plugin.video.vrt.nu/')

    # Favorites menu: '/favorites'
    def test_favorites(self):
        plugin.run(['plugin://plugin.video.vrt.nu/favorites', '0', ''])
        plugin.run(['plugin://plugin.video.vrt.nu/favorites/programs', '0', ''])
        plugin.run(['plugin://plugin.video.vrt.nu/favorites/recent', '0', ''])
        plugin.run(['plugin://plugin.video.vrt.nu/favorites/recent/2', '0', ''])
        self.assertEqual(plugin.url_for(addon.favorites_recent, page=2), 'plugin://plugin.video.vrt.nu/favorites/recent/2')
        plugin.run(['plugin://plugin.video.vrt.nu/favorites/offline', '0', ''])
        plugin.run(['plugin://plugin.video.vrt.nu/favorites/docu', '0', ''])

    # A-Z menu: '/programs'
    def test_az_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/programs', '0', ''])
        self.assertEqual(plugin.url_for(addon.programs), 'plugin://plugin.video.vrt.nu/programs')

    # Episodes menu: '/programs/<program>'
    def test_episodes_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/programs/thuis', '0', ''])
        self.assertEqual(plugin.url_for(addon.programs, program='thuis'), 'plugin://plugin.video.vrt.nu/programs/thuis')
        plugin.run(['plugin://plugin.video.vrt.nu/programs/de-campus-cup', '0', ''])
        self.assertEqual(plugin.url_for(addon.programs, program='de-campus-cup'), 'plugin://plugin.video.vrt.nu/programs/de-campus-cup')

    # Categories menu: '/categories'
    def test_categories_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/categories', '0', ''])
        self.assertEqual(plugin.url_for(addon.categories), 'plugin://plugin.video.vrt.nu/categories')

    # Categories programs menu: '/categories/<category>'
    def test_categories_tvshow_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/categories/docu', '0', ''])
        self.assertEqual(plugin.url_for(addon.categories, category='docu'), 'plugin://plugin.video.vrt.nu/categories/docu')
        plugin.run(['plugin://plugin.video.vrt.nu/categories/voor-kinderen', '0', ''])
        self.assertEqual(plugin.url_for(addon.categories, category='voor-kinderen'), 'plugin://plugin.video.vrt.nu/categories/voor-kinderen')

    # Featured menu: '/featured'
    def test_featured_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/featured', '0', ''])
        self.assertEqual(plugin.url_for(addon.featured), 'plugin://plugin.video.vrt.nu/featured')

    # Featured programs menu: '/featured/<cfeatured>'
    def test_featured_tvshow_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/featured/kortfilm', '0', ''])
        self.assertEqual(plugin.url_for(addon.featured, feature='kortfilm'), 'plugin://plugin.video.vrt.nu/featured/kortfilm')

    # Channels menu = '/channels/<channel>'
    def test_channels_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/channels', '0', ''])
        self.assertEqual(plugin.url_for(addon.channels), 'plugin://plugin.video.vrt.nu/channels')
        plugin.run(['plugin://plugin.video.vrt.nu/channels/ketnet', '0', ''])
        self.assertEqual(plugin.url_for(addon.channels, channel='ketnet'), 'plugin://plugin.video.vrt.nu/channels/ketnet')

    # Live TV menu: '/livetv'
    def test_livetv_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/livetv', '0', ''])
        self.assertEqual(plugin.url_for(addon.livetv), 'plugin://plugin.video.vrt.nu/livetv')

    # Most recent menu: '/recent/<page>'
    def test_recent_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/recent', '0', ''])
        self.assertEqual(plugin.url_for(addon.recent), 'plugin://plugin.video.vrt.nu/recent')
        plugin.run(['plugin://plugin.video.vrt.nu/recent/2', '0', ''])
        self.assertEqual(plugin.url_for(addon.recent, page=2), 'plugin://plugin.video.vrt.nu/recent/2')

    # Soon offline menu: '/offline/<page>'
    def test_offline_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/offline', '0', ''])
        self.assertEqual(plugin.url_for(addon.offline), 'plugin://plugin.video.vrt.nu/offline')

    # TV guide menu: '/tvguide/<date>/<channel>'
    def test_tvguide_date_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/tvguide', '0', ''])
        self.assertEqual(plugin.url_for(addon.tvguide), 'plugin://plugin.video.vrt.nu/tvguide/date')
        plugin.run(['plugin://plugin.video.vrt.nu/tvguide/date/today', '0', ''])
        self.assertEqual(plugin.url_for(addon.tvguide, date='today'), 'plugin://plugin.video.vrt.nu/tvguide/date/today')
        plugin.run(['plugin://plugin.video.vrt.nu/tvguide/date/today/canvas', '0', ''])
        self.assertEqual(plugin.url_for(addon.tvguide, date='today', channel='canvas'), 'plugin://plugin.video.vrt.nu/tvguide/date/today/canvas')
        plugin.run(['plugin://plugin.video.vrt.nu/tvguide/channel/canvas', '0', ''])
        self.assertEqual(plugin.url_for(addon.tvguide_channel, channel='canvas'), 'plugin://plugin.video.vrt.nu/tvguide/channel/canvas')
        plugin.run(['plugin://plugin.video.vrt.nu/tvguide/channel/canvas/today', '0', ''])
        self.assertEqual(plugin.url_for(addon.tvguide_channel, channel='canvas', date='today'), 'plugin://plugin.video.vrt.nu/tvguide/channel/canvas/today')

    # Clear search history: '/search/clear'
    # Add search keyword: '/search/add/<keywords>'
    # Remove search keyword: '/search/remove/<keywords>'
    def test_search_history(self):
        plugin.run(['plugin://plugin.video.vrt.nu/search/add/foobar', '0', ''])
        self.assertEqual(plugin.url_for(addon.add_search, keywords='foobar'), 'plugin://plugin.video.vrt.nu/search/add/foobar')
        plugin.run(['plugin://plugin.video.vrt.nu/search/add/foobar', '0', ''])
        self.assertEqual(plugin.url_for(addon.add_search, keywords='foobar'), 'plugin://plugin.video.vrt.nu/search/add/foobar')
        plugin.run(['plugin://plugin.video.vrt.nu/search/query/foobar', '0', ''])
        self.assertEqual(plugin.url_for(addon.add_search, keywords='foobar'), 'plugin://plugin.video.vrt.nu/search/add/foobar')
        plugin.run(['plugin://plugin.video.vrt.nu/search/remove/foobar', '0', ''])
        self.assertEqual(plugin.url_for(addon.remove_search, keywords='foobar'), 'plugin://plugin.video.vrt.nu/search/remove/foobar')
        plugin.run(['plugin://plugin.video.vrt.nu/search/remove/foobar', '0', ''])
        self.assertEqual(plugin.url_for(addon.remove_search, keywords='foobar'), 'plugin://plugin.video.vrt.nu/search/remove/foobar')
        plugin.run(['plugin://plugin.video.vrt.nu/search/clear', '0', ''])
        self.assertEqual(plugin.url_for(addon.clear_search), 'plugin://plugin.video.vrt.nu/search/clear')
        plugin.run(['plugin://plugin.video.vrt.nu/search', '0', ''])
        self.assertEqual(plugin.url_for(addon.search), 'plugin://plugin.video.vrt.nu/search')
        plugin.run(['plugin://plugin.video.vrt.nu/search/add/foobar', '0', ''])
        self.assertEqual(plugin.url_for(addon.add_search, keywords='foobar'), 'plugin://plugin.video.vrt.nu/search/add/foobar')

    # Search VRT NU menu: '/search/query/<keywords>/<page>'
    def test_search_menu(self):
        plugin.run(['plugin://plugin.video.vrt.nu/search', '0', ''])
        self.assertEqual(plugin.url_for(addon.search), 'plugin://plugin.video.vrt.nu/search')
        plugin.run(['plugin://plugin.video.vrt.nu/search/query', '0', ''])
        self.assertEqual(plugin.url_for(addon.search_query), 'plugin://plugin.video.vrt.nu/search/query')
        plugin.run(['plugin://plugin.video.vrt.nu/search/query/dag', '0', ''])
        self.assertEqual(plugin.url_for(addon.search_query, keywords='dag'), 'plugin://plugin.video.vrt.nu/search/query/dag')
        plugin.run(['plugin://plugin.video.vrt.nu/search/query/dag/2', '0', ''])
        self.assertEqual(plugin.url_for(addon.search_query, keywords='dag', page=2), 'plugin://plugin.video.vrt.nu/search/query/dag/2')
        plugin.run(['plugin://plugin.video.vrt.nu/search/query/winter', '0', ''])
        self.assertEqual(plugin.url_for(addon.search_query, keywords='winter'), 'plugin://plugin.video.vrt.nu/search/query/winter')

    # Follow method: '/follow/<program>/<title>'
    def test_follow_route(self):
        plugin.run(['plugin://plugin.video.vrt.nu/follow/thuis/Thuis', '0', ''])
        self.assertEqual(plugin.url_for(addon.follow, program='thuis', title='Thuis'), 'plugin://plugin.video.vrt.nu/follow/thuis/Thuis')

    # Unfollow method: '/unfollow/<program>/<title>'
    def test_unfollow_route(self):
        plugin.run(['plugin://plugin.video.vrt.nu/unfollow/thuis/Thuis', '0', ''])
        self.assertEqual(plugin.url_for(addon.unfollow, program='thuis', title='Thuis'), 'plugin://plugin.video.vrt.nu/unfollow/thuis/Thuis')

    # Delete tokens method: '/tokens/delete'
    def test_clear_cookies_route(self):
        plugin.run(['plugin://plugin.video.vrt.nu/tokens/delete', '0', ''])
        self.assertEqual(plugin.url_for(addon.delete_tokens), 'plugin://plugin.video.vrt.nu/tokens/delete')

    # Delete cache method: '/cache/delete'
    def test_invalidate_caches_route(self):
        plugin.run(['plugin://plugin.video.vrt.nu/cache/delete', '0', ''])
        self.assertEqual(plugin.url_for(addon.delete_cache), 'plugin://plugin.video.vrt.nu/cache/delete')

    # Refresh favorites method: '/favorites/refresh'
    def test_refresh_favorites_route(self):
        plugin.run(['plugin://plugin.video.vrt.nu/favorites/refresh', '0', ''])
        self.assertEqual(plugin.url_for(addon.favorites_refresh), 'plugin://plugin.video.vrt.nu/favorites/refresh')

    # Play on demand by id = '/play/id/<publication_id>/<video_id>'
    # Achterflap episode 8 available until 31/12/2025
    def test_play_on_demand_by_id_route(self):
        plugin.run(['plugin://plugin.video.vrt.nu/play/id/vid-f80fa527-6759-45a7-908d-ec6f0a7b164e/pbs-pub-1a170972-dea3-4ea3-8c27-62d2442ee8a3', '0', ''])
        self.assertEqual(plugin.url_for(addon.play_id,
                                        video_id='vid-f80fa527-6759-45a7-908d-ec6f0a7b164e',
                                        publication_id='pbs-pub-1a170972-dea3-4ea3-8c27-62d2442ee8a3'),
                         'plugin://plugin.video.vrt.nu/play/id/vid-f80fa527-6759-45a7-908d-ec6f0a7b164e/pbs-pub-1a170972-dea3-4ea3-8c27-62d2442ee8a3')

    # Play livestream by id = '/play/id/<video_id>'
    # Canvas livestream
    def test_play_livestream_by_id_route(self):
        plugin.run(['plugin://plugin.video.vrt.nu/play/id/vualto_canvas_geo', '0', ''])
        self.assertEqual(plugin.url_for(addon.play_id, video_id='vualto_canvas_geo'), 'plugin://plugin.video.vrt.nu/play/id/vualto_canvas_geo')

    # Play on demand by url = '/play/url/<vrtnuwebsite_url>'
    # Achterflap episode 8 available until 31/12/2025
    def test_play_on_demand_by_url_route(self):
        plugin.run(['plugin://plugin.video.vrt.nu/play/url/https://www.vrt.be/vrtnu/a-z/achterflap/1/achterflap-s1a8/', '0', ''])
        self.assertEqual(plugin.url_for(addon.play_url,
                                        video_url='https://www.vrt.be/vrtnu/a-z/achterflap/1/achterflap-s1a8/'),
                         'plugin://plugin.video.vrt.nu/play/url/https://www.vrt.be/vrtnu/a-z/achterflap/1/achterflap-s1a8/')

    # Play livestream by url = '/play/url/<vrtnuwebsite_url>'
    # Canvas livestream
    def test_play_livestream_by_url_route(self):
        plugin.run(['plugin://plugin.video.vrt.nu/play/url/https://www.vrt.be/vrtnu/kanalen/canvas/', '0', ''])
        self.assertEqual(plugin.url_for(addon.play_url,
                                        video_url='https://www.vrt.be/vrtnu/kanalen/canvas/'),
                         'plugin://plugin.video.vrt.nu/play/url/https://www.vrt.be/vrtnu/kanalen/canvas/')

    # Play last episode method = '/play/lastepisode/<program>'
    def test_play_latestepisode_route(self):
        plugin.run(['plugin://plugin.video.vrt.nu/play/latest/het-journaal', '0', ''])
        self.assertEqual(plugin.url_for(addon.play_latest, program='het-journaal'), 'plugin://plugin.video.vrt.nu/play/latest/het-journaal')
        plugin.run(['plugin://plugin.video.vrt.nu/play/latest/terzake', '0', ''])
        self.assertEqual(plugin.url_for(addon.play_latest, program='terzake'), 'plugin://plugin.video.vrt.nu/play/latest/terzake')
        plugin.run(['plugin://plugin.video.vrt.nu/play/latest/winteruur', '0', ''])
        self.assertEqual(plugin.url_for(addon.play_latest, program='winteruur'), 'plugin://plugin.video.vrt.nu/play/latest/winteruur')

    # Play episode by air date method = '/play/airdate/<channel>/<start_date>'
    def test_play_airdateepisode_route(self):
        # Test Het Journaal
        plugin.run([lastweek.strftime('plugin://plugin.video.vrt.nu/play/airdate/een/%Y-%m-%dT19:00:00'), '0', ''])
        self.assertEqual(plugin.url_for(addon.play_by_air_date,
                                        channel='een',
                                        start_date=lastweek.strftime('%Y-%m-%dT19:00:00')),
                         lastweek.strftime('plugin://plugin.video.vrt.nu/play/airdate/een/%Y-%m-%dT19:00:00'))
        # Test TerZake
        plugin.run([lastweek.strftime('plugin://plugin.video.vrt.nu/play/airdate/canvas/%Y-%m-%dT20:00:00'), '0', ''])
        self.assertEqual(plugin.url_for(addon.play_by_air_date,
                                        channel='canvas',
                                        start_date=lastweek.strftime('%Y-%m-%dT20:00:00')),
                         lastweek.strftime('plugin://plugin.video.vrt.nu/play/airdate/canvas/%Y-%m-%dT20:00:00'))


if __name__ == '__main__':
    unittest.main()
