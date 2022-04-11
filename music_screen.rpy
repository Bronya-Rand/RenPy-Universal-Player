
image readablePos = DynamicDisplayable(renpy.curry(ost.music_pos)(
                    "music_room_progress_text"))
image readableDur = DynamicDisplayable(renpy.curry(ost.music_dur)(
                    "music_room_duration_text")) 
image titleName = DynamicDisplayable(renpy.curry(ost.dynamic_title_text)(
                    "music_room_information_text")) 
image authorName = DynamicDisplayable(renpy.curry(ost.dynamic_author_text)(
                    "music_room_information_text")) 
image coverArt = DynamicDisplayable(ost.refresh_cover_data) 
image songDescription = DynamicDisplayable(renpy.curry(ost.dynamic_description_text)(
                    "music_room_information_text")) 
image rpa_map_warning = DynamicDisplayable(renpy.curry(ost.rpa_mapping_detection)(
                    "music_room_information_text"))
image playPauseButton = DynamicDisplayable(ost.auto_play_pause_button)

    
screen music_room():
    tag menu

    default bar_val = AdjustableAudioPositionValue()

    use game_menu(_("OST Player")):
        
        hbox at music_room_transition:
            style "music_room_hbox"
            
            if not ost_info.get_current_soundtrack():
                if persistent.listui:
                    xpos 0.35
                else:
                    xpos 0.3
                    ypos 0.4
                    spacing 10

                vbox:
                    text "No music is currently playing.":
                        color "#000"
                        outlines[]
                        size 24

                    if not persistent.listui:
                        textbutton "Music List":
                            text_style "navigation_button_text"
                            action [ShowMenu("music_list_type"), With(Dissolve(0.25))]
                            xalign 0.5
            else:
                if persistent.listui:
                    xpos 0.08
                    yalign -0.25

                    add "coverArt" at cover_art_resize(200)
                else:
                    xpos 0.06
                    yalign 0.25
                
                    add "coverArt" at cover_art_resize(350)

                vbox:
                    hbox:
                        if not persistent.listui:
                            yoffset 80
                        else:
                            yoffset -2

                        vbox:
                            if not persistent.listui:
                                xsize 520
                            else:
                                xsize 640

                            add "titleName"

                            add "authorName"

                            add "albumName"

                            hbox:
                                if not persistent.listui:
                                    yoffset 20
                                else:
                                    yoffset 10
                                spacing 15

                                imagebutton:
                                    idle "images/music_room/backward.png"
                                    hover "images/music_room/backwardHover.png"
                                    action [SensitiveIf(renpy.music.is_playing(channel='music_room')), Function(ost_controls.rewind_music)]

                                add "playPauseButton"

                                imagebutton:
                                    idle "images/music_room/forward.png"
                                    hover "images/music_room/forwardHover.png"
                                    action [SensitiveIf(renpy.music.is_playing(channel='music_room')), Function(ost_controls.forward_music)]

                                if persistent.listui:

                                    null width 15

                                    imagebutton:
                                        idle ConditionSwitch("ost_controls.loopSong", "images/music_room/replayOn.png", 
                                                            "True", "images/music_room/replay.png")
                                        hover "images/music_room/replayHover.png"
                                        action [ToggleVariable("ost_controls.loopSong", False, True)]
                                    imagebutton:
                                        idle ConditionSwitch("ost_controls.randomSong", "images/music_room/shuffleOn.png", 
                                                            "True", "images/music_room/shuffle.png")
                                        hover "images/music_room/shuffleHover.png"
                                        action [ToggleVariable("ost_controls.randomSong", False, True)]
                                    imagebutton:
                                        idle "images/music_room/info.png"
                                        hover "images/music_room/infoHover.png"
                                        action [ShowMenu("music_info"), With(Dissolve(0.25))]
                                    imagebutton:
                                        idle "images/music_room/settings.png"
                                        hover "images/music_room/settingsHover.png"
                                        action [ShowMenu("music_settings"), With(Dissolve(0.25))]
                                    imagebutton:
                                        idle "images/music_room/refreshList.png"
                                        hover "images/music_room/refreshHover.png"
                                        action [Function(ost_song_assign.refresh_list)]

                                    null width 15
                                    
                                    imagebutton:
                                        idle ConditionSwitch("preferences.get_volume(\"music_room_mixer\") == 0.0", 
                                            "images/music_room/volume.png", "True", 
                                            "images/music_room/volumeOn.png")
                                        hover ConditionSwitch("preferences.get_volume(\"music_room_mixer\") == 0.0", 
                                            "images/music_room/volumeHover.png", "True", 
                                            "images/music_room/volumeOnHover.png")
                                        action [Function(ost_controls.mute_player)]
                                        yoffset -8
                                    bar value Preference ("music_room_mixer volume") xsize 100 yoffset 8 xoffset -15
                                
                            if persistent.listui:
                                yoffset 20
                                vbox:
                                    hbox:
                                        bar:
                                            style "music_room_list_bar"

                                            value bar_val
                                            hovered bar_val.hovered
                                            unhovered bar_val.unhovered

                                    hbox:
                                        add "readablePos" 
                                        add "readableDur" xpos 550

                            if not persistent.listui:

                                hbox:
                                    yoffset 30
                                    spacing 15

                                    imagebutton:
                                        idle ConditionSwitch("ost_controls.loopSong", "images/music_room/replayOn.png", 
                                                            "True", "images/music_room/replay.png")
                                        hover "images/music_room/replayHover.png"
                                        action [ToggleVariable("ost_controls.loopSong", False, True)]
                                    imagebutton:
                                        idle ConditionSwitch("ost_controls.randomSong", "images/music_room/shuffleOn.png", 
                                                            "True", "images/music_room/shuffle.png")
                                        hover "images/music_room/shuffleHover.png"
                                        action [ToggleVariable("ost_controls.randomSong", False, True)]
                                    imagebutton:
                                        idle "images/music_room/info.png"
                                        hover "images/music_room/infoHover.png"
                                        action [ShowMenu("music_info"), With(Dissolve(0.25))]
                                    imagebutton:
                                        idle "images/music_room/musicwindow.png"
                                        hover "images/music_room/musicwindowHover.png"
                                        action [ShowMenu("music_list_type"), With(Dissolve(0.25))]
                                    imagebutton:
                                        idle "images/music_room/settings.png"
                                        hover "images/music_room/settingsHover.png"
                                        action [ShowMenu("music_settings"), With(Dissolve(0.25))]
                                    imagebutton:
                                        idle "images/music_room/refreshList.png"
                                        hover "images/music_room/refreshHover.png"
                                        action [Function(ost_song_assign.refresh_list)]
        
        if persistent.listui:   
            vpgrid id "mpl" at music_room_transition:
                rows len(soundtracks)
                cols 1
                mousewheel True
                draggable True

                xpos 0.03
                ypos 0.25
                xsize 950
                ysize 380
                spacing 5

                for st in soundtracks:
                    frame:
                        xsize 900
                        hbox:
                            imagebutton:
                                xsize 66 ysize 66
                                idle Transform(ConditionSwitch(ost_info.get_current_soundtrack() == st, If(ost_controls.pausedState, "images/music_room/music_list_pause.png", 
                                    "images/music_room/music_list_play.png"), "True", st.cover_art), size=(64, 64))
                                hover Transform(ConditionSwitch(ost_info.get_current_soundtrack() == st, If(ost_controls.pausedState, "images/music_room/music_list_play.png", 
                                    "images/music_room/music_list_pause.png"), "True", "images/music_room/music_list_play.png"), size=(64, 64))
                                action If(ost_info.get_current_soundtrack() == st, If(ost_controls.pausedState, Function(ost_controls.play_music), Function(ost_controls.pause_music)), 
                                    [SetVariable("ost_controls.pausedState", False), Function(ost_info.set_current_soundtrack, st), Play("music_room", st.path, loop=ost_controls.loopSong, 
                                    fadein=2.0)])

                            null width 15

                            vbox:
                                xsize 770
                                text "{b}[st.name]{/b}" style "music_room_alt_list_title_text"
                                text "[st.author]" style "music_room_alt_list_author_text"
                                text "[st.album]"  style "music_room_alt_list_author_text"
                            if st.byteTime:
                                vbox:
                                    yalign 0.5
                                    xpos -20
                                    text ost_info.convert_time(st.byteTime) style "music_room_alt_list_author_text"

        if not persistent.listui:
            hbox at music_room_transition:
                xalign 0.4
                yalign 0.85
            
                if ost_info.get_current_soundtrack():
                    vbox:
                        hbox:
                            bar:
                                style "music_room_bar"

                                value bar_val
                                hovered bar_val.hovered
                                unhovered bar_val.unhovered

                        hbox:
                            add "readablePos" 
                            add "readableDur" xpos 630
                          
                    imagebutton:
                        idle ConditionSwitch("preferences.get_volume(\"music_room_mixer\") == 0.0", 
                            "images/music_room/volume.png", "True", 
                            "images/music_room/volumeOn.png")
                        hover ConditionSwitch("preferences.get_volume(\"music_room_mixer\") == 0.0", 
                            "images/music_room/volumeHover.png", "True", 
                            "images/music_room/volumeOnHover.png")
                        action [Function(ost_controls.mute_player)]
                        yoffset -16 xoffset 10
                    bar value Preference ("music_room_mixer volume") xsize 100 xoffset 10

    text "Ren'Py Universal Player v[ostVersion]":
        xalign 1.0 yalign 1.0
        xoffset -10 yoffset -10
        style "main_menu_version"

    if not config.developer:
        hbox:
            xalign 0.5 yalign 0.98

            python:
                try:
                    renpy.file("RPASongMetadata.json")
                    file_found = True
                except: file_found = False
            
            if not file_found:
                imagebutton:
                    idle "images/music_room/osterror.png"
                    action Show("dialog", message="{b}Warning{/b}\nThe RPA metadata file hasn't been generated.\nSongs in the {i}track{/i} folder won't be listed if you build your mod without it.\n Set {i}config.developer{/i} to {u}True{/u} in order to generate this file.",
                        ok_action=Hide("dialog"))

    # Start the music playing on entry to the music room.
    on "replace" action [Function(ost_main.ost_start), Stop("music", fadeout=1.0)]
    on "show" action [Function(ost_main.ost_start), Stop("music", fadeout=1.0)]

    # Restore the main menu music upon leaving.
    on "hide" action [If(persistent.auto_restore_music,
        [Stop("music_room", fadeout=1.0), SetMute("music", False), Play("music", ost_main.prevTrack, fadein=1.0)],
        SetMute("music", True))]
    on "replaced" action [Hide("music_settings"), Hide("music_list"), Hide("music_list_type"), 
        Hide("music_info"), Function(ost_main.ost_log_stop), If(persistent.auto_restore_music,
        [Stop("music_room", fadeout=1.0), SetMute("music", False), Play("music", ost_main.prevTrack, fadein=1.0)],
        SetMute("music", True))]

screen music_list_type(type=None):

    drag:
        drag_name "mlisttype"
        drag_handle (0, 0, 1.0, 40)
        xsize 470
        ysize 260
        xpos 0.3
        ypos 0.2

        frame:

            if type is not None:
                hbox:
                    xalign 0.05 ypos 0.005
                    textbutton "<-":
                        text_style "navigation_button_text"
                        action [Hide("music_list"), ShowMenu("music_list_type")]

            hbox:
                ypos 0.005
                xalign 0.52 
                text "Music List":
                    style "music_room_generic_text"

            hbox:
                ypos 0.005
                xalign 0.98
                textbutton "X":
                    text_style "navigation_button_text"
                    action Hide("music_list_type")

            side "c":
                xpos 0.05
                ypos 0.2
                xsize 430
                ysize 200

                viewport id "mlt":
                    mousewheel True
                    draggable True
                    has vbox

                    if type is None:
                        textbutton "All Songs":
                            text_style "music_list_button_text"
                            action [Hide("music_list_type"), ShowMenu("music_list")]

                        textbutton "Artist":
                            text_style "music_list_button_text"
                            action [Hide("music_list_type"), ShowMenu("music_list_type", type="artist")]

                        textbutton "Album Artist":
                            text_style "music_list_button_text"
                            action [Hide("music_list_type"), ShowMenu("music_list_type", type="albumartist")]

                        textbutton "Composer":
                            text_style "music_list_button_text"
                            action [Hide("music_list_type"), ShowMenu("music_list_type", type="composer")]

                        textbutton "Genre":
                            text_style "music_list_button_text"
                            action [Hide("music_list_type"), ShowMenu("music_list_type", type="genre")]

                    else:
                        python:
                            temp_list = []
                            for st in soundtracks:
                                if type == "artist":
                                    if st.author not in temp_list:
                                        temp_list.append(st.author)
                                elif type == "albumartist":
                                    if st.albumartist not in temp_list:
                                        temp_list.append(st.albumartist)
                                elif type == "composer":
                                    if st.composer not in temp_list:
                                        temp_list.append(st.composer)
                                elif type == "genre":
                                    if st.genre not in temp_list:
                                        temp_list.append(st.genre)
                            
                            temp_list = sorted(temp_list)

                        for st in temp_list:
                            textbutton "[st]":
                                style "l_list"
                                text_style "music_list_button_text"
                                action [Hide("music_list_type"), ShowMenu("music_list", type=type, arg=st)]
                        
    on "hide" action With(Dissolve(0.25))
            
screen music_list(type=None, arg=None):

    drag:
        drag_name "mlist"
        drag_handle (0, 0, 1.0, 40)
        xsize 470
        ysize 260
        xpos 0.3
        ypos 0.2

        python:
            new_soundtrack_list = []
            for st in soundtracks:
                if type == "artist":
                    if arg == st.author:
                        new_soundtrack_list.append(st)
                elif type == "albumartist":
                    if arg == st.albumartist:
                        new_soundtrack_list.append(st)
                elif type == "composer":
                    if arg == st.composer:
                        new_soundtrack_list.append(st)
                elif type == "genre":
                    if arg == st.genre:
                        new_soundtrack_list.append(st)
                else:
                    new_soundtrack_list.append(st)
                    
            new_soundtrack_list = sorted(new_soundtrack_list, key=lambda new_soundtrack_list: new_soundtrack_list.name)

        frame:
            hbox:
                xalign 0.05 ypos 0.005
                textbutton "<-":
                    text_style "navigation_button_text"
                    action [Hide("music_list"), ShowMenu("music_list_type", type=type)]

            hbox:
                ypos 0.005
                xalign 0.52 
                text "Music List":
                    style "music_room_generic_text"
                    size 24

            hbox:
                ypos 0.005
                xalign 0.98
                textbutton "X":
                    text_style "navigation_button_text"
                    action Hide("music_list")

            side "c":
                xpos 0.05
                ypos 0.2
                xsize 430
                ysize 200

                viewport id "ml":
                    draggable True
                    mousewheel True
                    has vbox

                    for nst in new_soundtrack_list:
                        textbutton "[nst.name]":
                            style "l_list"
                            text_style "music_list_button_text"
                            action [Hide("music_list"), Function(ost_info.set_current_soundtrack, nst), Play("music_room", nst.path, loop=ost_controls.loopSong, fadein=2.0)]

    on "hide" action With(Dissolve(0.25))

screen music_settings():

    drag:
        drag_name "msettings"
        drag_handle (0, 0, 1.0, 40)
        xsize 470
        ysize 260
        xpos 0.5
        ypos 0.5

        frame:
            hbox:
                ypos 0.005
                xalign 0.52 
                text "Player Settings":
                    style "music_room_generic_text"

            hbox:
                ypos 0.005
                xalign 0.98
                textbutton "X":
                    text_style "navigation_button_text"
                    action Hide("music_settings")

            side "c":
                xpos 0.05
                ypos 0.2
                xsize 430
                ysize 200

                viewport id "mlt":
                    mousewheel True
                    draggable True
                    has vbox
                    
                    textbutton "Compact Mode":
                        style "radio_button" 
                        action [Hide("music_list_type"), Hide("music_list"), Hide("music_info"),
                            ToggleField(persistent, "listui", False, True)]

                    textbutton "Restore Music Channel Music":
                        style "radio_button" 
                        action InvertSelected(ToggleField(persistent, "auto_restore_music", False, True))
                            
                    textbutton "About DDLC OST-Player":
                        text_style "navigation_button_text" 
                        action Show("dialog", message="Ren'Py Universal Player by GanstaKingofSA.\nCopyright © 2021-2022 GanstaKingofSA.", 
                            ok_action=Hide("dialog"))

    on "hide" action With(Dissolve(0.25))    

screen music_info():

    drag:
        drag_name "minfo"
        drag_handle (0, 0, 1.0, 40)
        xsize 480
        ysize 260
        xpos 0.4
        ypos 0.4

        frame:
            hbox:
                ypos 0.005
                xalign 0.52 
                text "Music Info" style "music_room_generic_text"

            hbox:
                ypos 0.005
                xalign 0.98
                textbutton "X":
                    text_style "navigation_button_text"
                    action Hide("music_info")

            side "c":
                xpos 0.05
                ypos 0.2
                xsize 460
                ysize 200

                viewport id "mi":
                    mousewheel True
                    draggable True
                    has vbox

                    python:
                        albumartist = ost_info.get_album_artist()
                        composer = ost_info.get_composer()
                        genre = ost_info.get_genre()
                        sideloaded = ost_info.get_sideload()
                        comment = ost_info.get_description() or None
                    
                    text "{u}Album Artist{/u}: [albumartist]" style "music_room_info_text"
                    text "{u}Composer{/u}: [composer]" style "music_room_info_text"
                    text "{u}Genre{/u}: [genre]" style "music_room_info_text"
                    text "{u}Sideloaded{/u}: [sideloaded]" style "music_room_info_text"
                    text "{u}Comment{/u}: [comment]" style "music_room_info_text"

    on "hide" action With(Dissolve(0.25))    

style music_room_music_text is navigation_button_text:
    #font "images/music_room/riffic-bold.ttf"
    color "#000"
    outlines [(0, "#000", 0, 0)]
    hover_outlines []
    insensitive_outlines []
    size 36

style music_room_song_author_text:
    font "images/music_room/NotoSansSC-Light.otf"
    size 22
    outlines[]
    color "#000"

style music_list_button_text is navigation_button_text:
    size 22

style music_room_hbox:
    spacing 25

style music_room_bar:
    xsize 710
    thumb "gui/slider/horizontal_hover_thumb.png"

style music_room_list_bar is music_room_bar:
    xsize 600

style music_room_alt_list_title_text:
    font "images/music_room/NotoSansSC-Light.otf"
    color "#000"
    outlines []
    size 15
    bold True

style music_room_alt_list_author_text is music_room_alt_list_title_text:
    size 13
    bold False

transform music_room_transition:
    alpha(0.0)
    linear 0.5 alpha(1.0)

style song_progress_text:
    font "gui/font/Halogen.ttf"
    size 25
    outlines[]
    color "#000"
    xalign 0.28 
    yalign 0.78

style song_duration_text is song_progress_text:
    xalign 0.79 
    yalign 0.78

style l_list:
    left_padding 5

style renpy_generic_text:
    font "images/music_room/NotoSans-Regular.ttf"
    color "#000"
    outlines []

transform cover_art_resize(x):
    size(x, x)