# Myk3le's Billboard Scraper

Bypasses Billboard's (terrible) attempt at stopping non-premium users from accessing historical chart data.

Can use the chart data to create spotify playlists, download mp3s from youtube, or whatever you want.

```python
# billboard_scraper.py

if __name__ == "__main__":
    bs = BillboardScraper()
    bs.run([
        # Chart Name / Spotify ID / Start Year / End Year / Randomize Playlist / Reset 
        ["dance-electronic-songs", "2dQ3l3tfs1RJVLvlMtP1AE", 2010, 2019, True, True],
        ["r-b-hip-hop-songs", "0PqOIZndNeEa06NqfVgRWj", 1990, 1999, True, False],
        ["rock-songs", "5Pj5YUcfvquncJEHXNmZ44", 1990, 2099, True, False],
        ["hot-100", "7JfbAmvCqyUYMoGNS29Q6b", 2020, 2099, True, False],
        ["billboard-200", "6U167rWiAmYDtQvZF2ZfBi", 2020, 2099, True, True]
    ])
```

Create a secrets.py file with the following information...
```python
SPOTIFY_CLIENT_ID = 'your client id'
SPOTIFY_CLIENT_SECRET = 'your client secret'
SPOTIFY_REDIRECT_URI = 'your redirect uri'
SPOTIFY_USER_ID = 'your spotify user id'
SPOTIFY_SCOPE = 'playlist-modify-private playlist-modify-public'
```
