from datetime import datetime, timedelta
from pprint import pprint
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
import pickle

class BillboardScraper:
    def __init__(self):
        self.chart_data = dict()
        self.load()

        pprint(self.chart_data)

        #self.scrape_chart_data("rock-songs", "01-01-2009", datetime.today().strftime("%m-%d-%Y"), max_workers=100)
        #print("There are {} results".format(len(self.chart_data)))

        self.save()

    def load(self):
        try:
            with open("data.pkl", 'rb') as file:
                self.chart_data = pickle.load(file)
        except:
            pass

    def save(self):
        with open("data.pkl", 'wb') as file:
            pickle.dump(self.chart_data, file)

    def extract_chart_data(self, html_content):
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
                    results.append(f"{label_text} - {title_text}")

        return list(set(results))

    def scrape_single_date(self, chart_name, date):
        """Scrape chart data for a single date and return the results."""
        while True:
            link = f'https://www.billboard.com/charts/{chart_name}/{date.strftime("%Y-%m-%d")}/'
            try:
                response = requests.get(link, timeout=10)
                response.raise_for_status()  # Raise exception for bad status codes
                chart_data = self.extract_chart_data(response.text)
                print(f"Scraped: {link}")
                return chart_data
            except requests.RequestException as e:
                print(f"Error scraping {link}: {e}")


    def scrape_chart_data(self, chart_name, start_date, end_date, max_workers=4):
        """Scrape chart data for a date range using multithreading."""
        start_date = datetime.strptime(start_date, "%m-%d-%Y").date()
        end_date = datetime.strptime(end_date, "%m-%d-%Y").date()

        # Generate list of dates (increment by 7 days)
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=7)

        # Collect all results in a temporary list
        all_results = []

        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit scraping tasks for all dates
            futures = [executor.submit(self.scrape_single_date, chart_name, date) for date in dates]
            # Collect results from completed threads
            for future in futures:
                result = future.result()  # Get the result of each thread
                all_results.extend(result)

        # Deduplicate and assign to self.chart_data after all threads are done
        self.chart_data[chart_name] = list(set(all_results))

        return self.chart_data

if __name__ == "__main__":
    BillboardScraper()