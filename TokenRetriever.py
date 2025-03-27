import time
from seleniumbase import SB
from selenium.webdriver.support.ui import WebDriverWait
import json
import requests
import hashlib
import os
import base64

class TokenRetriever:
    CLIENT_KEY = "awdjaq9ide8ofrtz"
    REDIRECT_URI = "https://streamlabs.com/tiktok/auth"
    STREAMLABS_API_URL = "https://streamlabs.com/api/v5/slobs/auth/data"

    def __init__(self, cookies_file='cookies.json'):
        self.code_verifier = self.generate_code_verifier()
        self.code_challenge = self.generate_code_challenge(self.code_verifier)
        self.streamlabs_auth_url = (
            f"https://streamlabs.com/m/login?"
            f"force_verify=1&external=mobile&skip_splash=1&tiktok"
            f"&code_challenge={self.code_challenge}"
        )
        self.cookies_file = cookies_file
        self.auth_code = None

    @staticmethod
    def generate_code_verifier():
        return os.urandom(64).hex()

    @staticmethod
    def generate_code_challenge(code_verifier):
        sha256_hash = hashlib.sha256(code_verifier.encode()).digest()
        return base64.urlsafe_b64encode(sha256_hash).decode("utf-8").rstrip("=")

    def load_cookies(self, driver):
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)

    def retrieve_token(self):
        with SB(uc=True, headless=False) as sb:
            sb.open("https://www.tiktok.com/transparency")
            self.load_cookies(sb)

            sb.open(self.streamlabs_auth_url)

            try:
                wait = WebDriverWait(sb, 600)
                wait.until(lambda sb: "success=true" in sb.get_current_url())
            except:
                print("Failed to authorize TikTok.")
                return None
        
        params = {
            'client_key': self.CLIENT_KEY,
            'scope': 'user.info.basic,live.room.tag,live.room.info,live.room.manage,user.info.profile,user.info.stats',
            'aid': '1459',
            'redirect_uri': self.REDIRECT_URI,
            'source': 'web',
            'response_type': 'code'
        }
        with requests.Session() as s:
            try:
                time.sleep(5)
                params= {
                    "code_verifier": self.code_verifier
                }
                response = s.get(self.STREAMLABS_API_URL, params=params)
                if response.status_code != 200:
                    print(f"Bad response: {response.status_code} - {response.text}")
                    return None
                    
                try:
                    resp_json = response.json()
                except json.JSONDecodeError:
                    print("Invalid JSON response. Status code:", response.status_code)
                    return None
                if resp_json.get("success"):
                    token = resp_json["data"].get("oauth_token")
                    print(f"Got Streamlabs OAuth token: {token}")
                    return token
                else:
                    print("Streamlabs token request failed:", resp_json)
                    return None
            except Exception as e:
                print("Error requesting token from Streamlabs:", e)
                return None
        return None