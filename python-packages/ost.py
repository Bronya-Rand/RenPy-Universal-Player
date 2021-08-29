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

import random
import re
import os
import json
import renpy
import pygame_sdl2
from tinytag import TinyTag
from renpy.text.text import Text
from renpy.display.im import image
import renpy.audio.music as music
import renpy.display.behavior as displayBehavior

# Creation of Music Room and Code Setup
version = 1.6
music.register_channel("music_room", mixer="music_room_mixer", loop=False)
if renpy.windows:
    gamedir = renpy.config.gamedir.replace("\\", "/")
elif renpy.android:
    try: os.mkdir(os.path.join(os.environ["ANDROID_PUBLIC"], "game"))
    except: pass
    gamedir = os.path.join(os.environ["ANDROID_PUBLIC"], "game")
else:
    gamedir = renpy.config.gamedir


# Lists for holding media types
autoDefineList = []
manualDefineList = []
soundtracks = []
file_types = ('.mp3', '.ogg', '.opus', '.wav')

# Stores soundtrack in progress
game_soundtrack = False

# Stores positions of track/volume/default priority
time_position = 0.0 
time_duration = 3.0
old_volume = 0.0
priorityScan = 2
scale = 1.0

# Stores paused track/player controls
game_soundtrack_pause = False
prevTrack = False
randomSong = False
loopSong = False
organizeAZ = False
organizePriority = True
pausedstate = False

random.seed()

class soundtrack:
    '''
    Class responsible to define songs to the music player.
    '''

    def __init__(self, name="", path="", priority=2, author="", byteTime=False, 
                description="", cover_art=False, unlocked=True):
        self.name = name
        self.path = path
        self.priority = priority
        self.author = author
        self.byteTime = byteTime
        self.description = description
        if not cover_art:
            self.cover_art = "images/music_room/nocover.png"
        else:
            self.cover_art = cover_art
        self.unlocked = unlocked

@renpy.exports.pure
class AdjustableAudioPositionValue(renpy.ui.BarValue):
    '''
    Class that replicates a music progress bar in Ren'Py.
    '''

    def __init__(self, channel='music_room', update_interval=0.0):
        self.channel = channel
        self.update_interval = update_interval
        self.adjustment = None
        self._hovered = False

    def get_pos_duration(self):
        if not music.is_playing(self.channel):
            pos = time_position
        else:
            pos = music.get_pos(self.channel) or 0.0
        duration = time_duration

        return pos, duration

    def get_song_options_status(self):
        return loopSong, randomSong

    def get_adjustment(self):
        pos, duration = self.get_pos_duration()
        self.adjustment = renpy.ui.adjustment(value=pos, range=duration, 
                                            changed=self.set_pos, adjustable=True)

        return self.adjustment

    def hovered(self):
        self._hovered = True

    def unhovered(self):
        self._hovered = False

    def set_pos(self, value):
        loopThis = self.get_song_options_status()
        if (self._hovered and pygame_sdl2.mouse.get_pressed()[0]):
            music.play("<from {}>".format(value) + game_soundtrack.path, 
                    self.channel)
            if loopThis:
                music.queue(game_soundtrack.path, self.channel, loop=True)

    def periodic(self, st):
        pos, duration = self.get_pos_duration()
        loopThis, doRandom = self.get_song_options_status()

        if pos and pos <= duration:
            self.adjustment.set_range(duration)
            self.adjustment.change(pos)
                    
        if pos > duration - 0.20:
            if loopThis:
                music.play(game_soundtrack.path, self.channel, loop=True)
            elif doRandom:
                random_song()
            else:
                next_track()

        return self.update_interval 

if renpy.config.screen_width != 1280:
    scale = renpy.config.screen_width / 1280.0
else:
    scale = 1.0

def music_pos(style_name, st, at):
    '''
    Returns the track position to Ren'Py.
    '''

    global time_position

    if music.get_pos(channel='music_room') is not None:
        time_position = music.get_pos(channel='music_room')

    readableTime = convert_time(time_position)
    d = Text(readableTime, style=style_name) 
    return d, 0.20

def music_dur(style_name, st, at):
    '''
    Returns the track duration to Ren'Py.
    '''

    global time_duration

    if game_soundtrack.byteTime:
        time_duration = game_soundtrack.byteTime
    else:
        time_duration = music.get_duration(
                                        channel='music_room') or time_duration

    readableDuration = convert_time(time_duration)
    d = Text(readableDuration, style=style_name)     
    return d, 0.20

def dynamic_title_text(style_name, st, at):
    '''
    Returns a resized song title text to Ren'Py.
    '''

    title = len(game_soundtrack.name)

    if title <= 21:
        songNameSize = int(37 * scale) 
    elif title <= 28:
        songNameSize = int(29 * scale)
    else:
        songNameSize = int(23 * scale)

    d = Text(game_soundtrack.name, style=style_name, substitute=False,
            size=songNameSize)

    return d, 0.20

def dynamic_author_text(style_name, st, at):
    '''
    Returns a resized song artist text to Ren'Py.
    '''

    author = len(game_soundtrack.author)

    if author <= 32:
        authorNameSize = int(25 * scale)
    elif author <= 48:
        authorNameSize = int(23 * scale)
    else:
        authorNameSize = int(21 * scale)

    d = Text(game_soundtrack.author, style=style_name, substitute=False,
            size=authorNameSize)

    return d, 0.20

def refresh_cover_data(st, at):
    '''
    Returns the song cover art to Ren'Py.
    '''

    d = image(game_soundtrack.cover_art)
    return d, 0.20

def dynamic_description_text(style_name, st, at):
    '''
    Returns a resized song album/comment to Ren'Py.
    '''

    desc = len(game_soundtrack.description)

    if desc <= 32:
        descSize = int(25 * scale)
    elif desc <= 48:
        descSize = int(23 * scale)
    else:
        descSize = int(21 * scale)

    d = Text(game_soundtrack.description, style=style_name, substitute=False,
            size=descSize)
    return d, 0.20

def auto_play_pause_button(st, at):
    '''
    Returns either a play/pause button to Ren'Py based off song play status.
    '''

    if music.is_playing(channel='music_room'):
        if pausedstate:
            d = renpy.display.behavior.ImageButton("images/music_room/pause.png")
        else:
            d = renpy.display.behavior.ImageButton("images/music_room/pause.png", 
                                                action=current_music_pause)
    else:
        d = displayBehavior.ImageButton("images/music_room/play.png", 
                                        action=current_music_play)
    return d, 0.20

def rpa_mapping_detection(style_name, st, at):
    '''
    Returns a warning message to the player if it can't find the RPA cache
    JSON file in the game folder.
    '''

    try: 
        renpy.exports.file("RPASongMetadata.json")
        return Text("", size=23), 0.0
    except:
        return Text("{b}Warning:{/b} The RPA metadata file hasn't been generated. Songs in the {i}track{/i} folder that are archived into a RPA won't work without it. Set {i}config.developer{/i} to {i}True{/i} in order to generate this file.", style=style_name, size=20), 0.0

def convert_time(x):
    '''
    Converts track position and duration to human-readable time.
    '''

    hour = ""

    if int (x / 3600) > 0:
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

def current_music_pause():
    '''
    Pauses the current song playing.
    '''

    global game_soundtrack_pause, pausedstate
    pausedstate = True

    if not music.is_playing(channel='music_room'):
        return
    else:
        soundtrack_position = music.get_pos(channel = 'music_room') + 1.6

    if soundtrack_position is not None:
        game_soundtrack_pause = ("<from " + str(soundtrack_position) + ">" 
                                + game_soundtrack.path)

    music.stop(channel='music_room',fadeout=2.0)

def current_music_play():
    '''
    Plays either the paused state of the current song or a new song to the
    player.
    '''

    global pausedstate
    pausedstate = False

    if not game_soundtrack_pause:
        music.play(game_soundtrack.path, channel = 'music_room', fadein=2.0)
    else:
        music.play(game_soundtrack_pause, channel = 'music_room', fadein=2.0)
    
def current_music_forward():
    '''
    Fast-forwards the song by 5 seconds or advances to the next song.
    '''

    global game_soundtrack_pause

    if music.get_pos(channel = 'music_room') is None:
        soundtrack_position = time_position + 5
    else:
        soundtrack_position = music.get_pos(channel = 'music_room') + 5

    if soundtrack_position >= time_duration: 
        game_soundtrack_pause = False
        if randomSong:
            random_song()
        else:
            next_track()
    else:
        game_soundtrack_pause = ("<from " + str(soundtrack_position) + ">" 
                                + game_soundtrack.path)

        music.play(game_soundtrack_pause, channel = 'music_room')

def current_music_backward():
    '''
    Rewinds the song by 5 seconds or advances to the next song behind it.
    '''

    global game_soundtrack_pause

    if music.get_pos(channel = 'music_room') is None:
        soundtrack_position = time_position - 5
    else:
        soundtrack_position = music.get_pos(channel = 'music_room') - 5

    if soundtrack_position <= 0.0:
        game_soundtrack_pause = False
        next_track(True)
    else:
        game_soundtrack_pause = ("<from " + str(soundtrack_position) + ">" 
                                + game_soundtrack.path)
            
        music.play(game_soundtrack_pause, channel = 'music_room')

def next_track(back=False):
    '''
    Advances to the next song ahead or behind to the player or the start/end.
    '''

    global game_soundtrack

    for index, item in enumerate(soundtracks):
        if (game_soundtrack.description == item.description 
            and game_soundtrack.name == item.name):
            try:
                if back:
                    game_soundtrack = soundtracks[index-1]
                else:
                    game_soundtrack = soundtracks[index+1]
            except:
                if back:
                    game_soundtrack = soundtracks[-1]
                else:
                    game_soundtrack = soundtracks[0]
            break

    if game_soundtrack != False:
        music.play(game_soundtrack.path, channel='music_room', loop=loopSong)

def random_song():
    '''
    Advances to the next song with pure randomness.
    '''

    global game_soundtrack

    unique = 1
    if soundtracks[-1].path == game_soundtrack.path:
        pass
    else:
        while unique != 0:
            a = random.randrange(0, len(soundtracks)-1)
            if game_soundtrack != soundtracks[a]:
                unique = 0
                game_soundtrack = soundtracks[a]

    if game_soundtrack != False:
        music.play(game_soundtrack.path, channel='music_room', loop=loopSong)

def mute_player():
    '''
    Mutes the music player.
    '''

    global old_volume

    if renpy.game.preferences.get_volume("music_room_mixer") != 0.0:
        old_volume = renpy.game.preferences.get_volume("music_room_mixer")
        renpy.game.preferences.set_volume("music_room_mixer", 0.0)
    else:
        if old_volume == 0.0:
            renpy.game.preferences.set_volume("music_room_mixer", 0.5)
        else:
            renpy.game.preferences.set_volume("music_room_mixer", old_volume)

def refresh_list():
    '''
    Refreshes the song list.
    '''

    scan_song() 
    if renpy.config.developer or renpy.config.developer == "auto":
        rpa_mapping()
    resort()

def resort():
    '''
    Adds songs to the song list and resorts them by priority or A-Z.
    '''

    global soundtracks
    soundtracks = []

    for obj in autoDefineList:
        if obj.unlocked:
            soundtracks.append(obj)
    for obj in manualDefineList:
        if obj.unlocked:
            soundtracks.append(obj)

    if organizeAZ:
        soundtracks = sorted(soundtracks, key=lambda soundtracks: 
                            soundtracks.name)
    if organizePriority:
        soundtracks = sorted(soundtracks, key=lambda soundtracks: 
                            soundtracks.priority)

def get_info(path, tags):   
    '''
    Gets the info of the tracks in the track info for defining.
    '''

    sec = tags.duration
    try:
        image_data = tags.get_image()
        
        with open(os.path.join(gamedir, "python-packages/binaries.txt"), "rb") as a:
            lines = a.readlines()

        jpgbytes = bytes("\\xff\\xd8\\xff")
        utfbytes = bytes("o\\x00v\\x00e\\x00r\\x00\\x00\\x00\\x89PNG\\r\\n")

        jpgmatch = re.search(jpgbytes, image_data) 
        utfmatch = re.search(utfbytes, image_data) 

        if jpgmatch:
            cover_formats=".jpg"
        else:
            cover_formats=".png"

            if utfmatch: # addresses itunes cover descriptor fixes
                image_data = re.sub(utfbytes, lines[2], image_data)

        coverAlbum = re.sub(r"\[|\]|/|:|\?",'', tags.album)
                
        with open(os.path.join(gamedir, 'track/covers', coverAlbum + cover_formats), 'wb') as f:
            f.write(image_data)

        art = coverAlbum + cover_formats
        return tags.title, tags.artist, sec, art, tags.album, tags.comment
    except TypeError:
        return tags.title, tags.artist, sec, None, tags.album, tags.comment

def scan_song():
    '''
    Scans the track folder for songs and defines them to the player.
    '''

    global autoDefineList

    exists = []
    for x in autoDefineList[:]:
        try:
            renpy.exports.file(x.path)
            exists.append(x.path)    
        except:
            autoDefineList.remove(x)
        
    for x in os.listdir(gamedir + '/track'):
        if x.endswith((file_types)) and "track/" + x not in exists:
            path = "track/" + x
            tags = TinyTag.get(gamedir + "/" + path, image=True) 
            title, artist, sec, altAlbum, album, comment = get_info(path, tags)
            def_song(title, artist, path, priorityScan, sec, altAlbum, album,
                    comment, True)

def def_song(title, artist, path, priority, sec, altAlbum, album, comment,
            unlocked=True):
    '''
    Defines the song to the music player list.
    '''

    if title is None:
        title = str(path.replace("track/", "")).capitalize()
    if artist is None or artist == "":
        artist = "Unknown Artist"
    if altAlbum is None or altAlbum == "":
        altAlbum = "images/music_room/nocover.png" 
    else:
        altAlbum = "track/covers/"+altAlbum
        try:
            renpy.exports.image_size(altAlbum)
        except:
            altAlbum = "images/music_room/nocover.png" 
    if album is None or album == "":
        description = "Non-Metadata Song"
    else:
        if comment is None: 
            description = album 
        else:
            description = album + '\n' + comment 

    class_name = re.sub(r"-|'| ", "_", title)

    class_name = soundtrack(
        name = title,
        author = artist,
        path = path,
        byteTime = sec,
        priority = priority,
        description = description,
        cover_art = altAlbum,
        unlocked = unlocked
    )
    autoDefineList.append(class_name)

def rpa_mapping():
    '''
    Maps songs in the track folder to a JSON for APK/RPA packing.
    '''

    data = []
    try: os.remove(os.path.join(gamedir, "RPASongMetadata.json"))
    except: pass
    for y in autoDefineList:
        data.append ({
            "class": re.sub(r"-|'| ", "_", y.name),
            "title": y.name,
            "artist": y.author,
            "path": y.path,
            "sec": y.byteTime,
            "altAlbum": y.cover_art,
            "description": y.description,
            "unlocked": y.unlocked,
        })
    with open(gamedir + "/RPASongMetadata.json", "a") as f:
        json.dump(data, f)

def rpa_load_mapping():
    '''
    Loads the JSON mapping and defines it to the player.
    '''

    try: renpy.exports.file("RPASongMetadata.json")
    except: return

    with renpy.exports.file("RPASongMetadata.json") as f:
        data = json.load(f)

    for p in data:
        title, artist, path, sec, altAlbum, description, unlocked = (p['title'], 
                                                                    p['artist'], 
                                                                    p["path"], 
                                                                    p["sec"], 
                                                                    p["altAlbum"], 
                                                                    p["description"], 
                                                                    p["unlocked"])

        p['class'] = soundtrack(
            name = title,
            author = artist,
            path = path,
            byteTime = sec,
            priority = priorityScan,
            description = description,
            cover_art = altAlbum,
            unlocked = unlocked
        )
        autoDefineList.append(p['class'])

def get_music_channel_info():
    '''
    Gets the info of the music channel for exiting purposes.
    '''

    global prevTrack

    prevTrack = music.get_playing(channel='music')
    if prevTrack is None:
        prevTrack = False

def check_paused_state():
    '''
    Checks if the music player is in a paused state for exiting purposes.
    '''

    if not game_soundtrack or pausedstate:
        return
    else:
        current_music_pause()

try: os.mkdir(gamedir + "/track")
except: pass
try: os.mkdir(gamedir + "/track/covers")
except: pass

for x in os.listdir(gamedir + '/track/covers'):
    os.remove(gamedir + '/track/covers/' + x)

scan_song()
if renpy.config.developer or renpy.config.developer == "auto":
    rpa_mapping()
else:
    rpa_load_mapping()
resort()