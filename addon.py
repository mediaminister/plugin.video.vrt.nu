# -*- coding: utf-8 -*-

# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' This is the actual VRT Nu video plugin entry point '''

from __future__ import absolute_import, division, unicode_literals
import sys

import xbmcaddon
from resources.lib.kodiwrappers import kodiwrapper
from resources.lib.vrtplayer import actions

try:
    from urllib.parse import parse_qsl
except ImportError:
    from urlparse import parse_qsl

_ADDON_URL = sys.argv[0]
_ADDON_HANDLE = int(sys.argv[1])


def router(params_string):
    ''' This is the main router for the video plugin menu '''
    addon = xbmcaddon.Addon()
    params = dict(parse_qsl(params_string))
    action = params.get('action')

    kodi_wrapper = kodiwrapper.KodiWrapper(_ADDON_HANDLE, _ADDON_URL, addon)
    kodi_wrapper.log_access(_ADDON_URL, params_string)

    if action == actions.CLEAR_COOKIES:
        from resources.lib.vrtplayer import tokenresolver
        token_resolver = tokenresolver.TokenResolver(kodi_wrapper)
        token_resolver.reset_cookies()
        return
    if action == actions.LISTING_TVGUIDE:
        from resources.lib.vrtplayer import tvguide
        tv_guide = tvguide.TVGuide(kodi_wrapper)
        tv_guide.show_tvguide(params)
        return

    from resources.lib.vrtplayer import vrtapihelper, vrtplayer
    api_helper = vrtapihelper.VRTApiHelper(kodi_wrapper)
    vrt_player = vrtplayer.VRTPlayer(kodi_wrapper, api_helper)

    if action == actions.LISTING_AZ_TVSHOWS:
        vrt_player.show_tvshow_menu_items()
    elif action == actions.LISTING_CATEGORIES:
        vrt_player.show_category_menu_items()
    elif action == actions.LISTING_CHANNELS:
        vrt_player.show_channels_menu_items(channel=params.get('channel'))
    elif action == actions.LISTING_LIVE:
        vrt_player.show_livestream_items()
    elif action == actions.LISTING_EPISODES:
        vrt_player.show_episodes(path=params.get('video_url'))
    elif action == actions.LISTING_RECENT:
        vrt_player.show_recent(page=params.get('page', 1))
    elif action == actions.LISTING_CATEGORY_TVSHOWS:
        vrt_player.show_tvshow_menu_items(category=params.get('category'))
    elif action == actions.PLAY:
        vrt_player.play(params)
    else:
        vrt_player.show_main_menu_items()


if __name__ == '__main__':
    router(sys.argv[2][1:])
