import requests
import json
from bs4 import BeautifulSoup

BASE_URL = "https://www.upr.si/si/o-univerzi/"

def extract_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # article container
    container = soup.find("div", attrs={"class": "block-courses_details block-courses_details_full P30 bg-0 padding-top-15"})
    
    # extract all text (paragraphs, headers, links)
    full_text = container.get_text(separator="\n", strip=True)

    return full_text


def get_articles():
    articles = []

    url_suffixes = [
        "t4eu-/t4eu-priloznosti-/za-zaposlene/",
        "t4eu-/t4eu-priloznosti-/za-studente-/",
        "t4eu-novice/p/1",
        "t4eu-novice/p/2",
        "t4eu-/arhiv-preteklih-priloznosti-t4eu-/p/1",
        "t4eu-/arhiv-preteklih-priloznosti-t4eu-/p/2"
    ]

    with open("logs.json") as f:
        logs = json.load(f)
        last_link_priloznosti_za_studente = logs.get("last_priloznosti_za_studente_link")
        last_link_priloznosti_za_zaposlene = logs.get("last_priloznosti_za_zaposlene_link")
        last_link_novice = logs.get("last_novice_link")

    for suffix in url_suffixes:
        first = True

        match suffix:
            case "t4eu-/t4eu-priloznosti-/za-studente-/":
                last_link = last_link_priloznosti_za_studente
                json_key = "last_priloznosti_za_studente_link"
            case "t4eu-/t4eu-priloznosti-/za-zaposlene/":
                last_link = last_link_priloznosti_za_zaposlene
                json_key = "last_priloznosti_za_zaposlene_link"
            case "t4eu-novice/p/1":
                last_link = last_link_novice
                json_key = "last_novice_link"

        url = BASE_URL + suffix
        soup = BeautifulSoup(requests.get(url).text, "html.parser")

        for div in soup.find_all("div", class_="column-description P30 bg-2 resizable"):
            a = div.find("a")
            if a and a.get("href"):
                link = a.get("href")

                if link.startswith("/si/o-univerzi/"):
                    link = "https://www.upr.si" + link
                else:
                    link = "https://www.upr.si/si/o-univerzi/t4eu-novice/p/" + link

                if last_link == link:
                    if json_key == "last_novice_link":
                        for article in articles:
                            article["content"] = extract_content(article["link"])
                        return articles
                    stop_suffix = True
                    break
                else:
                    if first:
                        first = False
                        logs[json_key] = link
                        with open("logs.json", "w") as f:
                            json.dump(logs, f)
                    articles.append({
                        "title": a.find("h5").get_text(strip=True),
                        "link": link
                    })

        if stop_suffix:
            continue

    for article in articles:
        article["content"] = extract_content(article["link"])

    return articles


if __name__ == "__main__":
    get_articles()