import pickle
import time

import spotipy
from spotipy import SpotifyOAuth
from concurrent.futures import ThreadPoolExecutor
import random


class Spotify:
    def __init__(self, client_id, client_secret, redirect_uri, scope):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope
            ))

    # Function to search for a single song's URI
    def search_song(self, sp, song, max_retries=5):
        query = f"track:{song['title']} artist:{song['artist']}"
        for attempt in range(max_retries):
            try:
                result = sp.search(q=query, type='track', limit=1)
                song_uri = result['tracks']['items'][0]['uri']
                print(f"Found: {song['title']} by {song['artist']} ({song_uri})")
                return song_uri
            except (IndexError, KeyError):
                print(f"Track not found: {song['title']} by {song['artist']}")
                return None
            except spotipy.exceptions.SpotifyException as e:
                if e.http_status == 429:  # Rate limit error
                    retry_after = int(e.headers.get('Retry-After', 10))  # Default to 10s
                    print(f"Rate limit hit, retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                else:
                    print(f"Error searching {song['title']} by {song['artist']}: {e}")
                    return None
        print(f"Failed to find {song['title']} by {song['artist']} after {max_retries} retries")
        return None

    def add_track_to_playlist(self, songs_to_add, playlist_id=None, randomize=False, reset=False):
        existing_uris = []

        offset = 0
        while True:
            results = self.sp.playlist_items(playlist_id, limit=100, offset=offset)
            existing_uris.extend([item['track']['uri'] for item in results['items']])
            if len(results['items']) < 100:
                break
            offset += 100
        print(f"Found {len(existing_uris)} existing tracks in playlist")

        song_uris = list(existing_uris)

        if randomize:
            try:
                self.sp.playlist_replace_items(playlist_id=playlist_id, items=[])
                print(f"Cleared all songs from playlist (ID: {playlist_id})")
            except spotipy.exceptions.SpotifyException as e:
                print(f"Error clearing playlist: {e}")
                exit()

        # Use ThreadPoolExecutor for concurrent searches
        max_workers = 3  # Adjust based on rate limits and performance
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Map songs to search function, passing Spotipy client and song dict
            results = executor.map(lambda song: self.search_song(self.sp, song), songs_to_add)

        # Collect valid URIs from results
        song_uris.extend([uri for uri in results if uri is not None])
        print(f"Total songs after search: {len(song_uris)}")

        song_uris = list(set(song_uris))
        if randomize:
            random.shuffle(song_uris)

        if song_uris:
            chunk_size = 100
            for i in range(0, len(song_uris), chunk_size):
                chunk = song_uris[i:i + chunk_size]
                self.sp.playlist_add_items(playlist_id=playlist_id, items=chunk)
                print(f"Added {len(chunk)} songs to playlist in batch {i // chunk_size + 1}")
            print(f"Total: Added {len(song_uris)} songs to playlist!")
        else:
            print("No songs were added to the playlist.")
