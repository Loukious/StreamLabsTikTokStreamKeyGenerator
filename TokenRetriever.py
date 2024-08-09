import gzip
import seleniumwire.undetected_chromedriver as uc
import json
import requests
from urllib.parse import urlparse, parse_qs
import hashlib
import os
import base64

class TokenRetriever:
    CLIENT_KEY = "awdjaq9ide8ofrtz"
    REDIRECT_URI = "https://streamlabs.com/tiktok/auth"
    STATE = ""
    SCOPE = "user.info.basic,live.room.info,live.room.manage,user.info.profile,user.info.stats"
    STREAMLABS_API_URL = "https://streamlabs.com/api/v5/auth/data"

    def __init__(self, cookies_file='cookies.json'):
        self.code_verifier = self.generate_code_verifier()
        self.code_challenge = self.generate_code_challenge(self.code_verifier)
        self.streamlabs_auth_url = (
            f"https://streamlabs.com/m/login?force_verify=1&external=mobile&skip_splash=1&tiktok&code_challenge={self.code_challenge}"
        )
        self.cookies_file = cookies_file
        self.driver = None

    @staticmethod
    def generate_code_verifier():
        return base64.urlsafe_b64encode(os.urandom(64)).decode('utf-8').rstrip('=')

    @staticmethod
    def generate_code_challenge(code_verifier):
        sha256 = hashlib.sha256()
        sha256.update(code_verifier.encode('utf-8'))
        return base64.urlsafe_b64encode(sha256.digest()).decode('utf-8').rstrip('=')

    def load_cookies(self, driver):
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)

    def retrieve_token(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
        chrome_options.add_argument("--disable-web-security")  # Disable web security
        chrome_options.add_argument("--allow-running-insecure-content")  # Allow insecure content

        self.driver = uc.Chrome(options=chrome_options)
        self.driver.get("https://www.tiktok.com")  # Load a page first before setting cookies
        self.load_cookies(self.driver)
        self.driver.get(self.streamlabs_auth_url)

        try:
            request = self.driver.wait_for_request('https://www.tiktok.com/passport/open/web/auth/v2/', timeout=600)
            if request:
                decompressed_body = gzip.decompress(request.response.body)
                response_body = decompressed_body.decode('utf-8')
                data = json.loads(response_body)

                redirect_url = data.get('redirect_url')
                if redirect_url:
                    with requests.session() as s:
                        s.get(redirect_url)
                    parsed_url = urlparse(redirect_url)
                    auth_code = parse_qs(parsed_url.query).get('code', [None])[0]
                else:
                    print("No redirect_url found in the response.")
                    return None
            else:
                print("No request intercepted or timeout reached.")
                return None

        finally:
            try:
                self.driver.close()
            except Exception as e:
                print(f"Error closing browser: {e}")

        if auth_code:
            try:
                import time
                token_request_url = f"{self.STREAMLABS_API_URL}?code_verifier={self.code_verifier}&code={auth_code}"
                time.sleep(3)  # Wait a few seconds before sending the request
                response = requests.get(token_request_url).json()
                if response["success"]:
                    return response["data"]["oauth_token"]
            except:
                print("Failed to obtain token.")
                return None

        print("Failed to obtain authorization code.")
        return None
