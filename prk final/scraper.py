import requests
from bs4 import BeautifulSoup

def scrape_nba_titles():
    url = "https://www.nba.com/news"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = [h.text for h in soup.find_all("h3")]
    return titles[:5]