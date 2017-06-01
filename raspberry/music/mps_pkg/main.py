#!/usr/bin/env python
# coding: utf-8
"""
mps.

https://github.com/np1/mps

Copyright (C)  2013-2014 nagev

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

from __future__ import print_function

__version__ = "0.20.16"
__author__ = "nagev"
__license__ = "GPLv3"

import xml.etree.ElementTree as ET
import unicodedata
import subprocess
import tempfile
import __main__
import logging
import hashlib
import difflib
import random
import socket
import zlib
import time
import math
import json
import sys
import re
import os


try:
    # pylint: disable=F0401
    from colorama import init as init_colorama, Fore, Style
    has_colorama = True

except ImportError:
    has_colorama = False


# Python 3 compatibility hack

if sys.version_info[:2] >= (3, 0):
    # pylint: disable=E0611,F0401
    import pickle
    from urllib.request import build_opener
    from urllib.error import HTTPError, URLError
    from urllib.parse import urlencode
    uni, byt, xinput = str, bytes, input
    xinput = input

else:
    from urllib2 import build_opener, HTTPError, URLError
    from urllib import urlencode
    import cPickle as pickle
    uni, byt, xinput = unicode, str, raw_input

utf8_encode = lambda x: x.encode("utf8") if type(x) == uni else x
utf8_decode = lambda x: x.decode("utf8") if type(x) == byt else x
mswin = os.name == "nt"
not_utf8_environment = mswin or not "UTF-8" in os.environ.get("LANG", "")
member_var = lambda x: not(x.startswith("__") or callable(x))
zcomp = lambda v: zlib.compress(pickle.dumps(v, protocol=2), 9)
zdecomp = lambda v: pickle.loads(zlib.decompress(v))


def dbg(*a, **b):
    """ Dumy function. """

    pass


def utf8_replace(txt):
    """ Replace unsupported characters in unicode string, returns unicode. """

    sse = sys.stdout.encoding
    txt = txt.encode(sse, "replace").decode("utf8", "ignore")
    return txt


def remove_special_chars(text):
    """ Fix filename for Windows. """

    text = utf8_replace(text) # replace unsupported characters
    allowed = re.compile(r'[^\\/?*$\'"%&:<>|]')
    text = "".join(x if allowed.match(x) else "_" for x in text)
    return text


def get_default_ddir():
    """ Get system default Download directory, append mps dir. """

    join, user = os.path.join, os.path.expanduser("~")

    if mswin:
        #return os.path.join(os.path.expanduser("~"), "Downloads", "mps")
        return join(user, "Downloads", "pms")

    USER_DIRS = join(user, ".config", "user-dirs.dirs")
    DOWNLOAD_HOME = join(user, "Downloads")

    if 'XDG_DOWNLOAD_DIR' in os.environ:
        ddir = os.environ['XDG_DOWNLOAD_DIR']

    elif os.path.exists(USER_DIRS):
        lines = open(USER_DIRS).readlines()
        defn = [x for x in lines if x.startswith("XDG_DOWNLOAD_DIR")]

        if len(defn) == 0:
            ddir = user

        else:
            ddir = defn[0].split("=")[1]\
                .replace('"', '')\
                .replace("$HOME", user).strip()

    elif os.path.exists(DOWNLOAD_HOME):
        ddir = DOWNLOAD_HOME

    else:
        ddir = user

    ddir = utf8_decode(ddir)
    return join(ddir, "mps")


def get_config_dir():
    """ Get user configuration directory.  Create if needed. """

    if mswin:
        # AppData\Roaming on Windows 7
        confd = os.environ["APPDATA"]
    else:
        if "XDG_CONFIG_HOME" in os.environ:
            confd = os.environ["XDG_CONFIG_HOME"]
        else:
            confd = os.path.join(os.environ["HOME"], ".config")

    oldd = os.path.join(confd, "pms")
    mpsd = os.path.join(confd, "mps")

    if os.path.exists(oldd) and not os.path.exists(mpsd):
        os.rename(oldd, mpsd)

    elif not os.path.exists(mpsd):
        os.makedirs(mpsd)

    return mpsd


class Config(object):

    """ Holds various configuration values. """

    PLAYER = "mplayer"
    PLAYERARGS = "-nolirc -prefer-ipv4"
    COLOURS = False if mswin and not has_colorama else True
    CHECKUPDATE = True
    SHOW_MPLAYER_KEYS = True
    DDIR = get_default_ddir()


try:
    import readline
    readline.set_history_length(2000)
    has_readline = True

except ImportError:
    has_readline = False

opener = build_opener()
ua = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"
opener.addheaders = [("User-Agent", ua)]
urlopen = opener.open


class Memo(object):

    """ Memo handling and creation. """

    def __init__(self, filepath, life=60 * 60 * 24 * 3):
        self.life = life
        self.filepath = filepath
        self.data = {}

        if os.path.isfile(filepath):

            try:

                with open(filepath, "rb") as f:
                    self.data = pickle.load(f)
                    dbg("cache opened, %s items", len(self.data))

            except (EOFError, IOError) as e:
                dbg(uni(e))

        else:
            dbg("No cache found!")

        self.prune()

    def add(self, key, val, lifespan=None):
        """ Add key value pair, expire in lifespan seconds. """

        key = key.encode("utf8")
        key = hashlib.sha1(key).hexdigest()
        lifespan = self.life if not lifespan else lifespan
        expiry_time = int(time.time()) + lifespan
        self.data[key] = dict(expire=expiry_time, data=zcomp(val))
        dbg("cache item added: %s", key)

    def get(self, key):
        """ Fetch a value if it exists and is fresh. """

        now = int(time.time())
        key = key.encode("utf8")
        key = hashlib.sha1(key).hexdigest()

        if key in self.data:

            if self.data[key]['expire'] > now:
                dbg("cache hit %s", key)
                return zdecomp(self.data[key]['data'])

            else:
                del self.data[key]
                return None

        return None

    def prune(self):
        """ Remove stale items. """

        now = int(time.time())
        dbg("Pruning: ")
        stalekeys = [x for x in self.data if self.data[x]['expire'] < now]
        dbg("%s stale keys; %s total kys", len(stalekeys), len(self.data))

        for x in stalekeys:
            del self.data[x]

    def save(self):
        """ Save memo file to persistent storage. """

        self.prune()

        with open(self.filepath, "wb") as f:
            pickle.dump(self.data, f, protocol=2)


class Playlist(object):

    """ Representation of a playist, has list of songs. """

    def __init__(self, name=None, songs=None):
        self.name = name
        self.creation = time.time()
        self.songs = songs or []

    @property
    def is_empty(self):
        """ Return True / False if songs are populated or not. """

        return bool(not self.songs)

    @property
    def size(self):
        """ Return number of tracks. """

        return len(self.songs)

    @property
    def duration(self):
        """ Sum duration of the playlist. """

        duration = 0

        for song in self.songs:
            duration += int(song['Rduration'])

        duration = time.strftime('%H:%M:%S', time.gmtime(int(duration)))
        return duration



class g(object):

    """ Class for holding globals that are needed throught the module. """

    debug_mode = False
    last_volume = None
    album_tracks_bitrate = 320
    model = Playlist(name="model")
    last_search_query = ""
    current_page = 1
    active = Playlist(name="active")
    blank_text = "\n" * 200
    text = {}
    userpl = {}
    last_opened = message = content = ""
    config = [x for x in sorted(dir(Config)) if member_var(x)]
    configbool = [x for x in config if type(getattr(Config, x)) is bool]
    defaults = {setting: getattr(Config, setting) for setting in config}
    CFFILE = os.path.join(get_config_dir(), "config")
    PLFILE = os.path.join(get_config_dir(), "playlist")
    memo = Memo(os.path.join(get_config_dir(), "cache" + sys.version[0:5]))
    OLD_CFFILE = os.path.join(os.path.expanduser("~"), ".pms-config")
    OLD_PLFILE = os.path.join(os.path.expanduser("~"), ".pms-playlist")
    READLINE_FILE = None


def showconfig(_):
    """ Dump config data. """

    s = "  %s%-17s%s : \"%s\"\n"
    out = "  %s%-17s   %s%s%s\n" % (c.ul, "Key", "Value", " " * 40, c.w)

    for setting in g.config:
        out += s % (c.g, setting.lower(), c.w, getattr(Config, setting))

    g.content = out
    g.message = "Enter %sset <key> <value>%s to change\n" % (c.g, c.w)
    g.message += "Enter %sset all default%s to reset all" % (c.g, c.w)


def saveconfig():
    """ Save current config to file. """

    config = {setting: getattr(Config, setting) for setting in g.config}

    if g.last_volume:
        config["last_volume"] = g.last_volume

    with open(g.CFFILE, "wb") as fh:
        pickle.dump(config, fh, protocol=2)


def clearcache():
    """ Clear the cache. """
    g.memo.data = {}
    g.memo.save()
    g.content = generate_songlist_display()
    g.message = c.r + "Cache cleared!" + c.w


__main__.Playlist = Playlist

# override config if config file exists
def loadconfig(pfile):
    """ Load config from file. """

    saved_config = pickle.load(open(pfile, "rb"))
    for kk, vv in saved_config.items():
        if kk == "last_volume":
            g.last_volume = vv
        else:
            setattr(Config, kk, vv)

# Account for old versions
if os.path.exists(g.CFFILE):
    loadconfig(g.CFFILE)

elif os.path.exists(g.OLD_CFFILE):
    loadconfig(g.OLD_CFFILE)
    saveconfig()
    os.remove(g.OLD_CFFILE)

if has_readline:
    g.READLINE_FILE = os.path.join(get_config_dir(), "input_history")

    if os.path.exists(g.READLINE_FILE):
        readline.read_history_file(g.READLINE_FILE)


class c(object):

    """ Class for holding colour code values. """

    if mswin and has_colorama:
        white = Style.RESET_ALL
        ul = Style.DIM + Fore.YELLOW
        red, green, yellow = Fore.RED, Fore.GREEN, Fore.YELLOW
        blue, pink = Fore.CYAN, Fore.MAGENTA

    elif mswin:
        Config.COLOURS = False

    else:
        white = "\x1b[%sm" % 0
        ul = "\x1b[%sm" * 3 % (2, 4, 33)
        cols = ["\x1b[%sm" % n for n in range(91, 96)]
        red, green, yellow, blue, pink = cols

    if not Config.COLOURS:
        ul = red = green = yellow = blue = pink = white = ""
    r, g, y, b, p, w = red, green, yellow, blue, pink, white


def setconfig(key, val):
    """ Set configuration variable. """

    # pylint: disable=R0912
    success_msg = fail_msg = ""
    key = key.upper()

    if key == "ALL" and val.upper() == "DEFAULT":

        for k, v in g.defaults.items():
            setattr(Config, k, v)
            success_msg = "Default configuration reinstated"

    elif key == "DDIR" and not val.upper() == "DEFAULT":

        valid = os.path.exists(val) and os.path.isdir(val)

        if valid:
            setattr(Config, key, val)
            success_msg = "Downloads will be saved to %s%s%s" % (c.y, val, c.w)

        else:
            fail_msg = "Invalid path: %s%s%s" % (c.r, val, c.w)

    elif key in g.configbool and not val.upper() == "DEFAULT":

        if val.upper() in "0 FALSE OFF NO".split():
            setattr(Config, key, False)
            success_msg = "%s set to disabled (restart may be required)" % key

        elif key == "COLOURS" and mswin and not has_colorama:
            fail_msg = "Can't enable colours, colorama not found"

        else:
            setattr(Config, key, True)
            success_msg = "%s set to enabled (restart may be required)" % key

    elif key in g.config:

        if val.upper() == "DEFAULT":
            val = g.defaults[key]

        setattr(Config, key, val)
        success_msg = "%s has been set to %s" % (key.upper(), val)

    else:
        fail_msg = "Unknown config item: %s%s%s" % (c.r, key, c.w)

    showconfig(1)

    if success_msg:
        saveconfig()
        g.message = success_msg

    elif fail_msg:
        g.message = fail_msg


HELP = """
Note: More documentation is available at {3}https://github.com/np1/mps{1}
{0}Searching{1}
You can enter an artist/song name to search whenever the program is expecting
text input. Searches must be prefixed with either a {2}.{1} or {2}/{1} \
character.

Search for albums by entering {2}album [albumname]{1}

When a list of songs is displayed, you can use the following commands:
{2}n{1} to show next 20 results
{2}p{1} to show previous 20 results

{0}Downloading{1}
{2}d 3{1} to download song 3

{0}Selecting Songs{1}
{2}all{1} to play all
{2}1 2 3{1} to play songs 1 2 and 3
{2}2-4 6 7-3{1} to play songs 2 3 4 6 7 6 5 4 3
{2}3-6 9-12 shuffle{1} to play selected songs in random order
{2}3-6 9-12 repeat{1} to play selected songs continuously

{0}Manipulating Songs{1}
{2}rm 1 3{1} to remove songs 1 and 3.  Also use rm 1 2 5-7 to remove a range
{2}rm all{1} to remove all songs
{2}sw 1 3{1} to swap the position of songs 1 and 3
{2}mv 1 3{1} to move song 1 to postion 3

{0}Playlist commands{1}
{2}add 1 2 5-7{1} to add songs 1 2 5 6 and 7 to the current playlist.
{2}add 1 2 3 <playlist_name>{1} to add songs 1,2,3 to a saved playlist.  A new
    playlist will be created if the given name doesn't already exist.
{2}vp{1} to view the current playlist (then use rm, mv and sw to modify it)
{2}ls{1} to list your saved playlists
{2}open <playlist_name or ID>{1} to open a saved playlist as the current \
playlist
{2}view <playlist name or ID>{1} to view a playlist (leaves current playlist \
intact)
{2}play <playlist name or ID>{1} to play a saved playlist directly
{2}save{1} or {2}save <playlist_name>{1} to save the currently displayed songs
    as a stored playlist on disk
{2}mv <old_name or ID> <new_name>{1} to rename a playlist
{2}rmp <playlist_name or ID>{1} to delete a playlist from disk

{2}q{1} to quit
""".format(c.ul, c.w, c.g, c.r)


def F(key, nb=0, na=0, percent=r"\*", nums=r"\*\*", textlib=None):
    """Format text.

    nb, na indicate newlines before and after to return
    percent is the delimter for %s
    nums is the delimiter for the str.format command (**1 will become {1})
    textlib is the dictionary to use (defaults to g.text if not given)

    """

    textlib = textlib or g.text

    assert key in textlib
    text = textlib[key]
    percent_fmt = textlib.get(key + "_")
    number_fmt = textlib.get("_" + key)

    if number_fmt:
        text = re.sub(r"(%s(\d))" % nums, "{\\2}", text)
        text = text.format(*number_fmt)

    if percent_fmt:
        text = re.sub(r"%s" % percent, r"%s", text)
        text = text % percent_fmt

    text = re.sub(r"&&", r"%s", text)

    return "\n" * nb + text + c.w + "\n" * na

g.text = {
    "exitmsg": """\
**0mps - **1http://github.com/np1/mps**0
Released under the GPLv3 license
(c) 2013-2014 nagev**2\n""",
    "_exitmsg": (c.r, c.b, c.w),

    # Error / Warning messages

    'no playlists': "*No saved playlists found!*",
    'no playlists_': (c.r, c.w),
    'pl bad name': '*&&* is not valid a valid name. Ensure it starts with a '
    'letter or _',
    'pl bad name_': (c.r, c.w),
    'pl not found': 'Playlist *&&* unknown. Saved playlists are shown above',
    'pl not found_': (c.r, c.w),
    'pl not found advise ls': 'Playlist "*&&*" not found. Use *ls* to list',
    'pl not found advise ls_': (c.y, c.w, c.g, c.w),
    'pl empty': 'Playlist is empty!',
    'advise add': 'Use *add N* to add a track',
    'advise add_': (c.g, c.w),
    'advise search': 'Search for songs and then use *add* to add them',
    'advise search_': (c.g, c.w),
    'no data': 'Error fetching data. Perhaps http://pleer.com is down.\n*&&*',
    'no data_': (c.r, c.w),
    'use dot': 'Start your query with a *.* to perform a search',
    'use dot_': (c.g, c.w),
    'cant get track': 'Problem fetching this track: *&&*',
    'cant get track_': (c.r, c.w),
    'track unresolved': 'Sorry, this track is not available',
    'no player': '*&&* was not found on this system',
    'no player_': (c.y, c.w),
    'no pl match for rename': '*Couldn\'t find matching playlist to rename*',
    'no pl match for rename_': (c.r, c.w),
    'invalid range': "*Invalid item / range entered!*",
    'invalid range_': (c.r, c.w),

    # Info messages

    'pl renamed': 'Playlist *&&* renamed to *&&*',
    'pl renamed_': (c.y, c.w, c.y, c.w),
    'pl saved': 'Playlist saved as *&&*.  Use *ls* to list playlists',
    'pl saved_': (c.y, c.w, c.g, c.w),
    'pl loaded': 'Loaded playlist *&&* as current playlist',
    'pl loaded_': (c.y, c.w),
    'pl viewed': 'Showing playlist *&&*',
    'pl viewed_': (c.y, c.w),
    'pl help': 'Enter *open <name or ID>* to load a playlist',
    'pl help_': (c.g, c.w),
    'added to pl': '*&&* tracks added (*&&* total [*&&*]). Use *vp* to view',
    'added to pl_': (c.y, c.w, c.y, c.w, c.y, c.w, c.g, c.w),
    'added to saved pl': '*&&* tracks added to *&&* (*&&* total [*&&*])',
    'added to saved pl_': (c.y, c.w, c.y, c.w, c.y, c.w, c.y, c.w),
    'song move': 'Moved *&&* to position *&&*',
    'song move_': (c.y, c.w, c.y, c.w),
    'song sw': ("Switched track *&&* with *&&*"),
    'song sw_': (c.y, c.w, c.y, c.w),
    'current pl': "This is the current playlist. Use *save <name>* to save it",
    'current pl_': (c.g, c.w),
    'songs rm': '*&&* tracks removed &&',
    'songs rm_': (c.y, c.w)
}


def save_to_file():
    """ Save playlists.  Called each time a playlist is saved or deleted. """

    f = open(g.PLFILE, "wb")
    pickle.dump(g.userpl, f, protocol=2)


def load_playlist(pfile):
    """ Load pickled playlist file. """

    try:
        f = open(pfile, "rb")
        g.userpl = pickle.load(f)

    except IOError:
        g.userpl = {}
        save_to_file()


def open_from_file():
    """ Open playlists. Called once on script invocation. """

    if os.path.exists(g.PLFILE):
        load_playlist(g.PLFILE)

    elif os.path.exists(g.OLD_PLFILE):
        load_playlist(g.OLD_PLFILE)
        save_to_file()
        os.remove(g.OLD_PLFILE)

    else:
        g.userpl = {}
        save_to_file()


def logo(col=None, version=""):
    """ Return text logo. """

    col = col if col else random.choice((c.g, c.r, c.y, c.b, c.p, c.w))
    LOGO = col + """\
                88888b.d88b.  88888b.  .d8888b
                888 "888 "88b 888 "88b 88K
                888  888  888 888  888 "Y8888b.
                888  888  888 888 d88P      X88
                888  888  888 88888P"   88888P'
                              888
                              888   %s%s
                              888%s
      """ % (c.w + "v" + version if version else "", col, c.w)
    return LOGO + c.w if not g.debug_mode else ""


def playlists_display():
    """ Produce a list of all playlists. """

    if not g.userpl:
        g.message = F("no playlists")
        return logo(c.y) + "\n\n" if g.model.is_empty else \
            generate_songlist_display()

    maxname = max(len(a) for a in g.userpl)
    out = "      {0}Saved Playlists{1}\n".format(c.ul, c.w)
    start = "      "
    fmt = "%s%s%-3s %-" + uni(maxname + 3) + "s%s %s%-7s%s %-5s%s"
    head = (start, c.b, "ID", "Name", c.b, c.b, "Count", c.b, "Duration", c.w)
    out += "\n" + fmt % head + "\n\n"

    for v, z in enumerate(sorted(g.userpl)):
        n, p = z, g.userpl[z]
        l = fmt % (start, c.g, v + 1, n, c.w, c.y, uni(p.size), c.y,
                   p.duration, c.w) + "\n"
        out += l

    return out


def mplayer_help(short=True):
    """ Mplayer help.  """

    volume = "[{0}9{1}] volume [{0}0{1}]"
    volume = volume if short else volume + "      [{0}ctrl-c{1}] return"
    seek = u"[{0}\u2190{1}] seek [{0}\u2192{1}]"
    pause = u"[{0}\u2193{1}] SEEK [{0}\u2191{1}]       [{0}space{1}] pause"

    if not_utf8_environment:
        seek = "[{0}<-{1}] seek [{0}->{1}]"
        pause = "[{0}DN{1}] SEEK [{0}UP{1}]       [{0}space{1}] pause"

    ret = "[{0}q{1}] %s" % ("return" if short else "next track")
    fmt = "    %-20s       %-20s"
    lines = fmt % (seek, volume) + "\n" + fmt % (pause, ret)
    return lines.format(c.g, c.w)


def tidy(raw, field):
    """ Tidy HTML entities, format songlength if field is duration.  """

    if field == "duration":
        raw = time.strftime('%M:%S', time.gmtime(int(raw)))

    else:
        for r in (("&#039;", "'"), ("&amp;#039;", "'"), ("&amp;amp;", "&"),
                 ("  ", " "), ("&amp;", "&"), ("&quot;", '"')):
            raw = raw.replace(r[0], r[1])

    return raw


def get_average_bitrate(song):
    """ Calculate average bitrate of VBR tracks. """

    if song["rate"] == "VBR":
        vbrsize = float(song["Rsize"][:-3]) * 8192
        vbrlen = float(song["Rduration"])
        vbrabr = int(vbrsize / vbrlen)

        # fix some songs reporting large bitrates
        if vbrabr > 320:
            dbg("---- %s => bitrate: %s", song["song"], uni(vbrabr))
            vbrabr = 320

        song["listrate"] = uni(vbrabr) + " v"  # for display in list
        song["rate"] = uni(vbrabr) + " Kb/s VBR"  # for playback display

    else:
        song["listrate"] = song["rate"][:3]  # not vbr list display

    return song


def get_tracks_from_page(page):
    """ Get search results from web page. """

    fields = "duration file_id singer song link rate size source".split()
    matches = re.findall(r"\<li.(duration[^>]+)\>", page)
    songs = []

    if matches:

        for song in matches:
            cursong = {}

            for f in fields:
                v = re.search(r'%s=\"([^"]+)"' % f, song)

                if v:
                    cursong[f] = tidy(v.group(1), f)
                    cursong["R" + f] = v.group(1)

                else:
                    cursong[f] = "unknown"
                    cursong["R" + f] = "unknown"
                    #raise Exception("problem with field " + f)

            cursong = get_average_bitrate(cursong)
            songs.append(cursong)

    else:
        dbg("got unexpected webpage or no search results")
        return False

    return songs


def xprint(stuff, end=None):
    """ Compatible print. """

    print(xenc(stuff), end=end)


def xenc(stuff):
    """ Replace unsupported characters. """
    stuff = utf8_replace(stuff) if not_utf8_environment else stuff
    return stuff


def screen_update():
    """ Display content, show message, blank screen."""

    print(g.blank_text)

    if g.content:
        xprint(g.content)

    if g.message:
        xprint(g.message)

    g.message = g.content = ""


def playback_progress(idx, allsongs, repeat=False):
    """ Generate string to show selected tracks, indicate current track. """

    # pylint: disable=R0914
    # too many local variables
    out = "  %s%-32s  %-33s %s   %s\n" % (c.ul, "Artist", "Title", "Time", c.w)
    show_key_help = (Config.PLAYER == "mplayer" or Config.PLAYER == "mpv")\
        and Config.SHOW_MPLAYER_KEYS
    multi = len(allsongs) > 1

    for n, song in enumerate(allsongs):
        i = song['singer'][:31], song['song'][:32], song['duration']
        rate = song['rate']
        fmt = (c.w, "  ", c.b, i[0], c.w, c.b, i[1], c.w, c.y, i[2], c.w)

        if n == idx:
            fmt = (c.y, "> ", c.p, i[0], c.w, c.p, i[1], c.w, c.p, i[2], c.w)
            r, cur = rate, i

        out += "%s%s%s%-32s%s  %s%-33s%s [%s%s%s]\n" % fmt

    out += "\n" * (3 - len(allsongs))
    pos = 8 * " ", c.y, idx + 1, c.w, c.y, len(allsongs), c.w
    playing = "{}{}{}{} of {}{}{}\n\n".format(*pos) if multi else "\n\n"
    keys = mplayer_help(short=(not multi and not repeat))
    out = out if multi else generate_songlist_display(song=allsongs[0])

    if show_key_help:
        out += "\n" + keys

    else:
        playing = "{}{}{}{} of {}{}{}\n".format(*pos) if multi else "\n"
        out += "\n" + " " * 58 if multi else ""

    fmt = playing, c.r, cur[1], c.w, c.r, cur[0], c.w, r
    out += "%s    %s%s%s by %s%s%s [%s]" % fmt
    out += "    REPEAT MODE" if repeat else ""
    return out


def real_len(u):
    """ Try to determine width of strings displayed with monospace font. """

    u = utf8_decode(u)
    ueaw = unicodedata.east_asian_width
    widths = dict(W=2, F=2, A=1, N=0.75, H=0.5)
    return int(round(sum(widths.get(ueaw(char), 1) for char in u)))


def uea_trunc(num, t):
    """ Truncate to num chars taking into account East Asian width chars. """

    while real_len(t) > num:
        t = t[:-1]

    return t


def uea_rpad(num, t):
    """ Right pad with spaces taking into account East Asian width chars. """

    t = uea_trunc(num, t)

    if real_len(t) < num:
        t = t + (" " * (num - real_len(t)))

    return t


def generate_songlist_display(song=False):
    """ Generate list of choices from a song list."""

    songs = g.model.songs or []

    if not songs:
        return logo(c.g) + "\n\n"

    fmtrow = "%s%-6s %-7s %-21s %-22s %-8s %-7s%s\n"
    head = (c.ul, "Item", "Size", "Artist", "Track", "Length", "Bitrate", c.w)
    out = "\n" + fmtrow % head

    for n, x in enumerate(songs):
        col = (c.r if n % 2 == 0 else c.p) if not song else c.b
        size = x.get('size') or 0
        title = x.get('song') or "unknown title"
        artist = x.get('singer') or "unknown artist"
        bitrate = x.get('listrate') or "unknown"
        duration = x.get('duration') or "unknown length"
        art, tit = uea_trunc(20, artist), uea_trunc(21, title)
        art, tit = uea_rpad(21, art), uea_rpad(22, tit)
        fmtrow = "%s%-6s %-7s %s %s %-8s %-7s%s\n"
        size = uni(size)[:3]
        size = size[0:2] + " " if size[2] == "." else size

        if not song or song != songs[n]:
            out += (fmtrow % (col, uni(n + 1), size + " Mb",
                              art, tit, duration[:8], bitrate[:6], c.w))
        else:
            out += (fmtrow % (c.p, uni(n + 1), size + " Mb",
                              art, tit, duration[:8], bitrate[:6], c.w))

    return out + "\n" * (5 - len(songs)) if not song else out


def get_stream(song, force=False):
    """ Return the url for a song. """

    if not "track_url" in song or force:
        url = 'http://pleer.com/site_api/files/get_url?action=download&id=%s'
        url = url % song['link']

        try:
            dbg("[0] fetching " + url)
            wdata = urlopen(url, timeout=7).read().decode("utf8")
            dbg("fetched " + url)

        except (HTTPError, socket.timeout):
            time.sleep(2)  # try again
            dbg("[1] fetching 2nd attempt ")
            wdata = urlopen(url, timeout=7).read().decode("utf8")
            dbg("fetched 2nd attempt" + url)

        j = json.loads(wdata)

        if not j.get("track_link"):
            raise URLError("This track is not accessible")

        track_url = j['track_link']
        return track_url

    else:
        return song['track_url']


def playsong(song, failcount=0):
    """ Play song using config.PLAYER called with args config.PLAYERARGS."""

    # pylint: disable = R0912
    try:
        track_url = get_stream(song)
        song['track_url'] = track_url

    except (URLError, HTTPError, socket.timeout) as e:
        g.message = F('cant get track') % uni(e)
        return

    except ValueError:
        g.message = F('track unresolved')
        return

    try:
        dbg("getting content-length header for " + track_url)
        cl = opener.open(track_url, timeout=5).headers['content-length']
        dbg("got CL header:" + (cl or "none"))

    except (IOError, KeyError):
        if failcount < 1:
            track_url = get_stream(song, force=True)
            dbg("stale stream url..updating")
            song['track_url'] = track_url
            save_to_file()
            playsong(song, failcount=1)
            return
        g.message = F('track unresolved')
        return

    pargs = Config.PLAYERARGS.split()

    if "mplayer" in Config.PLAYER:

        if "-really-quiet" in pargs:
            pargs.remove("-really-quiet")

        if g.last_volume and "-volume" not in pargs:
            pargs += ["-volume", g.last_volume]

    cmd = [Config.PLAYER] + pargs + [song['track_url']]

    # fix for github issue 59 of mps-youtube
    if "mplayer" in Config.PLAYER and mswin and sys.version_info[:2] < (3, 0):
            cmd = [x.encode("utf8", errors="replace") for x in cmd]

    stdout = stderr = None
    dbg(cmd)

    try:
        with open(os.devnull, "w") as fnull:

            if "mpv" in Config.PLAYER:
                stderr = fnull

            if mswin:
                stdout = stderr = fnull

            if "mplayer" in Config.PLAYER:
                p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, bufsize=1)
                mplayer_status(p, "", get_length(song))

            else:
                subprocess.call(cmd, stdout=stdout, stderr=stderr)

    except OSError:
        g.message = F('no player') % Config.PLAYER

    finally:
        try:
            p.terminate()  # make sure to kill mplayer if mps crashes

        except (OSError, AttributeError, UnboundLocalError):
            pass


def get_length(song):
    """ Return song length in seconds. """

    d = song['duration']
    return sum(int(x) * 60 ** n for n, x in enumerate(reversed(d.split(":"))))


def writestatus(text):
    """ Update status line. """

    spaces = 75 - len(text)
    sys.stdout.write(" " + text + (" " * spaces) + "\r")
    sys.stdout.flush()


def mplayer_status(popen_object, prefix="", songlength=0):
    """ Capture time progress from player output. Write status line. """

    # A: 175.6
    re_mplayer = re.compile(r"A:\s*(?P<elapsed_s>\d+)\.\d\s*")
    # Volume: 88 %
    re_mplayer_volume = re.compile(r"Volume:\s*(?P<volume>\d+)\s*%")

    last_displayed_line = None
    buff = ''
    volume_level = None

    while popen_object.poll() is None:
        char = popen_object.stdout.read(1).decode('utf-8', errors="ignore")

        if char in '\r\n':
            mv = re_mplayer_volume.search(buff)
            if mv:
                volume_level = int(mv.group("volume"))
                g.last_volume = str(volume_level)

            m = re_mplayer.match(buff)
            if m:
                line = make_status_line(m, songlength, volume=volume_level)

                if line != last_displayed_line:
                    writestatus(prefix + (" " if prefix else "") + line)
                    last_displayed_line = line

            buff = ''

        else:
            buff += char


def make_status_line(match_object, songlength=0, volume=None,
                     progress_bar_size=60):
    """ Format progress line output.  """

    try:
        elapsed_s = int(match_object.group('elapsed_s') or '0')

    except ValueError:
        return ""

    display_s = elapsed_s
    display_m = 0

    if elapsed_s >= 60:
        display_m = display_s // 60
        display_s %= 60

    pct = (float(elapsed_s) / songlength * 100) if songlength else 0

    status_line = "%02i:%02i %s" % (display_m, display_s,
                                    ("[%.0f%%]" % pct).ljust(6)
                                    )

    if volume:
        progress_bar_size -= 10
        vol_suffix = " vol: %d%%  " % volume

    else:
        vol_suffix = ""

    progress = int(math.ceil(pct / 100 * progress_bar_size))
    status_line += " [%s]" % ("=" * (progress - 1) +
                              ">").ljust(progress_bar_size)
    status_line += vol_suffix
    return status_line


def top(period, page=1):
    """ Get top music for period, returns songs list."""

    period = period or "w"
    periods = "_ w 3m 6m year all".split()
    period = periods.index(period)
    url = ("http://pleer.com/en/gettopperiod?target1=%s&target2=r1&select=e&"
           "page_ru=1&page_en=%s")
    url = url % ("e%s" % period, page)
    tps = "past week,past 3 months,past 6 months,past year,all time".split(",")
    msg = ("%sTop tracks for %s%s" % (c.y, tps[period - 1], c.w))
    g.message = msg
    dbg("[2] fetching " + url)

    try:
        wdata = urlopen(url).read().decode("utf8")

    except (URLError, HTTPError) as e:
        g.message = F('no data') % e
        g.content = logo(c.r)
        return

    dbg("fetched " + url)
    match = re.search(r"<ol id=\"search-results\">[\w\W]+?<\/ol>", wdata)
    html_ol = match.group(0)
    g.model.songs = get_tracks_from_page(html_ol)
    g.content = generate_songlist_display()


def search(term, page=1, splash=True):
    """ Perform search. """

    if not term or len(term) < 2:
        g.message = c.r + "Not enough input" + c.w
        g.content = generate_songlist_display()

    elif term == "albumsearch":
        return

    else:
        original_term = term
        url = "http://pleer.com/search"
        query = {"target": "tracks", "page": page}

        if "+best" in term:
            term = term.replace("+best", "")
            query["quality"] = "best"

        elif "+good" in term:
            term = term.replace("+good", "")
            query["quality"] = "good"

        query["q"] = term
        g.message = "Searching for '%s%s%s'" % (c.y, term, c.w)
        query = [(k, query[k]) for k in sorted(query.keys())]
        url = "%s?%s" % (url, urlencode(query))

        if g.memo.get(url):
            songs = g.memo.get(url)

        else:
            if splash:
                g.content = logo(c.b) + "\n\n"
                screen_update()

            try:
                wdata = urlopen(url).read().decode("utf8")
                songs = get_tracks_from_page(wdata)

            except (URLError, HTTPError) as e:
                g.message = F('no data') % e
                g.content = logo(c.r)
                return

            if songs:
                g.memo.add(url, songs)

        if songs:
            g.model.songs = songs
            g.message = "Search results for %s%s%s" % (c.y, term, c.w)
            g.last_opened = ""
            g.last_search_query = original_term
            g.current_page = page
            g.content = generate_songlist_display()

        else:
            g.message = "Found nothing for %s%s%s" % (c.y, term, c.w)
            g.content = logo(c.r)
            g.current_page = 1
            g.last_search_query = ""


def show_message(message, col=c.r, update=False):
    """ Show message using col, update screen if required. """

    g.content = generate_songlist_display()
    g.message = col + message + c.w

    if update:
        screen_update()


def search_album(term, page=1, splash=True, bitrate=g.album_tracks_bitrate):
    """Search for albums. """

    #pylint: disable=R0914,R0912
    if not term:
        show_message("Enter album name:", c.g, update=True)
        term = xinput("> ")

        if not term or len(term) < 2:
            g.message = c.r + "Not enough input!" + c.w
            g.content = generate_songlist_display()
            return

    album = _get_mb_album(term)

    if not album:
        show_message("Album '%s' not found!" % term)
        return

    out = "'%s' by %s%s%s\n\n" % (album['title'],
                                  c.g, album['artist'], c.w)
    out += ("[Enter] to continue, [q] to abort, or enter artist name for:\n"
            "    %s" % (c.y + term + c.w + "\n"))

    g.message, g.content = out, logo(c.b)
    screen_update()
    prompt = "Artist? [%s] > " % album['artist']
    xprint(prompt, end="")
    artistentry = xinput().strip()

    if artistentry:

        if artistentry == "q":
            show_message("Album search abandoned!")
            return

        album = _get_mb_album(term, artist=artistentry)

        if not album:
            show_message("Album '%s' by '%s' not found!" % (term, artistentry))
            return

    title, artist = album['title'], album['artist']
    mb_tracks = _get_mb_tracks(album['aid'])

    if not mb_tracks:
        show_message("Album '%s' by '%s' has 0 tracks!" % (title, artist))
        return

    msg = "%s%s%s by %s%s%s\n\n" % (c.g, title, c.w, c.g, artist, c.w)
    msg += "Specify bitrate to match or [q] to abort"
    g.message = msg
    g.content = "Tracks:\n"
    for n, track in enumerate(mb_tracks, 1):
        g.content += "%02s  %s" % (n, track['title'])
        g.content += "\n"

    #g.content = logo(c.b) + "\n\n"
    screen_update()
    bitrate = g.album_tracks_bitrate
    brentry = xinput("Bitrate? [%s] > " % bitrate)

    if brentry.isdigit():
        bitrate = int(brentry)

    elif brentry == "":
        pass

    else:
        show_message("Album search abandoned!")
        return

    songs = []
    print(g.blank_text)
    itt = _match_tracks(artist, title, bitrate, mb_tracks)

    while True:

        try:
            songs.append(next(itt))

        except KeyboardInterrupt:
            print("%sHalted!%s" % (c.r, c.w))
            break

        except StopIteration:
            break

    if songs:
        print("\n%s / %s songs matched" % (len(songs), len(mb_tracks)))
        xinput("Press Enter to continue")
        g.model.songs = songs
        g.message = "Contents of album %s%s - %s%s %s(%d/%d)%s:" % (
            c.y, artist, title, c.w, c.b, len(songs), len(mb_tracks), c.w)
        g.last_opened = ""
        g.last_search_query = ""
        g.current_page = page
        g.content = generate_songlist_display()

    else:
        g.message = "Found no album tracks for %s%s%s" % (c.y, title, c.w)
        g.content = generate_songlist_display()
        g.current_page = 1
        g.last_search_query = ""


def _match_tracks(artist, title, bitrate, mb_tracks):
    """ Match list of tracks in mb_tracks by performing multiple searches. """

    #pylint: disable=R0914
    title_artist_str = c.g + title + c.w, c.g + artist + c.w
    xprint("\nSearching for %s by %s" % title_artist_str)
    xprint("Attempting to match bitrate of %s kbps\n\n" % bitrate)
    url = "http://pleer.com/search"
    dtime = lambda x: time.strftime('%M:%S', time.gmtime(int(x)))

    # do matching
    for track in mb_tracks:
        ttitle = track['title']
        length = track['length']
        xprint("Search :  %s%s - %s%s - %s" % (c.y, artist, ttitle, c.w,
                                               dtime(length)))
        q = utf8_encode("%s %s" % (artist, ttitle))
        q = utf8_encode(ttitle) if artist == "Various Artists" else q
        query = {"target": "tracks", "page": 1, "q": q}
        wdata, fromcache = _do_query(url, query, err='album track error',
                                     report=True)
        results = get_tracks_from_page(wdata) if wdata else None

        if not fromcache:
            time.sleep(1.5)

        if not results:
            print(c.r + "Nothing matched :(\n" + c.w)
            continue

        s, score = _best_song_match(results, ttitle, length, bitrate)
        cc = c.g if score > 89 else c.y
        cc = c.r if score < 75 else cc
        xprint("Matched:  %s%s - %s%s - %s (%s kbps)\n[%sMatch confidence: "
               "%s%s]\n" % (c.y, s['singer'], s['song'], c.w, s['duration'],
                            s['listrate'], cc, score, c.w))
        yield s


def _get_mb_album(albumname, **kwa):
    """ Return artist, album title and track count from MusicBrainz. """

    url = "http://musicbrainz.org/ws/2/release/"
    qargs = dict(
        release='"%s"' % albumname,
        primarytype=kwa.get("primarytype", "album"),
        status=kwa.get("status", "official"))
    qargs.update({k: '"%s"' % v for k, v in kwa.items()})
    qargs = ["%s:%s" % item for item in qargs.items()]
    qargs = {"query": " AND ".join(qargs)}
    g.message = "Album search for '%s%s%s'" % (c.y, albumname, c.w)
    wdata = _do_query(url, qargs)

    if not wdata:
        return None

    ns = {'mb': 'http://musicbrainz.org/ns/mmd-2.0#'}
    root = ET.fromstring(utf8_encode(wdata))
    rlist = root.find("mb:release-list", namespaces=ns)

    if int(rlist.get('count')) == 0:
        return None

    album = rlist.find("mb:release", namespaces=ns)
    artist = album.find("./mb:artist-credit/mb:name-credit/mb:artist",
                        namespaces=ns).find("mb:name", namespaces=ns).text
    title = album.find("mb:title", namespaces=ns).text
    aid = album.get('id')
    return dict(artist=artist, title=title, aid=aid)


def _get_mb_tracks(albumid):
    """ Get track listing from MusicBraiz by album id. """

    ns = {'mb': 'http://musicbrainz.org/ns/mmd-2.0#'}
    url = "http://musicbrainz.org/ws/2/release/" + albumid
    query = {"inc": "recordings"}
    wdata = _do_query(url, query, err='album search error')

    if not wdata:
        return None

    root = ET.fromstring(utf8_encode(wdata))
    tlist = root.find("./mb:release/mb:medium-list/mb:medium/mb:track-list",
                      namespaces=ns)
    mb_songs = tlist.findall("mb:track", namespaces=ns)
    tracks = []
    path = "./mb:recording/mb:"

    for track in mb_songs:

        try:
            title, length, rawlength = "unknown", 0, 0
            title = track.find(path + "title", namespaces=ns).text
            rawlength = track.find(path + "length", namespaces=ns).text
            length = int(round(float(rawlength) / 1000))

        except (ValueError, AttributeError):
            xprint("not found")

        tracks.append(dict(title=title, length=length, rawlength=rawlength))

    return tracks


def _best_song_match(songs, title, duration, bitrate):
    """ Select best matching song based on title, length and bitrate.

    Score from 0 to 1 where 1 is best.

    """

    # pylint: disable=R0914
    seqmatch = difflib.SequenceMatcher
    variance = lambda a, b: float(abs(a - b)) / max(a, b)
    candidates = []

    for song in songs:
        dur, tit = int(song['Rduration']), song['song']
        bitr = int("".join(re.findall(r"\d", song['listrate'])))
        title_score = seqmatch(None, title, tit).ratio()
        bitrate_score = 1 - variance(bitrate, bitr)
        duration_score = 1 - variance(duration, dur)

        # apply weightings
        score = duration_score * .5 + title_score * .3 + bitrate_score * .2
        candidates.append((score, song))

    best_score, best_song = max(candidates, key=lambda x: x[0])
    percent_score = int(100 * best_score)
    return best_song, percent_score


def _do_query(url, query, err='query failed', cache=True, report=False):
    """ Perform http request.

    if cache is True, memo is utilised
    if report is True, return whether response is from memo

    """

    # convert query to sorted list of tuples (needed for consistent url_memo)
    query = [(k, query[k]) for k in sorted(query.keys())]
    url = "%s?%s" % (url, urlencode(query))

    if cache and g.memo.get(url):
        return g.memo.get(url) if not report else (g.memo.get(url), True)

    try:
        dbg("opening url %s", url)
        wdata = urlopen(url).read().decode("utf8")

    except (URLError, HTTPError) as e:
        g.message = "%s: %s (%s)" % (err, e, url)
        dbg(g.message)
        g.content = logo(c.r)
        return None if not report else (None, False)

    if cache and wdata:
        g.memo.add(url, wdata)

    return wdata if not report else (wdata, False)


def _make_fname(song):
    """" Create download directory, generate filename. """

    if not os.path.exists(Config.DDIR):
        os.makedirs(Config.DDIR)

    filename = song['singer'][:49] + " - " + song['song'][:49] + ".mp3"
    filename = filename.replace("/", "-")
    filename = remove_special_chars(filename) if mswin else filename
    filename = os.path.join(Config.DDIR, filename)
    filename = xenc(filename)
    return filename


def _download(song, filename):
    """ Download file, show status, return filename. """

    song['track_url'] = get_stream(song)
    dbg("fetching url " + song['track_url'])
    resp = urlopen(song['track_url'])
    dbg("fetched url " + song['track_url'])

    try:
        outfh = open(filename, 'wb')

    except IOError:
        # fat 32 doesn't like question marks
        filename = filename.replace("?", "_")
        outfh = open(filename.encode(sys.stdout.encoding,
                                     errors="replace"), "wb")

    xprint("Downloading %s%s%s ..\n" % (c.g, filename, c.w))
    total = int(resp.info()['Content-Length'].strip())
    chunksize, bytesdone, t0 = 16384, 0, time.time()
    status_string = ('  {0}{1:,}{2} Bytes [{0}{3:.2%}{2}] received. Rate: '
                     '[{0}{4:4.0f} kbps{2}].  ETA: [{0}{5:.0f} secs{2}]')
    while True:
        chunk = resp.read(chunksize)
        outfh.write(chunk)
        elapsed = time.time() - t0
        bytesdone += len(chunk)
        rate = (bytesdone / 1024) / elapsed
        eta = (total - bytesdone) / (rate * 1024)
        stats = (c.y, bytesdone, c.w, bytesdone * 1.0 / total, rate, eta)

        if not chunk:
            outfh.close()
            break

        status = status_string.format(*stats)
        sys.stdout.write("\r" + status + ' ' * 4 + "\r")
        sys.stdout.flush()

    return filename


def _bi_range(start, end):
    """
    Inclusive range function, works for reverse ranges.

    eg. 5,2 returns [5,4,3,2] and 2, 4 returns [2,3,4]

    """
    if start == end:
        return (start,)

    elif end < start:
        return reversed(range(end, start + 1))

    else:
        return range(start, end + 1)


def _parse_multi(choice, end=None):
    """ Handle ranges like 5-9, 9-5, 5- and -5. Return list of ints. """

    end = end or uni(g.model.size)
    pattern = r'(?<![-\d])(\d+-\d+|-\d+|\d+-|\d+)(?![-\d])'
    items = re.findall(pattern, choice)
    alltracks = []

    for x in items:

        if x.startswith("-"):
            x = "1" + x

        elif x.endswith("-"):
            x = x + uni(end)

        if "-" in x:
            nrange = x.split("-")
            startend = map(int, nrange)
            alltracks += _bi_range(*startend)

        else:
            alltracks.append(int(x))

    return alltracks


def _get_near_plname(begin):
    """ Return the closest matching playlist name that starts with begin. """

    for name in sorted(g.userpl):
        if name.lower().startswith(begin.lower()):
            break
    else:
        return begin

    return name


def play_pl(name):
    """ Play a playlist by name. """

    if name.isdigit():
        name = int(name)
        name = sorted(g.userpl)[name - 1]

    saved = g.userpl.get(name)

    if not saved:
        name = _get_near_plname(name)
        saved = g.userpl.get(name)

    if saved:
        g.model.songs = list(saved.songs)
        play_all("", "", "")

    else:
        g.message = F("pl not found") % name
        g.content = playlists_display()
        #return


def save_last(args=None):
    """ Save command with no playlist name. """

    if g.last_opened:
        open_save_view("save", g.last_opened)

    else:
        saveas = ""

        #save using artist name in postion 1
        if not g.model.is_empty:
            saveas = g.model.songs[0]['singer'][:15].strip()
            saveas = re.sub(r"[^-\w]", "-", saveas, re.UNICODE)

        # loop to find next available name
        post = 0

        while g.userpl.get(saveas):
            post += 1
            saveas = g.model.songs[0]['singer'][:15].strip() + "-" + uni(post)

        open_save_view("save", saveas)


def open_save_view(action, name):
    """ Open, save or view a playlist by name.  Get closest name match. """

    if action == "open" or action == "view":

        saved = g.userpl.get(name)

        if not saved:
            name = _get_near_plname(name)
            saved = g.userpl.get(name)

        if saved and action == "open":
            g.model.songs = g.active.songs = list(saved.songs)
            g.message = F("pl loaded") % name
            g.last_opened = name
            g.content = generate_songlist_display()

        elif saved and action == "view":
            g.model.songs = list(saved.songs)
            g.message = F("pl viewed") % name
            g.last_opened = ""
            g.content = generate_songlist_display()

        elif not saved and action in "view open".split():
            g.message = F("pl not found") % name
            g.content = playlists_display()

    elif action == "save":

        if not g.model.songs:
            g.message = "Nothing to save. " + F('advise search')

        else:
            name = name.replace(" ", "-")
            g.userpl[name] = Playlist(name, list(g.model.songs))
            g.message = F('pl saved') % name
            save_to_file()

        g.content = generate_songlist_display()


def open_view_bynum(action, num):
    """ Open or view a saved playlist by number. """

    srt = sorted(g.userpl)
    name = srt[int(num) - 1]
    open_save_view(action, name)


def songlist_rm_add(action, songrange):
    """ Remove or add tracks. works directly on user input. """

    selection = _parse_multi(songrange)

    if action == "add":

        for songnum in selection:
            g.active.songs.append(g.model.songs[songnum - 1])

        d = g.active.duration
        g.message = F('added to pl') % (len(selection), g.active.size, d)

    elif action == "rm":
        selection = list(reversed(sorted(list(set(selection)))))
        removed = uni(tuple(reversed(selection))).replace(",", "")

        for x in selection:
            g.model.songs.pop(x - 1)

        g.message = F('songs rm') % (len(selection), removed)

    g.content = generate_songlist_display()


def play(pre, choice, post=""):
    """ Play choice.  Use repeat/random if appears in pre/post. """

    if not g.model.songs:
        g.message = c.r + "There are no tracks to select" + c.w
        g.content = g.content or generate_songlist_display()

    else:
        shuffle = "shuffle" in pre + post
        repeat = "repeat" in pre + post
        selection = _parse_multi(choice)
        debug = ("shuffle=" + uni(shuffle) + " : repeat=" +
                 uni(repeat) + " : " + uni(selection))
        dbg(debug)
        songlist = [g.model.songs[x - 1] for x in selection]
        play_range(songlist, shuffle, repeat)


def play_all(pre, choice, post=""):
    """ Play all tracks in model (last displayed). shuffle/repeat if req'd."""

    options = pre + choice + post
    play(options, "1-" + uni(len(g.model.songs)))


def ls():
    """ List user saved playlists. """

    if not g.userpl:
        g.message = F('no playlists')
        g.content = g.content or generate_songlist_display()

    else:
        g.content = playlists_display()
        g.message = F('pl help')


def vp():
    """ View current working playlist. """

    if g.active.is_empty:
        txt = F('advise search') if g.model.is_empty else F('advise add')
        g.message = F('pl empty') + " " + txt

    else:
        g.model.songs = g.active.songs
        g.message = F('current pl')

    g.content = generate_songlist_display()


def play_range(songlist, shuffle=False, repeat=False):
    """ Play a range of songs, exit cleanly on keyboard interrupt. """

    if shuffle:
        random.shuffle(songlist)

    if not repeat:

        for n, song in enumerate(songlist):
            g.content = playback_progress(n, songlist, repeat=False)
            screen_update()

            try:
                playsong(song)

            except KeyboardInterrupt:
                print("Stopping...")
                time.sleep(1)
                g.message = c.y + "Playback halted" + c.w
                break

    elif repeat:

        while True:
            try:
                for n, song in enumerate(songlist):
                    g.content = playback_progress(n, songlist, repeat=True)
                    screen_update()
                    playsong(song)
                    g.content = generate_songlist_display()

            except KeyboardInterrupt:
                print("Stopping...")
                time.sleep(2)
                g.message = c.y + "Playback halted" + c.w
                break

    g.content = generate_songlist_display()


def show_help(helpname=None):
    """ Print help message. """

    print(g.blank_text)
    print(HELP)
    print("Press Enter to continue", end="")
    try:
        xinput("")
    except (KeyboardInterrupt, EOFError):
        prompt_for_exit()
    g.content = generate_songlist_display()


def quits(showlogo=True):
    """ Exit the program. """

    if has_readline:
        readline.write_history_file(g.READLINE_FILE)

    g.memo.save()
    saveconfig()
    msg = (g.blank_text) + logo(c.r, version=__version__) if showlogo else ""
    vermsg = ""
    print(msg + F("exitmsg", 2))

    if Config.CHECKUPDATE and showlogo:
        try:
            url = "https://github.com/np1/mps/raw/master/VERSION"
            v = urlopen(url).read().decode("utf8")
            v = re.search(r"^version\s*([\d\.]+)\s*$", v, re.MULTILINE)
            if v:
                v = v.group(1)
                if v > __version__:
                    vermsg += "\nA newer version is available (%s)\n" % v
        except (URLError, HTTPError, socket.timeout):
            pass

    #sys.exit(msg + F("exitmsg", 2) + vermsg)
    sys.exit(vermsg)


def download(num):
    """ Download a track. """

    song = (g.model.songs[int(num) - 1])
    filename = _make_fname(song)

    try:
        f = _download(song, filename)
        g.message = "Downloaded " + c.g + f + c.w

    except IndexError:
        g.message = c.r + "Invalid index" + c.w

    except KeyboardInterrupt:
        g.message = c.r + "Download halted!" + c.w

        try:
            os.remove(filename)

        except IOError:
            pass

    finally:
        g.content = generate_songlist_display()


def prompt_for_exit():
    """ Ask for exit confirmation. """

    g.message = c.r + "Press ctrl-c again to exit" + c.w
    g.content = generate_songlist_display()
    screen_update()

    try:
        userinput = xinput(c.r + " > " + c.w)

    except (KeyboardInterrupt, EOFError):
        quits(showlogo=False)

    return userinput


def playlist_remove(name):
    """ Delete a saved playlist by name - or purge working playlist if *all."""

    if name.isdigit() or g.userpl.get(name):

        if name.isdigit():
            name = int(name) - 1
            name = sorted(g.userpl)[name]

        del g.userpl[name]
        g.message = "Deleted playlist %s%s%s" % (c.y, name, c.w)
        g.content = playlists_display()
        save_to_file()

    else:
        g.message = F('pl not found advise ls') % name
        g.content = playlists_display()


def songlist_mv_sw(action, a, b):
    """ Move a song or swap two songs. """

    i, j = int(a) - 1, int(b) - 1

    if action == "mv":
        g.model.songs.insert(j, g.model.songs.pop(i))
        g.message = F('song move') % (g.model.songs[j]['song'], b)

    elif action == "sw":
        g.model.songs[i], g.model.songs[j] = g.model.songs[j], g.model.songs[i]
        g.message = F('song sw') % (min(a, b), max(a, b))

    g.content = generate_songlist_display()


def playlist_add(nums, playlist):
    """ Add selected song nums to saved playlist. """

    nums = _parse_multi(nums)

    if not g.userpl.get(playlist):
        playlist = playlist.replace(" ", "-")
        g.userpl[playlist] = Playlist(playlist)

    for songnum in nums:
        g.userpl[playlist].songs.append(g.model.songs[songnum - 1])
        dur = g.userpl[playlist].duration
        f = (len(nums), playlist, g.userpl[playlist].size, dur)
        g.message = F('added to saved pl') % f
        save_to_file()

    g.content = generate_songlist_display()


def playlist_rename_idx(_id, name):
    """ Rename a playlist by ID. """

    _id = int(_id) - 1
    playlist_rename(sorted(g.userpl)[_id] + " " + name)


def playlist_rename(playlists):
    """ Rename a playlist using mv command. """

    # Deal with old playlist names that permitted spaces
    a, b = "", playlists.split(" ")
    while a not in g.userpl:
        a = (a + " " + (b.pop(0))).strip()
        if not b and not a in g.userpl:
            g.message = F('no pl match for rename')
            g.content = g.content or playlists_display()
            return

    b = "-".join(b)
    g.userpl[b] = Playlist(b)
    g.userpl[b].songs = list(g.userpl[a].songs)
    playlist_remove(a)
    g.message = F('pl renamed') % (a, b)
    save_to_file()


def add_rm_all(action):
    """ Add all displayed songs to current playlist.

    remove all displayed songs from view.

    """

    if action == "rm":
        for n in reversed(range(0, len(g.model.songs))):
            g.model.songs.pop(n)
        g.message = c.b + "Cleared all songs" + c.w
        g.content = generate_songlist_display()

    elif action == "add":
        size = g.model.size
        songlist_rm_add("add", "-" + uni(size))


def nextprev(np):
    """ Get next / previous search results. """

    if np == "n":
        if len(g.model.songs) == 20 and g.last_search_query:
            g.current_page += 1
            search(g.last_search_query, g.current_page, splash=False)
            g.message += " : page %s" % g.current_page

        else:
            g.message = "No more songs to display"

    elif np == "p":
        if g.current_page > 1 and g.last_search_query:
            g.current_page -= 1
            search(g.last_search_query, g.current_page, splash=False)
            g.message += " : page %s" % g.current_page

        else:
            g.message = "No previous songs to display"

    g.content = generate_songlist_display()


def plist(parturl):
    """ Import playlist created on website. """

    url = "http://pleer.com/en/" + parturl

    try:
        page = urlopen(url).read().decode("utf8")
        songs = get_tracks_from_page(page)
        g.model.songs = songs
        g.active.songs = songs
        g.message = c.y + "Playlist imported" + c.w

    except IOError:
        g.message = "Problem fetching that list."

    g.content = generate_songlist_display()


def get_version_info():
    """ Return version and platform info. """

    import platform
    out = ("\nmps version    : %s " % __version__)
    out += ("\nPython version : %s" % sys.version)
    out += ("\nProcessor      : %s" % platform.processor())
    out += ("\nMachine type   : %s" % platform.machine())
    out += ("\nArchitecture   : %s, %s" % platform.architecture())
    out += ("\nPlatform       : %s" % platform.platform())
    envs = "TERM SHELL LANG LANGUAGE".split()

    for env in envs:
        value = os.environ.get(env)
        out += "\nenv:%-11s: %s" % (env, value) if value else ""

    return out


def main():
    """ Main control loop. """

    # update screen
    g.content = generate_songlist_display()
    g.content = logo(col=c.g, version=__version__) + "\n"
    g.message = "Enter .artist/song name to search or [h]elp"
    screen_update()

    # open playlists from file
    open_from_file()

    # get cmd line input
    inp = " ".join(sys.argv[1:])

    # input types
    word = r'[^\W\d][-\w\s]{,100}'
    rs = r'(?:repeat\s*|shuffle\s*)'
    regx = {
        'ls': r'ls$',
        'vp': r'vp$',
        'top': r'top(|3m|6m|year|all)\s*$',
        'plist': r'.*(list[\da-zA-Z]{8,14})$',
        'play': r'(%s{0,3})([-,\d\s]{1,250})\s*(%s{0,2})$' % (rs, rs),
        'quits': r'(?:q|quit|exit)$',
        'search': r'(?:search|\.|/)\s*(.{0,500})',
        'search_album': r'album\s*(.{0,500})',
        'play_pl': r'play\s*(%s|\d+)$' % word,
        'download': r'(?:d|dl|download)\s*(\d{1,4})$',
        'nextprev': r'(n|p)$',
        'play_all': r'(%s{0,3})all\s*(%s{0,3})$' % (rs, rs),
        'save_last': r'(save)\s*$',
        #'setconfig': r'set\s*(\w+)\s*"([^"]*)"\s*$',
        'setconfig': r'set\s*(\w+)\s*"?([^"]*)"?\s*$',
        'show_help': r'(?:help|h)$',
        'add_rm_all': r'(rm|add)\s*all$',
        'clearcache': r'clearcache$',
        #'showconfig': r'(showconfig)',
        'showconfig': r'(set|showconfig)\s*$',
        'playlist_add': r'add\s*(-?\d[-,\d\s]{1,250})(%s)$' % word,
        'open_save_view': r'(open|save|view)\s*(%s)$' % word,
        'songlist_mv_sw': r'(mv|sw)\s*(\d{1,4})\s*[\s,]\s*(\d{1,4})$',
        'songlist_rm_add': r'(rm|add)\s*(-?\d[-,\d\s]{,250})$',
        'playlist_rename': r'mv\s*(%s\s+%s)$' % (word, word),
        'playlist_remove': r'rmp\s*(\d+|%s)$' % word,
        'open_view_bynum': r'(open|view)\s*(\d{1,4})$',
        'playlist_rename_idx': r'mv\s*(\d{1,3})\s*(%s)\s*$' % word,
    }

    # compile regexp's
    regx = {name: re.compile(val, re.UNICODE) for name, val in regx.items()}
    prompt = "> "

    while True:
        try:
            # get user input
            userinput = inp or xinput(prompt)
            userinput = userinput.strip()
            print(c.w)

        except (KeyboardInterrupt, EOFError):
            userinput = prompt_for_exit()

        inp = None

        for k, v in regx.items():
            if v.match(userinput):
                func, matches = k, v.match(userinput).groups()

                try:
                    globals()[func](*matches)

                except IndexError:
                    g.message = F('invalid range')
                    g.content = g.content or generate_songlist_display()

                break
        else:
            g.content = g.content or generate_songlist_display()

            if userinput:
                g.message = c.b + "Bad syntax. Enter h for help" + c.w

        screen_update()


if "--debug" in sys.argv or os.environ.get("mpsdebug") == '1':
    print(get_version_info())
    sys.argv = [_x for _x in sys.argv if not "--debug" in _x]
    g.debug_mode = True
    g.blank_text = "--\n"
    logfile = os.path.join(tempfile.gettempdir(), "mps.log")
    logging.basicConfig(level=logging.DEBUG, filename=logfile)
    logging.getLogger("pafy").setLevel(logging.DEBUG)

if "--version" in sys.argv:
    print(get_version_info())
    print("")
    sys.exit()

elif "--logging" in sys.argv or os.environ.get("mpslog") == '1':
    sys.argv = [_x for _x in sys.argv if not "--logging" in _x]
    logfile = os.path.join(tempfile.gettempdir(), "mps.log")
    logging.basicConfig(level=logging.DEBUG, filename=logfile)

dbg = logging.debug  # pylint: disable=W0404

if has_colorama:
    init_colorama()

if __name__ == "__main__":
    main()
