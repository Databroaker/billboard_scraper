from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
import pickle
from secrets import *
from spotify_object import Spotify

class BillboardScraper:
    def __init__(self):
        self.chart_data = []
        self.load()
        self.scrape = False

        self.spotifyObj = Spotify(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SPOTIFY_SCOPE)

        #pprint(self.chart_data)

        today = datetime.today().strftime("%m-%d-%Y")

        if self.scrape:
            self.scrape_chart_data("billboard-200", "01-01-1900", today, max_workers=100)
            print("There are {} results".format(len(self.chart_data)))
            self.cleanup()
            self.save()

        self.add_songs_to_playlist("rock-songs", 1900, 2099, randomize=True, reset=True)

    def add_songs_to_playlist(self, chart_name, start_year, end_year, randomize=False, reset=False):
        to_add = []
        blacklist = []

        for entry in self.chart_data:
            print(entry)
            if entry["chart"] == chart_name:
                the_year = int(entry["year"])
                if the_year >= start_year and the_year <= end_year :
                    bl_string = "{}:::{}".format(entry["artist"], entry["title"])
                    if bl_string not in blacklist:
                        to_add.append(entry)
                        blacklist.append(bl_string)

        self.spotifyObj.add_track_to_playlist(to_add, "5Pj5YUcfvquncJEHXNmZ44", randomize=randomize, reset=reset)



    def cleanup(self):
        chart_names = []
        for entry in self.chart_data:
            if entry["chart"] not in chart_names:
                chart_names.append(entry["chart"])

        cleaned_chart_data = []

        for chart_name in chart_names:
            chart_list = []
            for entry in self.chart_data:
                if entry["chart"] == chart_name:
                    chart_list.append(entry)
            years = dict()
            for entry in chart_list:
                try:
                    years[int(entry['year'])].append(entry)
                except:
                    years[int(entry['year'])] = [entry]
            cleaned_years = self.remove_duplicate_songs(years)
            for year in sorted(cleaned_years):
                entry = cleaned_years[year]
                for e in entry:
                    cleaned_chart_data.append(e)

        self.chart_data = cleaned_chart_data

    def remove_duplicate_songs(self, years):
        song_tracker = {}

        for year, songs in years.items():
            for song_data in songs:
                song_key = (song_data['artist'], song_data['title'])
                if song_key not in song_tracker or int(year) > song_tracker[song_key]['year']:
                    song_tracker[song_key] = {'year': int(year), 'data': song_data}

        cleaned_years = {}
        for song_key, info in song_tracker.items():
            year = info['year']
            if year not in cleaned_years:
                cleaned_years[year] = []
            cleaned_years[year].append(info['data'])

        return cleaned_years

    def load(self):
        try:
            with open("data.pkl", 'rb') as file:
                self.chart_data = pickle.load(file)
        except:
            pass

    def save(self):
        with open("data.pkl", 'wb') as file:
            pickle.dump(self.chart_data, file)

    def extract_chart_data(self, html_content, chart, year):
        soup = BeautifulSoup(html_content, 'html.parser')
        chart_uls = soup.find_all('ul', class_='o-chart-results-list-row')
        results = []

        for ul in chart_uls:
            li_elements = ul.find_all('li', class_='o-chart-results-list__item')
            for li in li_elements:
                title = li.find('h3', class_='c-title')
                if title:
                    title_text = title.get_text(strip=True)
                    label = li.find('span', class_='c-label')
                    label_text = label.get_text(strip=True) if label else None
                    results.append({
                        "artist": label_text,
                        "title": title_text,
                        "chart": chart,
                        "year": year
                    })

        return results

    def scrape_single_date(self, chart_name, date):
        while True:
            link = f'https://www.billboard.com/charts/{chart_name}/{date.strftime("%Y-%m-%d")}/'
            try:
                response = requests.get(link, timeout=10)
                response.raise_for_status()
                chart_data = self.extract_chart_data(response.text, chart_name, date.strftime("%Y"))
                print(f"Scraped: {link}")
                return chart_data
            except requests.RequestException as e:
                print(f"Error scraping {link}: {e}")

    def remove_duplicates_dicts(self, dict_list):
        seen = set()
        unique_list = []
        for d in dict_list:
            tuple_d = tuple(sorted(d.items()))
            if tuple_d not in seen:
                seen.add(tuple_d)
                unique_list.append(d)
        return unique_list

    def scrape_chart_data(self, chart_name, start_date, end_date, max_workers=4):
        start_date = datetime.strptime(start_date, "%m-%d-%Y").date()
        end_date = datetime.strptime(end_date, "%m-%d-%Y").date()

        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=7)

        all_results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.scrape_single_date, chart_name, date) for date in dates]
            for future in futures:
                result = future.result()
                all_results.extend(result)

        self.chart_data += self.remove_duplicates_dicts(all_results)

        return self.chart_data

if __name__ == "__main__":
    BillboardScraper()