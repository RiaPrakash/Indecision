from flask import Flask, render_template, request
app = Flask(__name__)
import spotipy
import spotipy.util as util
import sys
import requests 
import webbrowser, os

tracks = []
playlists = []
playlist_ids = []
playlist_tracks = []

positive_playlists = []
negative_playlists = []
neutral_playlists = []

words = []
suggestion = ['No playlist found yet']

@app.route('/', methods=['POST', 'GET'])
def home():
    
    # Only start program if username is provided in command line
    scope = 'user-library-read'
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: %s username" % (sys.argv[0],) )
        sys.exit()

    # Prompt for Spotify token
    token = util.prompt_for_user_token(username, scope)
    if token:
        sp = spotipy.Spotify(auth=token)

        # Tracks
        if len(tracks) == 0:
            results = sp.current_user_saved_tracks()
            for item in results['items']:
                track = item['track']
                tracks.append(track['name'] + ' - ' + track['artists'][0]['name'])
            print('Got all tracks.')
            # Setting False here 

        # Playlists
        if len(playlists) == 0 and len(playlist_ids) == 0:
            playlist_results = sp.current_user_playlists(limit=50, offset=0)
            for item in playlist_results['items']:
                playlists.append(item['name'])
                playlist_ids.append(item['id'])
            print('Got all playlists.')
        
        # Tracks in playlist 
        if len(playlist_tracks) == 0:
            for playlist_id in playlist_ids:
                songs = []
                current_tracks = sp.user_playlist_tracks(sp.current_user()['id'],playlist_id)
                for item in current_tracks['items']:
                    track_test = item['track']
                    # songs.append(track_test['name'])
                    songs.append(track_test['id'])
                playlist_tracks.append(songs)
            print('Got all playlist tracks')

            # Features per playlist - only after tracks found
            tracks_rand = ['R', 'a']
            print('Conducting audio analysis.')
            # Calculate mean danceability, energy and tempo
            dance_mean = []
            energy_mean = []
            tempo_mean = []
            for pt in playlist_tracks:
                current_dance = []
                current_energy = []
                current_tempo = []
                for track in pt:
                    # To prevent NoneType errors
                    if track != None:
                        current_track_features = sp.audio_features(tracks=track)
                        dance = current_track_features[0]['danceability']
                        current_dance.append(dance)
                        energy = current_track_features[0]['energy']
                        current_energy.append(energy)
                        tempo = current_track_features[0]['tempo']
                        current_tempo.append(tempo)
                dance_mean.append(sum(current_dance)/len(current_dance))
                energy_mean.append(sum(current_energy)/len(current_energy))
                tempo_mean.append(sum(current_tempo)/len(current_tempo))
            # print('dance_mean', dance_mean)
            # print('energy_mean', energy_mean)
            # print('tempo_mean', tempo_mean)
            # print(playlists)
            # Dictionary mapping playlists to mean values
            d = {}
            for i in range(0, len(playlists)):
                d[playlists[i]] = [dance_mean[i], energy_mean[i], tempo_mean[i]]
            print(d)
            # Alotting Playlist based on audio analysis - not using tempo
            for i in range(0, 2):
                # Alotting positive and negative
                key_max = max(d.keys(), key=(lambda k: d[k][i]))
                if key_max not in positive_playlists:
                    positive_playlists.append(key_max)
                    print('added ', key_max, ' to pos playlists')
                key_min = min(d.keys(), key=(lambda k: d[k][i]))
                if key_min not in negative_playlists:
                    negative_playlists.append(key_min)
                    print('added ', key_min, ' to neg playlists')
            for k in d.keys():
                # Alotting neutral
                if k not in positive_playlists and k not in negative_playlists:
                    if k not in neutral_playlists:
                        neutral_playlists.append(k)
                        print('added ', k, ' to neu playlists')
            print('Completed audio analysis')
                
        # User Marking Their Own Playlists
        if (request.method == 'POST') and ("Positive" in request.form):
            positive_playlist = request.form['Positive']
            positive_playlists.append(positive_playlist)
            print('User altered positive_playlists to: ', positive_playlists)
        if (request.method == 'POST') and ("Negative" in request.form):
            negative_playlist = request.form['Negative']
            negative_playlists.append(negative_playlist)
            print('User altered negative_playlists to: ', negative_playlists)
        if (request.method == 'POST') and ("Neutral" in request.form):
            neutral_playlist = request.form['Neutral']
            neutral_playlists.append(neutral_playlist)
            print('User altered neutral_playlists to: ', neutral_playlists)

        # Words
        if (request.method == 'POST') and ("Words" in request.form):
            text = request.form['Words']
            processed_text = text.upper()
            words.append(text)
            print('Words are: ', words)
        
            # Suggestion
            values = []
            for word in words:
                r = requests.post('http://text-processing.com/api/sentiment/', data={"text":word})
                data = r.json()
                values.append(data['label'])
            print('Sentiment of words are: ', values)
            
            total_vibe = []
            if len(words) > 0:
                n_pos = 0
                n_neg = 0
                n_neutral = 0
                for value in values:
                    if value == 'pos':
                        n_pos += 1
                    if value == 'neg':
                        n_neg += 1
                    if value == 'neutral':
                        n_neutral += 1
                r_pos = n_pos/(n_pos + n_neg + n_neutral)
                r_neg = n_neg/(n_pos + n_neg + n_neutral)
                r_neutral = n_neutral/(n_pos + n_neg + n_neutral)
                print('ratios: ', r_pos, r_neg, r_neutral)
                if (r_pos >= r_neg) and (r_pos >= r_neutral):
                    total_vibe.append('pos')
                if (r_neg >= r_pos) and (r_neg >= r_neutral):
                    total_vibe.append('neg')
                if (r_neutral >= r_pos) and (r_neutral >= r_neg):
                    total_vibe.append('neutral')
                print('total_vibe is: ', total_vibe)

            if len(total_vibe) > 0:
                # if 'No playlist found yet' in suggestion:
                #     suggestion.remove('No playlist found yet')
                suggestion.clear()
                if 'pos' in total_vibe:
                    suggestion.extend(positive_playlists)
                if 'neg' in total_vibe:
                    suggestion.extend(negative_playlists)
                if 'neutral' in total_vibe:
                    suggestion.extend(neutral_playlists)

    else:
        print("Can't get token for", username)

    return render_template('index1.html', user=username, 
    tracks=tracks, playlists=playlists, words=words, suggestion=suggestion,
    positive_playlists=positive_playlists, negative_playlists=negative_playlists, neutral_playlists=neutral_playlists)


if __name__ == '__main__':
    app.run(debug=True)