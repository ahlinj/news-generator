import requests
from bs4 import BeautifulSoup

URL = "https://www.upr.si/si/o-univerzi/t4eu-/t4eu-priloznosti-/za-zaposlene/"

all_articles_upr = []

response = requests.get(URL)
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