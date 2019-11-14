To run project:
1. First declare your Spotify client ID, secret ID and URI in the terminal
export SPOTIPY_CLIENT_ID='<your-id>'
export SPOTIPY_CLIENT_SECRET='<your-secret>'
export SPOTIPY_REDIRECT_URI='http://localhost:5000/'

2. Then run the following command in terminal
>> python flask1.py username 
where username is whatever username you wish. 

3. Go to http://localhost:5000/

Things I want to improve in the project:
- Make tracks, plallists and tracks in playlists GET methods
- Use more feautures in audio analysis. Currently using danceability and energy.
- Find threshold for danceability and energy. Currently alloting based on min and max.
- Create option to alter words.
- Fix audio analysis boolean checker.