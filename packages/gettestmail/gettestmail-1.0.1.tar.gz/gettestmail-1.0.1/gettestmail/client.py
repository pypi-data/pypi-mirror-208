import requests
from gettestmail.models import GetTestMail, Problem
from typing import Optional


class APIException(Exception):
    def __init__(self, problem: Problem):
        super().__init__(f"{problem.status} {problem.title}: {problem.detail}")
        self.problem = problem


class GetTestMailClient:
    def __init__(self, api_key: str, base_url: str = "https://gettestmail.com/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def create_new(self, expires_at: Optional[str] = None) -> GetTestMail:
        url = f"{self.base_url}/gettestmail"
        payload = {"expiresAt": expires_at} if expires_at else {}
        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code != 201:
            raise APIException(Problem(**response.json()))

        data = response.json()
        return GetTestMail(**data)

    def wait_for_message(self, id: str) -> GetTestMail:
        url = f"{self.base_url}/gettestmail/{id}"
        response = requests.get(url, headers=self.headers, allow_redirects=True)

        if response.status_code != 200:
            raise APIException(Problem(**response.json()))
        
        data = response.json()
        return GetTestMail(**data)
