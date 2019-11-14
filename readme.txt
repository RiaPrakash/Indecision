Overview:
A playlist recommender for all the times  you're feeling moody but don't know what to listen to. 
Suggests playlists from your Spotify account by mapping audio analysis on your playlists to 
sentiment analysis on descriptive words entered by you describing your current mood.

Instructions to run project:
1. First declare your Spotify client ID, secret ID and URI in the terminal
export SPOTIPY_CLIENT_ID='<your-id>'
export SPOTIPY_CLIENT_SECRET='<your-secret>'
export SPOTIPY_REDIRECT_URI='<your-redirect-url'

2. Then run the following command in terminal
>> python flask1.py username 
where username is whatever username you wish. 

3. Go to http://localhost:5000/