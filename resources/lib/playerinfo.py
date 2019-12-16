# -*- coding: utf-8 -*-
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Implementation of PlayerInfo class"""

from __future__ import absolute_import, division, unicode_literals
from threading import Event, Thread
from xbmc import getInfoLabel, Player, PlayList

from apihelper import ApiHelper
from data import SECONDS_MARGIN
from favorites import Favorites
from kodiutils import addon_id, container_reload, get_advanced_setting_int, get_setting, has_addon, log, notify
from resumepoints import ResumePoints
from utils import assetpath_to_id, play_url_to_id, to_unicode, url_to_episode


class PlayerInfo(Player, object):  # pylint: disable=useless-object-inheritance
    """Class for communication with Kodi player"""

    def __init__(self):
        """PlayerInfo initialisation"""
        self.resumepoints = ResumePoints()
        self.apihelper = ApiHelper(Favorites(), self.resumepoints)
        self.last_pos = None
        self.listen = False
        self.paused = False
        self.total = None
        self.positionthread = None
        self.quit = Event()

        self.asset_id = None
        self.path = None
        self.title = None
        self.ep_id = None
        self.url = None
        self.whatson_id = None
        from random import randint
        self.thread_id = randint(1, 10001)
        log(3, '[PlayerInfo %d] Initialized' % self.thread_id)
        super(PlayerInfo, self).__init__(self)

    def onPlayBackStarted(self):  # pylint: disable=invalid-name
        """Called when user starts playing a file"""
        self.path = getInfoLabel('Player.Filenameandpath')
        if self.path.startswith('plugin://plugin.video.vrt.nu/'):
            self.listen = True
        else:
            self.listen = False
            return

        log(3, '[PlayerInfo %d] Event onPlayBackStarted' % self.thread_id)

        # Get asset_id, title and url from api
        ep_id = play_url_to_id(self.path)

        # Get episode data
        episode = self.apihelper.get_single_episode_data(video_id=ep_id.get('video_id'), whatson_id=ep_id.get('whatson_id'), video_url=ep_id.get('video_url'))

        # This may be a live stream?
        if episode is None:
            return

        self.asset_id = assetpath_to_id(episode.get('assetPath'))
        self.title = episode.get('program')
        self.url = url_to_episode(episode.get('url', ''))
        self.ep_id = 'S%sE%s' % (episode.get('seasonTitle'), episode.get('episodeNumber'))
        self.whatson_id = episode.get('whatsonId') if episode.get('whatsonId') else None

    def onAVStarted(self):  # pylint: disable=invalid-name
        """Called when Kodi has a video or audiostream"""
        if not self.listen:
            return
        log(3, '[PlayerInfo %d] Event onAVStarted' % self.thread_id)
        self.quit.clear()
        self.update_position()
        self.update_total()
        self.push_position()
        self.push_upnext()

        # StreamPosition thread keeps running when watching multiple episode with "Up Next"
        # only start StreamPosition thread when it doesn't exist yet.
        if not self.positionthread:
            self.positionthread = Thread(target=self.stream_position, name='StreamPosition')
            self.positionthread.start()

    def onAVChange(self):  # pylint: disable=invalid-name
        """Called when Kodi has a video, audio or subtitle stream. Also happens when the stream changes."""

    def onPlayBackSeek(self, time, seekOffset):  # pylint: disable=invalid-name
        """Called when user seeks to a time"""
        if not self.listen:
            return
        log(3, '[PlayerInfo %d] Event onPlayBackSeek time=%d offset=%d' % (self.thread_id, time, seekOffset))
        self.last_pos = time // 1000

        # If we seek beyond the end, quit Player
        if self.last_pos >= self.total:
            self.quit.set()
            self.stop()

    def onPlayBackPaused(self):  # pylint: disable=invalid-name
        """Called when user pauses a playing file"""
        if not self.listen:
            return
        log(3, '[PlayerInfo %d] Event onPlayBackPaused' % self.thread_id)
        self.update_position()
        self.push_position(position=self.last_pos, total=self.total)
        self.paused = True

    def onPlayBackResumed(self):  # pylint: disable=invalid-name
        """Called when user resumes a paused file or a next playlist item is started"""
        if not self.listen:
            return
        suffix = 'after pausing' if self.paused else 'after playlist change'
        log(3, '[PlayerInfo %d] Event onPlayBackResumed %s' % (self.thread_id, suffix))
        if not self.paused:
            self.push_position(position=self.last_pos, total=self.total)
        self.paused = False

    def onPlayBackEnded(self):  # pylint: disable=invalid-name
        """Called when Kodi has ended playing a file"""
        if not self.listen:
            return
        self.quit.set()
        log(3, '[PlayerInfo %d] Event onPlayBackEnded' % self.thread_id)
        self.last_pos = self.total

    def onPlayBackError(self):  # pylint: disable=invalid-name
        """Called when playback stops due to an error"""
        if not self.listen:
            return
        self.quit.set()
        log(3, '[PlayerInfo %d] Event onPlayBackError' % self.thread_id)

    def onPlayBackStopped(self):  # pylint: disable=invalid-name
        """Called when user stops Kodi playing a file"""
        if not self.listen:
            return
        self.quit.set()
        log(3, '[PlayerInfo %d] Event onPlayBackStopped' % self.thread_id)

    def onThreadExit(self):  # pylint: disable=invalid-name
        """Called when player stops, before the player exited, so before the menu refresh"""
        log(3, '[PlayerInfo %d] Event onThreadExit' % self.thread_id)
        self.positionthread = None
        self.push_position(position=self.last_pos, total=self.total)

    def stream_position(self):
        """Get latest stream position while playing"""
        while self.isPlaying() and not self.quit.is_set():
            self.update_position()
            if self.quit.wait(timeout=0.2):
                break
        self.onThreadExit()

    def add_upnext(self, video_id):
        """Add Up Next url to Kodi Player"""
        url = 'plugin://plugin.video.vrt.nu/play/upnext/%s' % video_id
        self.update_position()
        self.update_total()
        if self.isPlaying() and self.total - self.last_pos < 1:
            log(3, '[PlayerInfo] %d Add %s to Kodi Playlist' % (self.thread_id, url))
            PlayList(1).add(url)
        else:
            log(3, '[PlayerInfo] %d Add %s to Kodi Player' % (self.thread_id, url))
            self.play(url)

    def push_upnext(self):
        """Push episode info to Up Next service add-on"""
        if has_addon('service.upnext') and get_setting('useupnext', 'true') == 'true' and self.isPlaying():
            info_tag = self.getVideoInfoTag()
            next_info = self.apihelper.get_upnext(dict(
                program=to_unicode(info_tag.getTVShowTitle()),
                playcount=info_tag.getPlayCount(),
                rating=info_tag.getRating(),
                path=self.path,
                runtime=self.total,
            ))
            if next_info:
                from base64 import b64encode
                from json import dumps
                data = [to_unicode(b64encode(dumps(next_info).encode()))]
                sender = '%s.SIGNAL' % addon_id()
                notify(sender=sender, message='upnext_data', data=data)

    def update_position(self):
        """Update the player position, when possible"""
        try:
            self.last_pos = self.getTime()
        except RuntimeError:
            pass

    def update_total(self):
        """Update the total video time"""
        try:
            total = self.getTotalTime()
            # Kodi Player sometimes returns a total time of 0.0 and this causes unwanted behaviour with VRT NU Resumepoints API.
            if total > 0.0:
                self.total = total
        except RuntimeError:
            pass

    def push_position(self, position=0, total=100):
        """Push player position to VRT NU resumepoints API"""
        # Not all content has an asset_id
        if not self.asset_id:
            return

        # Push resumepoint to VRT NU
        self.resumepoints.update(
            asset_id=self.asset_id,
            title=self.title,
            url=self.url,
            position=position,
            total=total,
            whatson_id=self.whatson_id,
            asynchronous=True
        )

        # Kodi internal watch status is only updated when the play action is initiated from the GUI, so this doesn't work after quitting "Up Next"
        if (not self.path.startswith('plugin://plugin.video.vrt.nu/play/upnext')
                and not self.overrule_kodi_watchstatus(position, total)):
            return

        # Do not reload container when playing or not stopped
        if self.isPlaying() or not self.quit.is_set():
            return

        container_reload()

    @staticmethod
    def overrule_kodi_watchstatus(position, total):
        """Determine if we need to overrule the Kodi watch status"""

        # Kodi uses different resumepoint margins than VRT NU, to obey to VRT NU resumepoint margins
        # we sometimes need to overrule Kodi watch status.
        # Use setting from advancedsettings.xml or default value
        # https://github.com/xbmc/xbmc/blob/master/xbmc/settings/AdvancedSettings.cpp
        # https://kodi.wiki/view/HOW-TO:Modify_automatic_watch_and_resume_points

        ignoresecondsatstart = get_advanced_setting_int('video/ignoresecondsatstart', default=180)
        ignorepercentatend = get_advanced_setting_int('video/ignorepercentatend', default=8)

        # Convert percentage to seconds
        ignoresecondsatend = round(total * (100 - ignorepercentatend) / 100.0)

        if position <= max(SECONDS_MARGIN, ignoresecondsatstart):
            # Check start margins
            if SECONDS_MARGIN <= position <= ignoresecondsatstart:
                return True
            if ignoresecondsatstart <= position <= SECONDS_MARGIN:
                return True

        if position >= min(total - SECONDS_MARGIN, ignoresecondsatend):
            # Check end margins
            if total - SECONDS_MARGIN <= position <= ignoresecondsatend:
                return True
            if ignoresecondsatend <= position <= total - SECONDS_MARGIN:
                return True

        return False
