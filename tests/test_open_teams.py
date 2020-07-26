import pytest
import requests
from src.flaskapp.util import login

api_url = ""


def test_missing_token():
    email = "test1@gmail.com"
    token = ""
    data_dic = {"email": email, "token": token}
    resp = requests.get(api_url + "/open-teams", json=data_dic).json()
    assert resp["statusCode"] == 408


def test_bad_token():
    email = "test1@gmail.com"
    token = login(email, "test")
    data_dic = {"email": email, "token": token}
    resp = requests.get(api_url + "/open-teams", json=data_dic).json()
    assert resp["statusCode"] == 404


def test_no_open_team():
    pass


def test_return_open_team():
    pass


if __name__ == '__main__':
    pytest.main()