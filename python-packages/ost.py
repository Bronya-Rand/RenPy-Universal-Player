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

# Pardon any mess within this PY file.

import time, random, re, glob, os, json
import renpy, pygame_sdl2
from tinytag import TinyTag
from renpy.text.text import Text
from renpy.display.im import image
import renpy.audio.music as music
import renpy.display.behavior as displayBehavior

# Creation of Music Room and Code Setup
version = 1.2
music.register_channel("music_room", mixer="music_room_mixer", loop=False)
if renpy.windows:
    gamedir = renpy.config.gamedir.replace("\\", "/")
else:
    gamedir = renpy.config.gamedir


# Lists for holding media types
renpyFileList = renpy.exports.list_files(common=False)
mp3List = []
oggList = []
playableMP3List = []
playableOGGList = []
manualDefineList = []
soundtracks = []

# Stores soundtrack in progress
game_soundtrack = False

# Stores positions of track/volume/default priority
time_position = 0.0 # 
time_duration = 3.0
soundtrack_position = 0.0
soundtrack_duration = 0.0
old_volume = 0.0
priorityScan = 2
scale = 1.0

# Stores paused track/player controls
game_soundtrack_pause = False
music_muted = False
randomSong = False
loopSong = False
organizeAZ = False
organizePriority = True

class soundtrack:
    def __init__(self, name = "", full_name = "", path = "", priority = 2, author = False, byteTime = False, description = False, cover_art = False):
        #name that will be displayed
        self.name = name
        #name that will be displayed in 
        self.full_name = full_name
        #path to the music file
        self.path = path
        #priority of the list
        self.priority = priority
        #author names
        self.author = author
        # byte time duration of song (backup for some songs)
        self.byteTime = byteTime
        #description of soundtrack
        self.description = description
        #path to the cover art image
        if cover_art == False:
            self.cover_art = "images/music_room/nocover.png"
        else:
            self.cover_art = cover_art

# Adjustable Bar for track scrolling
@renpy.exports.pure
class AdjustableAudioPositionValue(renpy.ui.BarValue):
    def __init__(self, channel='music_room', update_interval=0.0):
        self.channel = channel
        self.update_interval = update_interval
        self.adjustment = None
        self._hovered = False

    def get_pos_duration(self):
            
        pos = music.get_pos(self.channel) or 0.0
        duration = music.get_duration(self.channel) or time_duration
        if game_soundtrack.byteTime:
            duration = game_soundtrack.byteTime

        return pos, duration

    def get_song_options_status(self):
        return loopSong, randomSong

    def get_adjustment(self):
        pos, duration = self.get_pos_duration()
        self.adjustment = renpy.ui.adjustment(value=pos, range=duration, changed=self.set_pos, adjustable=True)
        return self.adjustment

    def hovered(self):
        self._hovered = True

    def unhovered(self):
        self._hovered = False

    def set_pos(self, value):
        loopThis = self.get_song_options_status()
        if (self._hovered and pygame_sdl2.mouse.get_pressed()[0]):
            music.play("<from {}>".format(value) + game_soundtrack.path, self.channel)
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

# scales positions/spacing if not 1280x720
if renpy.config.screen_width != 1280:
    scale = renpy.config.screen_width / 1280.0
else:
    scale = 1.0

def music_pos(style_name, st, at):
    global time_position
    global time_duration

    if game_soundtrack == False: # failsafe to when user quits out of OST
        return Text("", style=style_name, size=40), 0.0

    if music.is_playing(channel='music_room'): # checks if music is playing
        time_position = music.get_pos(channel='music_room') or time_position # grabs position of song
    else:
        if time_position > time_duration - 0.20:
            time_position = 0.0

    readableTime = convert_time(time_position) # converts to readable time for display
    d = Text(readableTime, style=style_name) 
    return d, 0.20

def music_dur(style_name, st, at):
    global time_duration

    if game_soundtrack == False: # failsafe to when user quits out of OST
        return Text("", style=style_name, size=40), 0.0

    if music.is_playing(channel='music_room'): # checks if music is playing
        time_duration = music.get_duration(channel='music_room') or time_duration # sets duration to what renpy thinks it lasts
    if game_soundtrack.byteTime:
        time_duration = game_soundtrack.byteTime

    readableDuration = convert_time(time_duration) # converts to readable time for display
    d = Text(readableDuration, style=style_name)     
    return d, 0.20

def dynamic_title_text(style_name, st, at):
    if game_soundtrack == False: # failsafe to when user quits out of OST
        return Text("Exiting...", size=int(36 * scale)), 0.0

    title = len(game_soundtrack.full_name) # grabs the length of the name and artist 

    if title <= 21: # checks length against set var checks (can be changed) 
        songNameSize = int(37 * scale) 
    elif title <= 28:
        songNameSize = int(29 * scale)
    else:
        songNameSize = int(23 * scale)

    d = Text(game_soundtrack.full_name, style=style_name, size=songNameSize)
    return d, 0.20

def dynamic_author_text(style_name, st, at):
    if game_soundtrack == False: # failsafe to when user quits out of OST
        return Text("", style=style_name, size=gui.text_size), 0.0

    author = len(game_soundtrack.author)

    if author <= 32:
        authorNameSize = int(25 * scale)
    elif author <= 48:
        authorNameSize = int(23 * scale)
    else:
        authorNameSize = int(21 * scale)

    d = Text(game_soundtrack.author, style=style_name, size=authorNameSize)
    return d, 0.20

def refresh_cover_data(st, at):
    if game_soundtrack == False: # failsafe to when user quits out of OST
        return Text("", size=gui.text_size), 0.0

    d = image(game_soundtrack.cover_art)
    return d, 0.20

# displays current music description
def dynamic_description_text(style_name, st, at):
    if game_soundtrack == False: 
        return Text("", size=23), 0.0

    desc = len(game_soundtrack.description)

    if desc <= 32:
        descSize = int(25 * scale)
    elif desc <= 48:
        descSize = int(23 * scale)
    else:
        descSize = int(21 * scale)

    d = Text(game_soundtrack.description, style=style_name, substitute=False, size=descSize) # false sub for albums with brackets/etc
    return d, 0.20

def auto_play_pause_button(st, at):
    if game_soundtrack == False: 
        return Text("", size=23), 0.0
    
    if music.is_playing(channel='music_room'):
        d = displayBehavior.ImageButton("images/music_room/pause.png", action=current_music_pause)
    else:
        d = displayBehavior.ImageButton("images/music_room/play.png", action=current_music_play)
    return d, 0.20

def rpa_mapping_detection(style_name, st, at):
    try: 
        renpy.exports.file("RPASongMetadata.json")
        return Text("", size=23), 0.0
    except:
        return Text("{b}Warning:{/b} The RPA metadata file hasn't been generated. Songs in the {i}track{/i} folder that are archived into a RPA won't work without it. Set {i}config.developer{/i} to {i}True{/i} in order to generate this file.", style=style_name, size=20), 0.0

# Converts the time to a readable time
def convert_time(x):
    readableTime = time.gmtime(float(x))
    res = time.strftime("%M:%S",readableTime)
    return res

# Pauses the song and saves it's pause spot
def current_music_pause():
    global soundtrack_position, soundtrack_duration, game_soundtrack_pause

    soundtrack_position = music.get_pos(channel = 'music_room') + 1.6
    soundtrack_duration = music.get_duration(channel = 'music_room')

    if soundtrack_position is not None:
        game_soundtrack_pause = "<from "+str(soundtrack_position) +">"+game_soundtrack.path

    music.stop(channel='music_room',fadeout=2.0)

# Starts the song from it's pause spot
def current_music_play():

    if game_soundtrack_pause is False:
        music.play(game_soundtrack.path, channel = 'music_room', fadein=2.0)
    else:
        music.play(game_soundtrack_pause, channel = 'music_room', fadein=2.0)
    
# Forwards track by 5 seconds
def current_music_forward():
    global soundtrack_position, soundtrack_duration, game_soundtrack_pause, time_duration

    if music.get_pos(channel = 'music_room') is None:
        soundtrack_position = soundtrack_position + 5
    else:
        soundtrack_position = music.get_pos(channel = 'music_room') + 5

    soundtrack_duration = music.get_duration(channel = 'music_room') or time_duration #! to handle latin duration issues
    if game_soundtrack.byteTime:
        time_duration = game_soundtrack.byteTime

    if soundtrack_position >= soundtrack_duration: 
        soundtrack_position = 0.0
        game_soundtrack_pause = False
        if randomSong:
            random_song()
        else:
            next_track()
    else:
        game_soundtrack_pause = "<from "+str(soundtrack_position) +">"+game_soundtrack.path

        music.play(game_soundtrack_pause, channel = 'music_room')

# Rewinds track by 5 seconds
def current_music_backward():
    global soundtrack_position, game_soundtrack_pause

    if music.get_pos(channel = 'music_room') is None:
        soundtrack_position = soundtrack_position - 5
    else:
        soundtrack_position = music.get_pos(channel = 'music_room') - 5

    if soundtrack_position <= 0.0:
        soundtrack_position = 0.0
        game_soundtrack_pause = False
        next_track(back=True)
    else:
        game_soundtrack_pause = "<from "+str(soundtrack_position) +">"+game_soundtrack.path
            
        music.play(game_soundtrack_pause, channel = 'music_room')

# Advances to next track or track behind the current track
def next_track(back=False):
    global game_soundtrack

    for st in range(len(soundtracks)):
        if game_soundtrack == soundtracks[st] or game_soundtrack.description == soundtracks[st].description and game_soundtrack.name == soundtracks[st].name:
            try:
                if back:
                    game_soundtrack = soundtracks[st-1]
                else:
                    game_soundtrack = soundtracks[st+1]
            except:
                if back:
                    game_soundtrack = soundtracks[len(soundtracks)-1]
                else:
                    game_soundtrack = soundtracks[0]
            break

    if game_soundtrack != False:
        music.play(game_soundtrack.path, channel='music_room', loop=loopSong)

# Advances to a random track
def random_song():
    global game_soundtrack

    random.seed()
    unique = 1
    while unique != 0:
        a = random.randrange(0,len(soundtracks)-1)
        if game_soundtrack != soundtracks[a]:
            unique = 0
            game_soundtrack = soundtracks[a]

    if game_soundtrack != False:
        music.play(game_soundtrack.path, channel='music_room', loop=loopSong)

# Mutes audio from the player
def mute_player():
    global old_volume

    if renpy.game.preferences.get_volume("music_room_mixer") != 0.0:
        old_volume = renpy.game.preferences.get_volume("music_room_mixer")
        renpy.game.preferences.set_volume("music_room_mixer", 0.0)
    else:
        renpy.game.preferences.set_volume("music_room_mixer", old_volume)

def refresh_list():
    scan_mp3() # scans mp3
    scan_ogg() # scans ogg
    resort()

def resort():
    global soundtracks
    soundtracks = [] # resets soundtrack list
    for obj in playableMP3List:
        soundtracks.append(obj)
    for obj in playableOGGList:
        soundtracks.append(obj)
    for obj in manualDefineList:
        soundtracks.append(obj)
    if organizeAZ:
        soundtracks = sorted(soundtracks, key=lambda soundtracks: soundtracks.name)
    if organizePriority:
        soundtracks = sorted(soundtracks, key=lambda soundtracks: soundtracks.priority)

# grabs info from the mp3/ogg (and cover if available)
def get_info(path, tags):   
    sec = tags.duration
    try:
        image_data = tags.get_image()
        jpgregex = r"\\xFF\\xD8\\xFF"

        match = re.search(jpgregex, image_data) # searches the image data in the file for a JPG pattern
        if match:
            cover_formats=".jpg" # set image format to jpg
        else:
            cover_formats=".png" # set image format to png
        altAlbum = re.sub(r"\[|\]|/|:|\?",'', tags.album) # converts problematic symbols to nothing i.e Emotion [Deluxe] to Emotion Deluxe
                
        with open(gamedir + '/track/covers/' + altAlbum + cover_formats, 'wb') as f: # writes image data with proper extension to destination
            f.write(image_data)
        return tags.title, tags.artist, sec, altAlbum, cover_formats, tags.album, tags.comment
    except TypeError:
        return tags.title, tags.artist, sec, None, None, tags.album, tags.comment

#Scans MP3 tracks to the OST Player
def scan_mp3():
    global mp3List, playableMP3List

    if glob.glob(gamedir + '/track/*.mp3'): 
        if len(mp3List) != 0: 
            for x in reversed(range(len(playableMP3List))): 
                playableMP3List.pop(x)

            mp3List = [gamedir + "/track\\" + x for x in os.listdir(gamedir + '/track') if x.endswith(".mp3")] 
            playableMP3List = [gamedir + "/track\\" + x for x in os.listdir(gamedir + '/track') if x.endswith(".mp3")]
 
        else:

            mp3List = glob.glob(gamedir + '/track/*.mp3') 
            playableMP3List = glob.glob(gamedir + '/track/*.mp3')

        mp3ListLength = len(playableMP3List) 

        for y in range(mp3ListLength):
            path = playableMP3List[y].replace("\\", "/") 
            tags = TinyTag.get(path, image=True) 
            title, artist, sec, altAlbum, cover_formats, album, comment = get_info(path, tags)
            def_mp3(title, artist, path, priorityScan, sec, altAlbum, cover_formats, y, album, comment)

# Scans OGG tracks to the OST Player
def scan_ogg():
    global oggList, playableOGGList

    if glob.glob(gamedir + '/track/*.ogg'): 

        if len(oggList) != 0:
            for x in reversed(range(len(playableOGGList))): 
                playableOGGList.pop(x)

            oggList = [gamedir + "/track\\" + x for x in os.listdir(gamedir + '/track') if x.endswith(".ogg")] 
            playableOGGList = [gamedir + "/track\\" + x for x in os.listdir(gamedir + '/track') if x.endswith(".ogg")]

        else:
            oggList = glob.glob(gamedir + '/track/*.ogg') 
            playableOGGList = glob.glob(gamedir + '/track/*.ogg')

        oggListLength = len(playableOGGList)

        for y in range(oggListLength):
            path = playableOGGList[y].replace("\\", "/")
            tags = TinyTag.get(path, image=True) 
            title, artist, sec, altAlbum, cover_formats, album, comment = get_info(path, tags) 
            def_ogg(title, artist, path, priorityScan, sec, altAlbum, cover_formats, y, album, comment) 

# Makes a OGG class for a OGG track to the OST Player
def def_ogg(title, artist, path, priority, sec, altAlbum, cover_formats, y, album, comment):
    if title is None: 
        title = "Unknown OGG File " + str(y)
    if artist is None: 
        artist = "Unknown Artist"
    if cover_formats is None: 
        description = "Non-Metadata OGG"
        cover_formats = "images/music_room/nocover.png" 
    else:
        cover_formats = "track/covers/"+altAlbum+cover_formats
        try:
            renpy.exports.image_size(cover_formats)
        except:
            cover_formats = "images/music_room/nocover.png" 
    if album is not None: 
        if comment is not None: 
            description = album + '\n' + comment 
        else:
            description = album 
    else:
        description = None 
        
    playableOGGList[y] = soundtrack(
        name = title,
        full_name = title,
        author = artist,
        path = path,
        byteTime = sec,
        priority = priorityScan,
        description = description,
        cover_art = cover_formats
    )

# Makes a MP3 class for a MP3 track to the OST Player
def def_mp3(title, artist, path, priority, sec, altAlbum, cover_formats, y, album, comment):
    if title is None:
        title = "Unknown MP3 File " + str(y)
    if artist is None:
        artist = "Unknown Artist"
    if cover_formats is None:
        description = "Non-Metadata MP3"
        cover_formats = "images/music_room/nocover.png" 
    else:
        cover_formats = "track/covers/"+altAlbum+cover_formats
        try:
            renpy.exports.image_size(cover_formats)
        except:
            cover_formats = "images/music_room/nocover.png" 
    if album is not None: 
        if comment is not None: 
            description = album + '\n' + comment 
        else:
            description = album
    else:
        description = None

    playableMP3List[y] = soundtrack(
        name = title,
        full_name = title,
        author = artist,
        path = path,
        byteTime = sec,
        priority = priorityScan,
        description = description,
        cover_art = cover_formats
    )

# maps track files in track folder before building the game
def rpa_mapping():
    data = []
    songTemp = ["track\\" + x for x in os.listdir(gamedir + '/track') if x.endswith(".mp3") or x.endswith(".ogg")]
    try: os.remove(gamedir + "/RPASongMetadata.json")
    except: pass
    for y in range(len(songTemp)):
        path = songTemp[y].replace("\\", "/") 
        tags = TinyTag.get(gamedir + "/" + path, image=True) 
        title, artist, sec, altAlbum, cover_formats, album, comment = get_info(path, tags) 
        data.append ({
            "class": re.sub(r"-|'| ", "_", title),
            "title": title,
            "artist": artist,
            "path": path,
            "sec": sec,
            "altAlbum": altAlbum,
            "cover_formats": cover_formats,
            "album": album,
            "comment": comment
        })
    with open(gamedir + "/RPASongMetadata.json", "a") as f:
        json.dump(data, f)

# loads the JSON file that holds RPA metadata
def rpa_load_mapping():
    try: renpy.exports.file("RPASongMetadata.json")
    except: return

    with renpy.exports.file("RPASongMetadata.json") as f:
        data = json.load(f)

    for p in data:
        title, artist, path, sec, altAlbum, cover_formats, album, comment = p['title'], p['artist'], p["path"], p["sec"], p["altAlbum"], p["cover_formats"], p["album"], p["comment"]
            
        if title is None: 
            title = "Unknown RPA Song " + str(p)
        if artist is None: 
            artist = "Unknown Artist"
        if cover_formats is None: 
            description = "Unknown RPA Song File"
            cover_formats = "images/music_room/nocover.png" 
        else:
            cover_formats = "track/covers/"+altAlbum+cover_formats
            try:
                renpy.exports.image_size(cover_formats)
            except:
                cover_formats = "images/music_room/nocover.png" 
        if album is not None: 
            if comment is not None: 
                description = album + '\n' + comment 
            else:
                description = album 
        else:
            description = None 

        p['class'] = soundtrack(
            name = title,
            full_name = title,
            author = artist,
            path = path,
            byteTime = sec,
            priority = priorityScan,
            description = description,
            cover_art = cover_formats
        )
        manualDefineList.append(p['class'])

try: os.mkdir(gamedir + "/track")
except: pass
try: os.mkdir(gamedir + "/track/covers")
except: pass

scan_mp3()
scan_ogg()

# checks for non-existant song covers for cleaning the covers directory
cover_list = ["track/covers/" + x for x in os.listdir(gamedir + '/track/covers')] 
for x in reversed(cover_list):
    for y in soundtracks:
        if y.cover_art == x:
            cover_list.pop(x)
for x in cover_list:
    os.remove(gamedir + "/" + x)

if renpy.config.developer:
    rpa_mapping()
else:
    rpa_load_mapping()
