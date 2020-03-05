import json
import requests

def test_profile():
    #GET
    #Create Profile
    url = "http://127.0.0.1:5000/profile"
    response = requests.get(url)
    assert response.status_code == 200

    #POST
    #No Skills Section and "skills" misspelled
    x = '{"skill" : ""}'
    input = json.loads(x)
    response = requests.post(url, json = input)
    assert response.status_code == 400

    #Prizes field with no prizes
    x = '{"prizes": " "}'
    input = json.loads(x)
    response = requests.post(url, json=input)
    assert response.status_code == 400 #Prizes are Optional

    #Valid Post
    x = '{"skills" : "XYZ Language", "prizes" : "ABC Prize"}'
    input = json.loads(x)
    response = requests.post(url, json=input)
    assert response.status_code == 200

    #Resetting to initial State
    x = '{"skills": "No Language", "prizes": " "}'
    input = json.loads(x)
    response = requests.post(url, json=input)
    assert response.status_code == 200



