import requests
from bs4 import BeautifulSoup

url = "https://transform4europe.eu/news/"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

results = []

# find all h3 elements with that elementor-post__title class
for h3 in soup.find_all("h3", class_="elementor-post__title"):
    # get a link inside the h3
    a = h3.find("a")
    if a and a.get("href"):
        results.append({
            "title": a.get_text(strip=True),
            "link": a["href"]
        })

for r in results:
    print(r)

# upr

#url2="https://www.upr.si/si/o-univerzi/t4eu-/t4eu-novice/pomlad-trajnostnega-razvoja-"

#response2 = requests.get(url2)

#print(response2.text)

