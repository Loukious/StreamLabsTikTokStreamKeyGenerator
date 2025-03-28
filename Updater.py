from _version import __version__
from packaging import version
import requests


class VersionChecker:
    REPO = "Loukious/StreamlabsTikTokStreamKeyGenerator"
    
    @classmethod
    def check_update(cls):
        try:
            response = requests.get(
                f"https://api.github.com/repos/{cls.REPO}/releases/latest",
                timeout=5
            )
            release = response.json()
            latest = release["tag_name"].lstrip('v')
            
            if version.parse(latest) > version.parse(__version__):
                return {
                    "current": __version__,
                    "latest": latest,
                    "url": release["html_url"],
                    "notes": release.get("body", "")
                }
        except Exception:
            return None