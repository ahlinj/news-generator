import requests
from bs4 import BeautifulSoup


BASE_URL = "https://transform4europe.eu/news/"
MAX_PAGE = 62

all_articles_t4eu = []

def extract_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # article container
    container = soup.find("div", attrs={"data-elementor-type": "single-post"})
    
    if container is None:
        container = soup.find("div", attrs={"data-elementor-type": "single-page"})
    
    # extract all text (paragraphs, headers, links)
    full_text = container.get_text(separator="\n", strip=True)

    return full_text


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
            all_articles_t4eu.append({
                "title": a.get_text(strip=True),
                "link": a["href"]
            })

for article in all_articles_t4eu:
    article["content"] = extract_content(article["link"])
    print(article["content"])
