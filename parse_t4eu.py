import requests
import json
from bs4 import BeautifulSoup


BASE_URL = "https://transform4europe.eu/news/"
MAX_PAGE = 62

def extract_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # article container
    container = soup.find("div", attrs={"data-elementor-type": "single-post"})
    
    if container is None:
        container = soup.find("div", attrs={"data-elementor-type": "single-page"})
    
    # extract all text (paragraphs, headers, links)
    return container.get_text(separator="\n", strip=True)

def get_articles():
    articles = []
    first = True

    with open("logs.json") as f:
        logs = json.load(f)
    last_link = logs.get("last_t4eu_link")


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
                if last_link == a["href"]:
                    for article in articles:
                        article["content"] = extract_content(article["link"])
                    return articles
                else:
                    if first:
                        first = False
                        logs["last_t4eu_link"] = a["href"]
                        with open("logs.json", "w") as f:
                            json.dump(logs, f)
                    articles.append({
                        "title": a.get_text(strip=True),
                        "link": a["href"]
                    })

    for article in articles:
        article["content"] = extract_content(article["link"])

    return articles
