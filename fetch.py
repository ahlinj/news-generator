import requests
from bs4 import BeautifulSoup


BASE_URL = "https://transform4europe.eu/news/"
MAX_PAGE = 62

all_articles = []

for page in range(1, MAX_PAGE + 1):
    # Construct page URL
    if page == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}{page}"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

   # find all h3 elements with that elementor-post__title class
    for h3 in soup.find_all("h3", class_="elementor-post__title"):
        # get a link inside the h3
        a = h3.find("a")
        if a and a.get("href"):
            all_articles.append({
                "title": a.get_text(strip=True),
                "link": a["href"]
            })

print("\nTotal articles collected:", len(all_articles))

for article in all_articles:
    print(article)

# upr

#url2="https://www.upr.si/si/o-univerzi/t4eu-/t4eu-novice/pomlad-trajnostnega-razvoja-"

#response2 = requests.get(url2)

#print(response2.text)

