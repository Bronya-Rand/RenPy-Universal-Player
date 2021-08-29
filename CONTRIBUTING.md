# Contributing to Ren'Py Universal Player

In general I am fine with any pull requests that adds, fixes or improves the code in this project. At most I would ask for the following

* State the PR's intended purpose like adding support for X, fix for Y, improved code for Z, etc.
   > If your PR is a fix for the project, please state the original intention and expected result and error you get. Screenshots of the issue are useful too.

Here is a sample PR for fixing code in `ost.py`
```
Title: OGG Auto-Define Update Fix

This PR fixes a line of code in `ost.py` that caused OGG tracks to not be defined automatically.
Intended Result: The music room player would load in OGG tracks at start-up or by the refresh button inside 'track'.
Result Gotten: No OGG tracks appear in the player list.
```

Here is a sample PR for adding a feature to the music room player.
```
Title: FLAC Track Support

This PR adds FLAC support to the music room player so users can play FLAC files within the project.
Result After This PR: FLAC files can be played from within the projects' music room player.
```

And here is a sample PR for improved code in screens.rpy.
```
Title: Cover Art Transition

This PR improves 'screens.rpy' by having 'cover_art_fade' constantly run after each track completes.
Result After This PR: Cover Art of tracks fade each time a new one is played.
```
