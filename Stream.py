import requests


class Stream:
    def __init__(self, token):
        self.s = requests.session()
        self.s.headers.update({
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) StreamlabsDesktop/1.17.0 Chrome/122.0.6261.156 Electron/29.3.1 Safari/537.36",
            "authorization": f"Bearer {token}"
        })

    def search(self, game):
        if not game:
            return []
        game = game[:25] # If the game name exceeds 25 characters, the API will return error 500
        url = f"https://streamlabs.com/api/v5/slobs/tiktok/info?category={game}"
        info = self.s.get(url).json()
        info["categories"].append({"full_name": "Other", "game_mask_id": ""})
        return info["categories"]

    def start(self, title, category, audience_type='0'):
        url = "https://streamlabs.com/api/v5/slobs/tiktok/stream/start"
        files=(
            ('title', (None, title)),
            ('device_platform', (None, 'win32')),
            ('category', (None, category)),
            ('audience_type', (None, audience_type)),
        )
        response = self.s.post(url, files=files).json()
        try:
            self.id = response["id"]
            return response["rtmp"], response["key"]
        except KeyError:
            print("Error: ", response)
            return None, None

    def end(self):
        url = f"https://streamlabs.com/api/v5/slobs/tiktok/stream/{self.id}/end"
        response = self.s.post(url).json()
        return response["success"]
    
    def getInfo(self):
        url = "https://streamlabs.com/api/v5/slobs/tiktok/info"
        response = self.s.get(url).json()
        return response