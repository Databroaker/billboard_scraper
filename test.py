import requests
from bs4 import BeautifulSoup
import os

import requests
from bs4 import BeautifulSoup
import datetime
import re
import pickle
import datetime
import time


import requests

import time
import sys
import os
from pathlib import Path


list_of_charts = [
    #'https://www.billboard.com/charts/r-b-hip-hop-songs/{}',
    'https://www.billboard.com/charts/rock-songs/{}',
    # 'https://www.billboard.com/charts/pop-songs/{}'
]

for the_year in reversed(range(1990, 1991)):
    for the_chart in list_of_charts:

        identifier = str(the_year) + "-" + the_chart.split("charts/")[-1].split("/")[0]
        print(identifier)


        bl_file = '{}.pkl'.format(identifier)


        try:
            with open(bl_file, 'rb') as file:
                # Call load method to deserialze
                blacklist = pickle.load(file)
        except:
            blacklist = []

        class BillBoard:
            endpoint = the_chart

            def __init__(self, date='2000-08-12') -> None:
                try:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError("Incorrect data format, should be YYYY-MM-DD")

                self.endpoint = self.endpoint.format(date)

            def request_website(self):
                response = requests.get(self.endpoint)
                self.payload = response.text

            def get_data(self):
                #print('Getting data from billboard\n')
                self.soup = BeautifulSoup(self.payload, 'html.parser')

            def parse_data(self):
                #'Parsing data from billboard\n')
                soup = self.soup
                songs = []

                divs = soup.find_all("li", {"class": "o-chart-results-list__item"})
                for d in divs:
                    txt = " ".join(d.get_text().replace("\t", " ").replace("\n", " ").strip().split(" "))
                    if len(txt) > 5:
                        splits = txt.split("   ")
                        txt = splits[-1] + "   " + splits[0]
                        txt = re.sub(' +',' ', txt)
                        if "NEW" in txt or "RE- ENTRY" in txt:
                            continue

                        artist = re.sub(' +',' ', splits[-1])
                        artist = " ".join(artist.split())

                        song =  re.sub(' +',' ', splits[0])
                        song = " ".join(song.split())

                        songs.append([artist, song])
                        #txt)
                        #print("=====")


                        # title = d.find('h3').get_text().strip()
                        # print(title)
                        # artist = d.find_all("span", {"class": "c-label"})[-1].get_text().strip()
                        # print(title + " - " + artist)

                return songs

        def get_billboard_song_titles_for_year(year):
            """
            Scrapes Wikipedia  for billboard song titles for a given year, There might be better sources to parse from
            but i've chosen wikipeida for this first iteration because the page format is really standard, lightweight and
            hasn't changed for the last 18 years.
            :return: List of billboard songs and artists in a tuple '(song, artist)'
            """
            billboard_page = "https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_"
            page = requests.get(billboard_page + str(year))
            soup = BeautifulSoup(page.content, 'html.parser')
            doc = soup.find("table", {"class": "wikitable"})
            year_data = []
            for row in doc.find_all(["tr"])[1:]:
                # The th is required because ~2000+ uses that format instead
                row_data = [cell.text.strip() for cell in row.findAll(["td", "th"])]
                if len(row_data) != 3:
                    print("Error Processing Row: ", row)
                else:
                    year_data.append(tuple(row_data))
            return year_data

        def parse_artist(content):
            for split_token in [" & ", " \\ ", " feat ", " featuring ", " and "]:
                content = content.partition(split_token)[0]
            return content

        def parse_song(content):
            for split_token in ["\\", "/"]:
                content = content.partition(split_token)[0]
            return content




        if __name__ == "__main__":

            year = the_year

            start_date = datetime.date(year=the_year, month=1, day=1)
            end_date   = datetime.date(year=the_year, month=12,  day=31)

            current_date = start_date
            all_songs = []
            while current_date <= end_date:
                track_ids = []
                new_ones = []
                strr = current_date.strftime("%Y-%m-%d")
                print("{} {}".format(identifier, strr))
                try:
                    bb = BillBoard(strr)
                    bb.request_website()
                    bb.get_data()
                    songs = bb.parse_data()

                    for s in songs:
                        all_songs.append("{} - {}".format(s[0], s[1]))
                        all_songs = list(set(all_songs))
                    print("Songs: {}".format(len(all_songs)))
                except Exception as e:
                    print(str(e))
                    print("ERROR CONNECTING TRYING AGAING in 1 MINUTE")
                    time.sleep(1)
                    continue


                for s in songs:
                    if s not in blacklist:

                        search_query = "{} {}".format(s[0], s[1])

                        if search_query not in blacklist:
                            ind = 0
                            skip = False
                            while True:
                                try:
                                    break
                                except:
                                    print("DIDNT FIND IT! TRYING AGAIN WITH INDEX {}".format(ind))
                                    ind += 1
                                    if ind >= 100:
                                        skip = True
                                        break
                            if not skip:
                                pass
                                #download(video_id, "G:\\_BILLBOARD\\{}\\".format(identifier), "{} - {}".format(s[0], s[1]))
                            blacklist.append(search_query)
                            with open(bl_file, 'wb') as file:
                                pickle.dump(blacklist, file)
                        else:
                            pass
                current_date += datetime.timedelta(days=7)
                #print("sleeping for 1")
                #time.sleep(10)

            # year_songs = get_billboard_song_titles_for_year(year)
            # track_ids = []
            # playlist = sp.user_playlist_create(username, "Billboard Hot 100 " + str(year), True)
            # for (rank, track, artist) in year_songs:
            #     query = parse_artist(artist) + " " + parse_song(track)
            #     results = sp.search(q=query)
            #     try:
            #         track_ids.append(results['tracks']['items'][0]['uri'])
            #     except:
            #         print("Error! Could not find: ",(year, rank, track, query))
            # sp.user_playlist_add_tracks(username, playlist['uri'], track_ids)
            # print("Play List Complete!")