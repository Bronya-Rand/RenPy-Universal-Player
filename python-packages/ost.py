# Copyright (C) 2021 GanstaKingofSA (Hanaka)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Pardon any mess within this PY file. Finally PEP8'd it.

import re
import os
import json
import threading
import logging
import renpy
import pygame_sdl2
from tinytag import TinyTag
from renpy.text.text import Text
from renpy.display.im import image
import renpy.audio.music as music
import renpy.display.behavior as displayBehavior
import renpy.random as rendom  # Ren'Py Random
import renpy.game.preferences as gamePreference

# Creation of Music Room and Code Setup
version = 2.0
music.register_channel("music_room", mixer="music_room_mixer", loop=False)
if renpy.windows:
    gamedir = renpy.config.gamedir.replace("\\", "/")
elif renpy.android:
    try:
        os.mkdir(os.path.join(os.environ["ANDROID_PUBLIC"], "game"))
    except:
        pass
    gamedir = os.path.join(os.environ["ANDROID_PUBLIC"], "game")
    try:
        renpy.file(gamedir + "/RPASongMetadata.json", "r")
    except:
        open(gamedir + "/RPASongMetadata.json", "w").write(
            renpy.file("RPASongMetadata.json").read()
        )
else:
    gamedir = renpy.config.gamedir

# Lists for holding media types
soundtracks = []
rendom.Random()


class OSTPlayerInfo:
    def __init__(self, channel="music_room"):
        self.current_soundtrack = None
        self.channel = channel
        self.time_position = 0.0
        self.time_duration = 1.0

    def get_pos(self):
        if music.get_pos(self.channel) is not None:
            self.time_position = music.get_pos(self.channel)

        return self.time_position

    def get_duration(self, songPath=None):
        if self.current_soundtrack and self.get_bytetime() and not songPath:
            return self.get_bytetime()
        else:
            try:
                if songPath:
                    pathToSong = songPath
                else:
                    pathToSong = self.get_path()

                tags = TinyTag.get(pathToSong, image=False)

                if tags.duration:
                    self.time_duration = tags.duration
                else:
                    if not songPath:
                        self.time_duration = (
                            music.get_duration(self.channel) or self.time_duration
                        )
            except:
                if not songPath:
                    self.time_duration = (
                        music.get_duration(self.channel) or self.time_duration
                    )

        return self.time_duration

    def convert_time(self, x):
        hour = ""

        if int(x / 3600) > 0:
            hour = str(int(x / 3600))

        if hour != "":
            if int((x % 3600) / 60) < 10:
                minute = ":0" + str(int((x % 3600) / 60))
            else:
                minute = ":" + str(int((x % 3600) / 60))
        else:
            minute = "" + str(int(x / 60))

        if int(x % 60) < 10:
            second = ":0" + str(int(x % 60))
        else:
            second = ":" + str(int(x % 60))

        return hour + minute + second

    def set_current_soundtrack(self, nst):
        self.current_soundtrack = nst

    def get_current_soundtrack(self):
        return self.current_soundtrack

    def get_title(self):
        return self.current_soundtrack.name

    def get_artist(self):
        return self.current_soundtrack.author

    def get_album(self):
        return self.current_soundtrack.album

    def get_album_artist(self):
        return self.current_soundtrack.albumartist

    def get_composer(self):
        return self.current_soundtrack.composer

    def get_genre(self):
        return self.current_soundtrack.genre

    def get_bytetime(self):
        return self.current_soundtrack.byteTime

    def get_sideload(self):
        return self.current_soundtrack.sideloaded

    def get_description(self):
        return self.current_soundtrack.description

    def get_cover_art(self):
        return self.current_soundtrack.cover_art

    def get_path(self):
        return self.current_soundtrack.path

    def music_pos(self, style_name, st, at):
        readableTime = self.convert_time(self.get_pos())

        if persistent.listui:
            return Text(readableTime, style=style_name, substitute=False, size=16), 0.20
        else:
            return Text(readableTime, style=style_name), 0.20

    def music_dur(self, style_name, st, at):
        readableDuration = self.convert_time(self.get_duration())

        if persistent.listui:
            return (
                Text(readableDuration, style=style_name, substitute=False, size=16),
                0.20,
            )
        else:
            return Text(readableDuration, style=style_name), 0.20

    def dynamic_title_text(self, style_name, st, at):
        title = self.get_title()

        if persistent.listui:
            return Text(title, style=style_name, substitute=False, size=20), 0.20

        if len(title) <= 21:
            songTextSize = int(37)
        elif len(title) <= 28:
            songTextSize = int(29)
        else:
            songTextSize = int(23)

        return Text(title, style=style_name, substitute=False, size=songTextSize), 0.20

    def dynamic_author_text(self, style_name, st, at):
        author = self.get_artist()

        if persistent.listui:
            return Text(author, style=style_name, substitute=False, size=20), 0.20

        if len(author) <= 32:
            authorTextSize = int(25)
        elif len(author) <= 48:
            authorTextSize = int(23)
        else:
            authorTextSize = int(21)

        return (
            Text(author, style=style_name, substitute=False, size=authorTextSize),
            0.20,
        )

    def refresh_cover_data(self, st, at):
        return image(self.get_cover_art().replace("[", "\[")), 0.20

    def dynamic_album_text(self, style_name, st, at):
        album = self.get_album()

        if persistent.listui:
            return Text(album, style=style_name, substitute=False, size=20), 0.20

        if len(album) <= 32:
            albumTextSize = int(25)
        elif len(album) <= 48:
            albumTextSize = int(23)
        else:
            albumTextSize = int(21)

        return Text(album, style=style_name, substitute=False, size=albumTextSize), 0.20


ost_info = OSTPlayerInfo()


class OSTPlayerControls:
    def __init__(self, channel="music_room"):
        self.channel = channel
        self.pausedState = False
        self.pausedAt = None
        self.oldVolume = 0.0
        self.randomSong = False
        self.loopSong = False

    def get_loop_status(self):
        return self.loopSong

    def get_shuffle_status(self):
        return self.randomSong

    def auto_play_pause_button(self, st, at):
        if renpy.audio.music.is_playing(self.channel):
            if self.pausedState:
                d = displayBehavior.ImageButton("images/music_room/pause.png")
            else:
                d = displayBehavior.ImageButton(
                    "images/music_room/pause.png", action=self.pause_music
                )
        else:
            d = displayBehavior.ImageButton(
                "images/music_room/play.png", action=self.play_music
            )
        return d, 0.20

    def pause_music(self):
        self.pausedState = True

        if not music.is_playing(self.channel):
            return

        soundtrack_position = (music.get_pos(self.channel) or 0.0) + 1.6

        if soundtrack_position is not None:
            self.pausedAt = (
                "<from " + str(soundtrack_position) + ">" + ost_info.get_path()
            )

        music.stop(self.channel, fadeout=2.0)

    def play_music(self):
        self.pausedState = False

        if not self.pausedAt:
            music.play(ost_info.get_path(), self.channel, fadein=2.0)
        else:
            music.play(self.pausedAt, self.channel, fadein=2.0)

    def forward_music(self):
        if not music.get_pos(self.channel):
            soundtrack_position = ost_info.get_pos() + 5
        else:
            soundtrack_position = music.get_pos(self.channel) + 5

        if soundtrack_position >= ost_info.get_duration():
            self.pausedAt = False
            if self.randomSong:
                self.random_song()
            else:
                self.next_track()
        else:
            self.pausedAt = (
                "<from " + str(soundtrack_position) + ">" + ost_info.get_path()
            )

            music.play(self.pausedAt, self.channel)

    def rewind_music(self):
        if not music.get_pos(self.channel):
            soundtrack_position = ost_info.get_pos() - 5
        else:
            soundtrack_position = music.get_pos(self.channel) - 5

        if soundtrack_position <= 0.0:
            self.pausedAt = False
            self.next_track(True)
        else:
            self.pausedAt = (
                "<from " + str(soundtrack_position) + ">" + ost_info.get_path()
            )

            music.play(self.pausedAt, self.channel)

    def next_track(self, back=False):
        index = 0
        while ost_info.current_soundtrack != soundtracks[index]:
            index = index + 1

        if back:
            ost_info.current_soundtrack = soundtracks[index - 1]
        else:
            try:
                ost_info.current_soundtrack = soundtracks[index + 1]
            except:
                ost_info.current_soundtrack = soundtracks[0]

        if not renpy.get_screen("music_room"):
            renpy.notify(
                "Now Playing: " + ost_info.get_title() + " - " + ost_info.get_artist()
            )

        music.play(ost_info.get_path(), self.channel, self.loopSong)

    def random_track(self):
        unique = 1
        while unique != 0:
            a = rendom.randint(0, len(soundtracks))
            if ost_info.current_soundtrack != soundtracks[a]:
                unique = 0
                ost_info.current_soundtrack = soundtracks[a]

        if not renpy.get_screen("music_room"):
            renpy.notify(
                "Now Playing: " + ost_info.get_title() + " - " + ost_info.get_artist()
            )

        renpy.audio.music.play(ost_info.get_path(), self.channel, self.loopSong)

    def mute_player(self):
        logging.info("Muting the audio player.")

        if gamePreference.get_volume("music_room_mixer") != 0.0:
            self.oldVolume = gamePreference.get_volume("music_room_mixer")
            gamePreference.set_volume("music_room_mixer", 0.0)
        else:
            if self.oldVolume == 0.0:
                gamePreference.set_volume("music_room_mixer", 0.5)
            else:
                gamePreference.set_volume("music_room_mixer", self.oldVolume)

    def check_paused_state(self):
        logging.info(
            "Checking if a music session exists or if we are in a paused state."
        )
        if not ost_info.current_soundtrack or self.pausedState:
            logging.info(
                "No music session found or we are currently in a paused state. "
                "Exiting check state."
            )
            return
        else:
            logging.info(
                "A music session was found or we are currently not in a paused state. "
                "Stopping music session and exiting check state."
            )
            self.pause_music()


ost_controls = OSTPlayerControls()


class soundtrack:
    def __init__(
        self,
        name,
        author,
        path,
        album="Unknown Album",
        albumartist="Unknown Album Artist",
        composer="Unknown Composer",
        genre="Unknown Genre",
        byteTime=False,
        sideloaded=False,
        description="",
        cover_art=None,
        unlocked=True,
    ):
        self.name = name
        self.author = author
        self.path = path
        self.album = album
        self.albumartist = albumartist
        self.composer = composer
        self.genre = genre
        self.byteTime = byteTime
        self.sideloaded = sideloaded
        self.description = description
        if not cover_art:
            self.cover_art = "images/music_room/nocover.png"
        else:
            self.cover_art = cover_art
        self.unlocked = unlocked


class ExternalOSTMonitor:
    def __init__(self, channel="music_player"):
        self.channel = channel
        self.lock = threading.RLock()
        self.periodic_condition = threading.Condition()
        self.ost_thread = threading.Thread(target=self.ost_thread_main)
        self.ost_thread.daemon = True
        self.ost_thread.start()

    def get_pos_duration(self):
        pos = music.get_pos(self.channel) or 0.0
        duration = ost_info.get_duration()

        return pos, duration

    def get_song_options_status(self):
        return ost_controls.get_loop_status(), ost_controls.get_shuffle_status()

    def ost_thread_main(self):
        while True:
            with self.periodic_condition:
                self.periodic_condition.wait(0.05)

            with self.lock:
                try:
                    pos, duration = self.get_pos_duration()
                    loopThis, doRandom = self.get_song_options_status()

                    if pos >= duration - 0.20:
                        if loopThis:
                            music.play(ost_info.get_path(), self.channel, loop=True)
                        elif doRandom:
                            ost_controls.random_track()
                        else:
                            ost_controls.next_track()
                except:
                    pass


@renpy.exports.pure
class AdjustableAudioPositionValue(renpy.ui.BarValue):
    def __init__(self, channel="music_player", update_interval=0.0):
        self.channel = channel
        self.update_interval = update_interval
        self.adjustment = None
        self._hovered = False

    def get_pos_duration(self):
        pos = music.get_pos(self.channel) or 0.0
        duration = ost_info.get_duration()

        return pos, duration

    def get_adjustment(self):
        pos, duration = self.get_pos_duration()
        self.adjustment = renpy.ui.adjustment(
            value=pos, range=duration, changed=self.set_pos, adjustable=True
        )

        return self.adjustment

    def hovered(self):
        self._hovered = True

    def unhovered(self):
        self._hovered = False

    def set_pos(self, value):
        if self._hovered and pygame_sdl2.mouse.get_pressed()[0]:
            music.play("<from {}>".format(value) + ost_info.get_path(), self.channel)
            if ost_controls.get_loop_status():
                music.queue(ost_info.get_path(), self.channel, True)

    def periodic(self, st):
        pos, duration = self.get_pos_duration()

        if pos and pos <= duration:
            self.adjustment.set_range(duration)
            self.adjustment.change(pos)

        return self.update_interval


class OSTPlayerSongAssign:
    def __init__(self):
        self.automaticList = []
        self.manualList = []
        self.file_types = (".mp3", ".ogg", ".opus", ".wav")

    def refresh_list(self):
        logging.info("Refreshing the music player list.")
        self.scan_song()
        if renpy.config.developer:
            self.rpa_mapping()
        self.resort()

    def resort(self):
        global soundtracks
        logging.info("Sorting the music player list.")

        for obj in self.automaticList:
            if obj not in soundtracks and obj.unlocked:
                soundtracks.append(obj)
        logging.info("Added auto-defined songs to the music list.")

        for obj in self.manualList:
            if obj not in soundtracks and obj.unlocked:
                soundtracks.append(obj)
        logging.info("Added manual-defined songs to the music list.")

        soundtracks = sorted(soundtracks, key=lambda soundtracks: soundtracks.name)

    def get_info(self, path, tags):
        sec = tags.duration
        try:
            image_data = tags.get_image()

            with renpy.exports.file("python-packages/binaries.txt") as a:
                lines = a.readlines()

            jpgbytes = bytes("\\xff\\xd8\\xff")
            pngbytes = bytes("\\x89PNG")
            utfbytes = bytes("o\\x00v\\x00e\\x00r\\x00\\x00\\x00\\x89PNG\\r\\n")

            jpgmatch = re.search(jpgbytes, image_data)
            pngmatch = re.search(pngbytes, image_data)
            utfmatch = re.search(utfbytes, image_data)

            if jpgmatch:
                cover_formats = ".jpg"
            elif pngmatch:
                cover_formats = ".png"
            else:
                raise TypeError

            if utfmatch:  # addresses itunes cover descriptor fixes
                logging.warning("Improper PNG data was found. Repairing cover art.")
                image_data = re.sub(utfbytes, lines[2], image_data)
            else:
                raise TypeError

            coverAlbum = re.sub(
                r"(\\|/|\:|\?|\*|\<|\>|\||\[|\])", "", tags.album or tags.title
            )

            if not os.path.exists(
                os.path.join(gamedir, "track/covers", coverAlbum + cover_formats)
            ):
                with open(
                    os.path.join(gamedir, "track/covers", coverAlbum + cover_formats),
                    "wb",
                ) as f:
                    f.write(image_data)

                art = "track/covers/" + coverAlbum + cover_formats
                logging.info("Obtained album cover for " + path + ".")
                return art
        except TypeError:
            logging.warning(
                'Cover art could not be obtained/written to the "covers" directory.'
            )
            return None

    def scan_song(self):
        logging.info("Scanning music directories.")
        exists = self.check_removed_songs()

        logging.info('Scanning the "track" folder for music.')
        for x in os.listdir(gamedir + "/track"):
            if x.endswith((self.file_types)) and "track/" + x not in exists:
                path = "track/" + x
                logging.info("Obtaining metadata info for " + path + ".")

                try:
                    tags = TinyTag.get(gamedir + "/" + path, image=True)
                except IOError:
                    logging.error(
                        "'IOError' while obtaining metadata info for "
                        + path
                        + ". Skipping song."
                    )
                    continue

                albumart = self.get_info(path, tags)
                self.def_song(path, tags, albumart, True)
                exists.append(path)

    def check_removed_songs(self):
        exists = []
        logging.info("Checking for removed songs.")

        for x in self.automaticList[:]:
            try:
                renpy.exports.file(x.path)
                exists.append(x.path)
            except:
                logging.info("Removed " + x.path + " from the music player list.")
                self.automaticList.remove(x)

        return exists

    def def_song(self, path, tags, albumart, unlocked=True):
        logging.info("Defining song located in " + path + " to the music player.")
        class_name = re.sub(
            r"-|'| ", "_", tags.title or str(path.replace("track/", ""))
        )

        class_name = soundtrack(
            name=tags.title or str(path.replace("track/", "")),
            author=tags.artist or "Unknown Artist",
            album=tags.album or "Unknown Album",
            albumartist=tags.albumartist or "Unknown Album Artist",
            composer=tags.composer or "Unknown Composer",
            genre=tags.genre or "Unknown Genre",
            path=path,
            byteTime=tags.duration or False,
            sideloaded=True,
            description=tags.comment or "",
            cover_art=albumart,
            unlocked=unlocked,
        )
        self.automaticList.append(class_name)

    def rpa_mapping(self):
        if not renpy.config.developer:
            return
        data = []

        try:
            os.remove(os.path.join(gamedir, "RPASongMetadata.json"))
        except:
            pass

        for y in self.automaticList:
            data.append(
                {
                    "class": re.sub(
                        r"-|'| ", "_", y.name or str(y.path.replace("track/", ""))
                    ),
                    "title": y.name,
                    "artist": y.author,
                    "album": y.album,
                    "albumartist": y.albumartist,
                    "composer": y.composer,
                    "genre": y.genre,
                    "path": y.path,
                    "sec": y.byteTime,
                    "sideloaded": y.sideloaded,
                    "comment": y.description,
                    "cover_art": y.cover_art,
                    "unlocked": y.unlocked,
                }
            )

        with open(gamedir + "/RPASongMetadata.json", "a") as f:
            json.dump(data, f)

    def rpa_load_mapping(self):
        try:
            logging.info("Attempting to load 'RPASongMetadata.json'.")
            with renpy.exports.file("RPASongMetadata.json") as f:
                data = json.load(f)
            logging.info("Loaded 'RPASongMetadata.json'.")
        except IOError:
            logging.warning("Attempting to load 'RPASongMetadata.json' failed.")
            return

        exists = self.check_removed_songs()

        for p in data:
            logging.info(
                "Defining cached class " + p["class"] + " to the music player."
            )
            if p["path"] not in exists:
                p["class"] = soundtrack(
                    name=p["title"],
                    author=p["artist"],
                    album=p["album"],
                    albumartist=p["albumartist"],
                    composer=p["composer"],
                    genre=p["genre"],
                    path=p["path"],
                    byteTime=p["sec"],
                    sideloaded=p["sideloaded"],
                    description=p["comment"],
                    cover_art=p["cover_art"],
                    unlocked=p["unlocked"],
                )
                self.automaticList.append(p["class"])


ost_song_assign = OSTPlayerSongAssign()


class OSTPlayerMain:
    def __init__(self):
        self.prevTrack = None

        if renpy.android:
            self.logdir = os.path.join(os.environ["ANDROID_PUBLIC"], "ost_log.txt")
        else:
            self.logdir = os.path.join(renpy.config.basedir, "ost_log.txt")

        if os.path.exists(self.logdir):
            os.remove(self.logdir)

        self.ost_log_start()

        logging.info(
            'Making the "track" folder in ' + gamedir + " if it's not present."
        )
        try:
            os.mkdir(os.path.join(gamedir, "track"))
        except:
            pass
        logging.info(
            'Making the "covers" folder in ' + gamedir + "/track if it's not present."
        )
        try:
            os.mkdir(os.path.join(gamedir, "track", "covers"))
        except:
            pass

        logging.info("Clearing the covers folder of cover art.")
        for x in os.listdir(os.path.join(gamedir, "track", "covers")):
            os.remove(os.path.join(gamedir, "track", "covers", x))

        ost_song_assign.scan_song()

    def get_music_channel_info(self):
        logging.info("Getting music playing from music channel.")
        self.prevTrack = music.get_playing(channel="music") or self.prevTrack
        logging.info('Obtained music status from "renpy.audio.music".')

        if not self.prevTrack:
            logging.warning('No music was found via "renpy.audio.music".')
            self.prevTrack = False

    def ost_log_start(self):
        logging.basicConfig(filename=self.logdir, level=logging.DEBUG)
        logging.info("Started logging this OST-Player session for errors.")

    def ost_log_stop(self):
        logging.info("Stopped logging this OST-Player session for errors.")
        logging.shutdown()

    def ost_start(self):
        if renpy.config.developer:
            ost_song_assign.rpa_mapping()
        else:
            ost_song_assign.rpa_load_mapping()
        self.get_music_channel_info()
        ost_song_assign.resort()

    def ost_quit(self):
        ost_controls.check_paused_state()
        self.ost_log_stop()


ost_main = OSTPlayerMain()
gamePreference.set_mute("music", False)
ost_monitor = ExternalOSTMonitor()

# Backwards Compatability
manualDefineList = ost_song_assign.manualList
