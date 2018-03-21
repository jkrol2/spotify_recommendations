# Moodify

This is repo for university project - recommendation system (based on user's data and user's current mood) for Spotify.

Types of tracks:
0 - sad
1 - happy
2 - party
3 - angry
4 - calm
5 - none

Format of file with playlists:
First line describe name of playlist in Spotify, so it is easier to add new ones.
Next line is: type of playlist (as described above), 'space' character and URL of playlist.
Currently script reads only 100 tracks from playlist. It is enough to get a lot of data, but worth to repair in future.
I have added error handling so it does not crash and just continue iterating to next playlist.


