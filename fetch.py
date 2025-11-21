import requests

# test

# t4eu

url = "https://transform4europe.eu/science-communication-workshop-abstract-accepted-and-now-what/"

response = requests.get(url)

print(response.text)     

# upr

url2="https://www.upr.si/si/o-univerzi/t4eu-/t4eu-novice/pomlad-trajnostnega-razvoja-"

response2 = requests.get(url2)

print(response2.text)

