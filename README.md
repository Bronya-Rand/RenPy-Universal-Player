# Ren'Py Universal Player (Ren'Py UOST-Player)
[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K22K8SU)

<u>Current Version:</u> [**1.0**](https://github.com/GanstaKingofSA/DDLC-OSTPlayer/releases/latest)

Ren'Py-Universal-Player or (Ren'Py UOST-Player) is a enhanced music room for Ren'Py projects that allows users to play tracks outside the game's story along with sideloaded songs. 

## Features
* MP3 and OGG Playback from a folder or inside a RPA
  > You will need to enable Developer Mode in order to make the metadata of songs in the track RPA folder generate for distribution.
* Metadata support for tracks
* Music Player controls
* Dynamic Font Scaling for Titles (some-what)
* Sorting support
* Based off the Ren'Py auto-generated template

## What do I need to run this?
1. A new Ren'Py project.
   > You can also place the added code in `screens.rpy` and add the `images` and `python-packages` folder to your projects' *game* folder.
2. The recent version of [Ren'Py UOST-Player](https://github.com/GanstaKingofSA/RenPy-Universal-Player/releases).

## How do I install this?

1. Drop all the contents in this ZIP file to your projects' *game* folder.
2. Open `options.rpy` and add this line after line `160` under the *init python:* block.
   ```py
   build.classify("game/RPASongMetadata.json", "all")
   ```
3. **(Optional)** Add some music to the `track` folder.
4. Run your project and enter the Music Room!

## What can I customize in Ren'Py UOST-Player?
Pretty much anything. This is based off the auto-generated Ren'Py template so everything is good for you to use as-is.
> If you plan to change the `track` folder name to something else, do let people know about this change if they want to add tracks to your game with your projects' music files.

## How do I manually define a song?
`manualtracks.rpy` has a small template to define songs manually if you need to do so. You have the following options to define these tracks.
```
name | Name of Track
full_name | Full Name of Track
path | Path to the file from the game folder
priority | Priortization of track on the list.
author | Artist
description | Track description, comments, etc
cover_art | Path to the track's cover art (JPG/PNG Only)
```

## How do I priortize a song or make a song the first one?
Set organizePriority to True and set the song priority by a value. 0 is the highest priority you can make a song be while 1, 2, etc. will be prioritzed lower in the list. i.e. `0 > 1 > 2 > ...`

## How do I organize the list alphabetically?
Turn on the A-Z Priority in the music player when playing a song or default it on, by setting `organizeAZ` to True.

## Can the organizations work together?
Yes.

## Why is there files in the `python-packages` folder?

These handles handle the functions of the music room player and the metadata of songs sideloaded or those that have metadata in the game.

`ost.py` - Music Room Code

`tinytag.py` - Track Metadata Code

## How do I add metadata info?
Right-click your song, Select Properties -> Details, and fill the blank boxes you can.
Alternatively, use [MusicBee](https://www.getmusicbee.com/) or a similar music player, or [MusicBrainz Picard](https://picard.musicbrainz.org/) and find your song.

- For MusicBee: Right-Click your song within the player, select _Edit_ and edit away the info you want, then click _Apply_ then _OK_.
- For MusicBrainz Picard: Add your song to Picard, select it, right-click the rectangle box that has 3 columns, select _Add New Tag_, select the tags you want to add like _Title_, _Artist_, _Comment_, _Album_, etc. There should be a blank box in the box area below, double-click it and edit away the info you want to add, then click _Save_ and press the _Save_ button near _Info_.

## Why did you do this?
I wanted to expand the original project I made with this code ([DDLC-OSTPlayer](https://github.com/GanstaKingofSA/DDLC-OSTPlayer)) to everyone else in Ren'Py. Originally made to see RWBY songs play within the Ren'Py engine. (Yang _:P_)