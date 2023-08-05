# Music Player GUI using Python Tkinter


## Functionality of the Music Player

- Better Looking GUI
- Pause/Play Supported
- Add/Delete songs from Playlist
- Previous/Next song function
- Time duration of song / next song displays
- List of all the songs.
- Adjust Volume
- Automatically Playing in Queue
- Play Selected song from Playlist

## Usage

- Make sure you have Python installed in your system.
- Run Following command in the CMD.
 ```
  pip install PyMusic-Player
  ```
## Example

 ```
# test.py
from PyMusic_Player import Music_Player_GUI

## Make sure all the .MP3 songs besides in the folder
song_dir = 'path/of/songs_dir'

# If you want to give the Icon, make sure you have downloaded proper .ICO file.
icon = 'your.ico'
Music_Player_GUI(song_dir,icon)
  ```

## Run the following Script.
 ```
  python test.py
 ```

## Screenshots
<img src="https://github.com/Spidy20/PyMusic_Player/blob/master/s1.PNG">

## Note 
- I have tried to implement all the functionality, it might have some bugs also. Ignore that or please try to solve that bug.
