import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.upr.si/si/o-univerzi/"

all_articles_upr = []
url_suffixes = [
    "t4eu-/t4eu-priloznosti-/za-zaposlene/",
    "t4eu-/t4eu-priloznosti-/za-studente-/",
    "t4eu-novice/p/1",
    "t4eu-novice/p/2",
    "t4eu-/arhiv-preteklih-priloznosti-t4eu-/p/1",
    "t4eu-/arhiv-preteklih-priloznosti-t4eu-/p/2"
]
for suffix in url_suffixes:
    url = BASE_URL + suffix

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    for div in soup.find_all("div", class_="column-description P30 bg-2 resizable"):
        a = div.find("a")
        if a and a.get("href"):
            title = a.find("h5")
            all_articles_upr.append({
                "title": title.get_text(strip=True),
                "link": "https://www.upr.si" + a["href"]
            })

for article in all_articles_upr:
    print(article)

print("\nTotal articles collected:", len(all_articles_upr))