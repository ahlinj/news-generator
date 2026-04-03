import requests

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
  "important_links": string[]
}}

Article:

From 16 to 20 March 2026, Universidade Católica Portuguesa, Porto Campus, will host the T4EU Common European Heritage Week, in collaboration with Porto GLAM sector stakeholders. Under the theme HERITAGE FUTURE(S) / FUTURE HERITAGE(S): ON THE THRESHOLD OF CHANGE, the week will bring together scholars, practitioners, and students for an intensive programme of training activities, including workshops, public lectures, a roundtable, and a scientific conference.\n\nThe central theme invites us to consider the future(s) of heritage and the heritage(s) of the future: How will our actions today shape our shared tomorrow? What new responsibilities arise as we face rapid ecological, technological, and social transformations? Are our decisions ensuring the sustainability of heritage ecosystems?\n\nThe programme, to be announced shortly, includes a T4EU Transformative Heritage Workshop, T4EU Regional Sustainable Heritage Workshops, an Artist Talk, Public Events with Regional Stakeholders and a enriching social and cultural programme, with a networking dinner with regional stakeholders, city walks, and guided museum visits.\n\nCornelius Holtorf, from the Linnaeus University (UNESCO), Paulo Lourenço, from University of Minho, and Roberta Altin, from University of Trieste are the keynote speakers.\n\nIntegrated in this week, the Annual T4EU Sustainable Heritage Conference will also take place, from 18 to 20 March. This important conference will be jointly organized with EPoCH2026 – the third edition of the international annual conference of the Heritage and Conservation-Restoration research area of CITAR, Católica, offering a unique platform to explore critical reflections and experimental practices in conservation-restoration and heritage studies within the European context.\n\nFrom material care to digital memory, from endangered traditions to emerging sustainable solutions and cultural forms, we will be challenged to critically reflect on the evolving landscapes and to imagine new configurations of practice, ethics, and responsibility – on the threshold of change.
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


if __name__ == "__main__":
    response = requests.post(
        url,
        json=payload,
    )
    print(response.json())
