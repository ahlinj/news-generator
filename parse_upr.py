import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.upr.si/si/o-univerzi/"

all_articles_upr = []

def extract_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # article container
    container = soup.find("div", attrs={"class": "block-courses_details block-courses_details_full P30 bg-0 padding-top-15"})
    
    # extract all text (paragraphs, headers, links)
    full_text = container.get_text(separator="\n", strip=True)

    return full_text


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
            link = a.get("href")

            if link.startswith("/si/o-univerzi/"):
                link = "https://www.upr.si" + link
            else:
                link = "https://www.upr.si/si/o-univerzi/t4eu-novice/p/" + link
        
            all_articles_upr.append({
                "title": title.get_text(strip=True),
                "link": link
            })

for article in all_articles_upr:
    article["content"] = extract_content(article["link"])
    print(article["content"])
