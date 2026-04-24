import json

import requests
from qdrant_client import QdrantClient
from collections import defaultdict
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[.,;:!?]?')

COLLECTION_NAME = "news_articles_2"


client = QdrantClient(host="localhost", port=6333)

def fetch_all_points():
    points = []
    offset = None

    while True:
        batch, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=500,
            with_payload=True,
            with_vectors=False,
            offset=offset
        )

        points.extend(batch)

        if offset is None:
            break

    return points

def group_articles(points):
    articles = defaultdict(list)

    for p in points:
        payload = p.payload
        key = (payload["title"], payload["link"])
        articles[key].append(payload)

    return articles

def get_chunk_id(chunk):
    return chunk["chunk_id"]

def reconstruct_articles(grouped):
    full_articles = []

    for (title, link), chunks in grouped.items():
        sorted_chunks = sorted(chunks, key=get_chunk_id)

        texts = []
        for chunk in sorted_chunks:
            texts.append(chunk["text"])

        full_text = " ".join(texts)

        full_articles.append({
            "title": title,
            "link": link,
            "text": full_text
        })

    return full_articles


def call_llm(url):
    article_html = return_article_html(url)
    if article_html is None:
        return None

    url = "http://hivecore.famnit.upr.si:6666/api/chat"

    prompt = f"""Extract structured information from the following article and return JSON with this schema:

    {{
    "title": string,
    "summary": string (max 3 sentences),
    "suitable_for_doctoral_students": "yes" | "no",
    "field": string,
    "type": "news" | "event",
    "application": {{
        "required": "yes" | "no",
        "link": string | null,
        "deadline": string | null
    }},
    "date_time": string | null,
    "location": {{
        "mode": "onsite" | "online" | "unknown",
        "place": string | null
    }},
    "all_links": string[] | null,
    "image_links": string[] | null,
    "pdf_links": string[] | null,
    "mailto_links": string[] | null
    }}
    
    IMPORTANT:
    - Always extract the URL from the `href` attribute of <a> tags.
    - Do NOT extract the visible text between <a>...</a>.
    - Return the full absolute URL exactly as it appears in `href`.
    - Ignore the following links: ["https://transform4europe.eu/", 
                                        "https://www.facebook.com/Transform4Europe",
                                        "https://www.youtube.com/channel/UCZExnhDJsZEho0d9sIxia0A/videos",
                                        "https://pl.linkedin.com/company/transform4europe",
                                        "https://transform4europe.eu",
                                        "https://www.instagram.com/transform4europe",
                                        "https://transform4europe.eu/category/news/"
                                        ]
    - Do NOT extract the following link from the src of the img element: https://transform4europe.eu/wp-content/uploads/2022/06/Logo_Transform4Europe_officialv2.png

    Article:

    {article_html}
    """

    payload = {
            "model": "hf.co/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:UD-Q4_K_XL",
            "stream": False,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an information extraction system. Always return ONLY valid JSON. Do not include explanations or text outside JSON. Use the exact schema provided."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    
    response = requests.post(
        url,
        json=payload,
    )
    try:
        return response.json()
    except Exception as e:
        print("ERROR: Not valid JSON: ", e)
        print("RAW RESPONSE:", response.text)
        return None

def extract_json(response):
    try:
        content = response["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print("Invalid JSON:", e)
        return None
    
def save_jsonl(data, file_path):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def return_article_html(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    container = soup.find("div", attrs={"data-elementor-type": "single-post"})
    
    if container is None:
        container = soup.find("div", attrs={"data-elementor-type": "single-page"})

    if container is None:
        container = soup.find("div", attrs={"class": "block-courses_details block-courses_details_full P30 bg-0 padding-top-15"})

    return container

def extract_links_soup(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    container = soup.find("div", attrs={"data-elementor-type": "single-post"})
    
    if container is None:
        container = soup.find("div", attrs={"data-elementor-type": "single-page"})

    if container is None:
        container = soup.find("div", attrs={"class": "block-courses_details block-courses_details_full P30 bg-0 padding-top-15"})

    if container is None:
        return ["404 article not found (probably)"], ["404 article not found (probably)"], ["404 article not found (probably)"]
    
    links = []
    image_links = []
    mail_links = set()

    for a in container.find_all("a", href=True):
        href = a["href"]


        ignore_links = ["https://transform4europe.eu/", 
                        "https://www.facebook.com/Transform4Europe",
                        "https://www.youtube.com/channel/UCZExnhDJsZEho0d9sIxia0A/videos",
                        "https://pl.linkedin.com/company/transform4europe",
                        "https://transform4europe.eu",
                        "https://www.instagram.com/transform4europe",
                        "https://transform4europe.eu/category/news/"
                        ]
        
        if href.startswith("/"):
            href = urljoin(url, href)

        if href not in ignore_links:
            links.append(href)

    for img in container.find_all("img"):
        if (src := img.get("src")) and src != "https://transform4europe.eu/wp-content/uploads/2022/06/Logo_Transform4Europe_officialv2.png":
            image_links.append(src)

    for text in container.stripped_strings:
        for match in EMAIL_REGEX.findall(text):
            mail_links.add(match.rstrip(".,;:!?"))

    return links, image_links, list(mail_links)


def is_link_image(links):
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"]
    images = []
    for link in links:
        if any(link.lower().endswith(ext) for ext in image_extensions):
            images.append(link)
    return images

def is_link_pdf(links):
    pdf_links = []
    for link in links:
        if link.lower().endswith(".pdf"):
            pdf_links.append(link)
    return pdf_links

def is_link_mailto(links):
    mailto_links = []
    for link in links:
        if link.lower().startswith("mailto:"):
            mailto_links.append(link)
    return mailto_links

if __name__ == "__main__":
    points = fetch_all_points()
    articles = group_articles(points)
    full_articles = reconstruct_articles(articles)
    i=0
    for article in full_articles:
        links, image_links, mail_links = extract_links_soup(article["link"])
        images = is_link_image(links)
        pdfs = is_link_pdf(links)
        mailto_links = is_link_mailto(links)
        i=i+1
        #extracted = call_llm(article["link"])
        #extracted_data = extract_json(extracted)
        
        result = {
            "title": article["title"],
            "link": article["link"],
            "all_links": links,
            "image_links": image_links+images,
            "pdf_links": pdfs,
            "mailto_links": mailto_links+mail_links,
        }
        
        print(i,"/", len(full_articles))
        save_jsonl(result, "data/extracted_soup_links_filtered_and_img_3.jsonl")