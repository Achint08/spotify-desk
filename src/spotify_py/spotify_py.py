import os
import subprocess
import base64
import requests


class Spotify(object):

    SPOTIFY_SEARCH_API = "https://api.spotify.com/v1/search"
    SPOTIFY_TOKEN_URI = "https://accounts.spotify.com/api/token"
    SPOTIFY_SHARE_URL = "https://open.spotify.com/track/"

    def __init__(self, client_id=None, client_secret=None):
        self.CLIENT_ID = ''
        self.CLIENT_SECRET = ''
        self.ACCESS_TOKEN = ''
        if not client_id:
            client_id = os.environ.get('SPOTIFY_CLIENT_ID', None)
        if not client_secret:
            client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET', None)
        self.__setup(client_id, client_secret)

    def __setup(self, client_id, client_secret):
        if not client_id or not client_secret:
            print('Please add CLIENT_ID and CLIENT_SECRET')
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        auth_token = base64.b64encode('{}:{}'.format(
            self.CLIENT_ID,
            self.CLIENT_SECRET
        ).encode('ascii')).decode('utf-8').strip()
        headers = {
            'Authorization': 'Basic ' + auth_token
        }
        data = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(
            self.SPOTIFY_TOKEN_URI,
            headers=headers,
            data=data
        )

        if response.status_code == 200:
            self.ACCESS_TOKEN = response.json()['access_token']
            print('Authorization Successful!')
        else:
            print('Authorization failed. \
                Please update your correct CLIENT_ID and CLIENT_SECRET')

    def show_artist(self):
        response = subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 artist of current track as string'],
            stdout=subprocess.PIPE
        )
        return response.stdout.decode('utf-8').strip()

    def show_album(self):
        response = subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 album of current track as string'],
            stdout=subprocess.PIPE
        )
        return response.stdout.decode('utf-8').strip()

    def show_track(self):
        response = subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 name of current track as string'],
            stdout=subprocess.PIPE
        )
        return response.stdout.decode('utf-8').strip()

    def search(self, query, query_type):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.ACCESS_TOKEN
        }
        params = {
            'q': query,
            'type': query_type
        }
        response = requests.get(
            self.SPOTIFY_SEARCH_API,
            params=params,
            headers=headers
        )
        return response.json()

    def play(self, uri):
        play_command = 'tell application "Spotify" to play'
        if uri:
            play_command += ' track "{}"'.format(uri)

        subprocess.run(
            ['osascript',
             '-e',
             play_command
             ]
        )

    def search_and_play(self, query, query_type='track'):
        results_key = query_type + 's'
        search_results = self.search(query, query_type)
        play_track_uri = search_results[results_key]['items'][0]['uri']
        self.play(play_track_uri)

    def play_album(self, query):
        self.search_and_play(query, 'album')

    def play_artist(self, query):
        self.search_and_play(query, 'artist')

    def play_playlist(self, query):
        self.search_and_play(query, 'playlist')

    def play_track(self, query):
        self.search_and_play(query, 'track')

    def play_url(self, url_query):
        track_id = url_query.replace(self.SPOTIFY_SHARE_URL, '')
        local_uri = 'spotify:track:' + track_id
        self.play(local_uri)

    def pause(self):
        subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to pause'
             ]
        )

    def quit(self):
        subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to quit'
             ]
        )

    def next_track(self):
        subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to next track'
             ]
        )

    def previous_track(self):
        subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify"\nset\
                  player position to 0\nprevious track\nend tell'
             ]
        )

    def replay_track(self):
        subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 set player position to 0'
             ]
        )

    def get_volume(self):
        response = subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 sound volume as integer'
             ],
            stdout=subprocess.PIPE
        )
        return response.stdout.decode('utf-8').strip()

    def set_volume(self, volume):
        subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 set sound volume to {}'.format(volume)
             ]
        )

    def volume_up(self):
        current_volume = int(self.get_volume())
        volume = current_volume + 10
        self.set_volume(volume)

    def volume_down(self):
        current_volume = int(self.get_volume())
        volume = current_volume - 10
        self.set_volume(volume)

    def set_min_volume(self):
        self.set_volume(0)

    def set_max_volume(self):
        self.set_volume(100)

    def toogle_shuffle_playback_mode(self):
        subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 set shuffling to not shuffling'
             ]
        )

        is_shuffle_mode = subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 shuffling'
             ],
            stdout=subprocess.PIPE
        ).stdout.decode('utf-8').strip()

        return False if is_shuffle_mode == 'false' else True

    def toogle_repeat_playback_mode(self):
        subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 set repeating to not repeating'
             ]
        )

        is_repeat_mode = subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 repeating'
             ],
            stdout=subprocess.PIPE
        ).stdout.decode('utf-8').strip()

        return False if is_repeat_mode == 'false' else True

    def get_share_url(self):
        local_uri = subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 spotify url of current track'
             ],
            stdout=subprocess.PIPE
        ).stdout.decode('utf-8').strip()
        share_id = local_uri.replace('spotify:track:', '')
        return self.SPOTIFY_SHARE_URL + share_id

    def set_position(self, seconds):
        subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 set player position to {}'.format(seconds)
             ]
        )

    def get_current_state(self):
        state_response = subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 player state as string'
             ],
            stdout=subprocess.PIPE
        )

        return state_response.stdout.decode('utf-8').strip()

    def get_current_track_duration_seconds(self):
        duration_response = subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 duration of current track'
             ],
            stdout=subprocess.PIPE
        )

        duration = int(duration_response.stdout.decode('utf-8').strip())/1000
        return duration

    def get_current_player_position_seconds(self):
        current_position = subprocess.run(
            ['osascript',
             '-e',
             'tell application "Spotify" to \
                 player position'
             ],
            stdout=subprocess.PIPE
        )

        duration = int(current_position.stdout.decode('utf-8').strip())/1000
        return duration
