from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "csebuetnlp/mT5_multilingual_XLSum"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)



def generate_summary(article):
    prompt = (
        "summarize: "
        f"{article['title']}\n\n{article['content']}"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048
    )

    output_ids = model.generate(
        **inputs,
        max_length=800,
        num_beams=4,
        early_stopping=True
    )

    return tokenizer.decode(output_ids[0], skip_special_tokens=True)

if __name__ == "__main__":
    article = {
        "title": "Mathematical methods and models in support of digital transformation",
        "content": """Join an interdisciplinary section within the framework of the traditional Spring Scientific Session at Sofia University St. Kliment Ohridski

28 and 29 March 2026 | Sofia University, Bulgaria

Home » News » Mathematical methods and models in support of digital transformation

About
Transform4Europe Alliance is pleased to invite you to join the interdisciplinary section ‘Mathematical Methods and Models in Support of Digital Transformation’ within the framework of the Spring Scientific Session of the Faculty of Mathematics and Informatics (FMI) of Sofia University ‘St. Kliment Ohridski’.

The event is organised during the year of the rotating presidency of the Transform4Europe alliance by Sofia University and aims to promote interdisciplinary exchange and cooperation between the partners in the Alliance.

All representatives of the academic community and Alliance partners can express interest in participating in the event by submitting an abstract through the scientific session’s electronic system.

The Spring Scientific Session will be held on 28 and 29 March 2026 (Saturday and Sunday) at the Faculty of Mathematics and Informatics of Sofia University “St. Kliment Ohridski”. The reports in the ‘Mathematical Methods and Models in Support of Digital Transformation’ section will be presented on 29 March 2026.

The forum will be dedicated to discussing policies and results related to the development and implementation of new mathematical methods and models for ensuring the quality, security, and effective use of data as a foundation for the digital transformation of the economy and the public sector.

The emphasis in the agenda will be put on innovative approaches and good practices for the effective and responsible implementation of intelligent software agents across various areas of public life.

Important dates:

Abstracts of reports must be submitted through the electronic system of the scientific session by 22 February 2026.
Participants whose reports have been approved will be notified by 14 March 2026.
The Spring Science Session will be held on 28 and 29 March 2026.
The reports in the specialised section of Transform4Europe will be presented on 29 March 2026.

The official language of the event is English.

Full information about the event is available on the official website of the FMI Spring Scientific Session: https://www.fmi.uni-sofia.bg/bg/proletna-nauchna-sesiya-na-fmi-2026

For further questions:

Assoc. Prof. Dafina Petkova, PhD

Vice-dean Master’s Degree Programs, Mobility

Faculty of Mathematics and Informatics,

Sofia University “St. Kliment Ohridski”

email: dafinaz@fmi.uni-sofia.bg

Participation in the ‘Mathematical methods and models in support of digital transformation’ section may be partially funded by the European Union. However, the views and opinions expressed belong to the author(s) and do not necessarily reflect those of the European Union or the European Executive Agency for Education and Culture (EACEA). Neither the European Union nor the EACEA can be held responsible for these views and opinions.

"""
    }
    print("Summary: " + generate_summary(article))