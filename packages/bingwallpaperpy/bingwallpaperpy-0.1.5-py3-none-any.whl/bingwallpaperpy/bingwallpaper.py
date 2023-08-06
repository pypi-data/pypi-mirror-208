from PIL import Image
from io import BytesIO
from pathlib import Path
import requests
import xml.etree.ElementTree as ET

MARKET = "de-DE"
OFFSET = "0"
COUNT = "1"
BASE_URL = "https://www.bing.com"
URL = f"{BASE_URL}/HPImageArchive.aspx?format=xml&idx={OFFSET}&n={COUNT}&mkt={MARKET}"
DEST_DIR = (
    Path.home() / "Downloads" if (Path.home() / "Downloads").exists() else Path("/tmp")
)
DEST_FN = "bingwallpaper.png"
DEST = DEST_DIR / DEST_FN


def download():
    '''Download today's Bing wallpaper.'''
    resp = requests.get(URL)
    if resp.ok:
        xml = ET.fromstring(resp.content)
        img_url = xml.find("./image/url").text
        print(BASE_URL + img_url)
        resp = requests.get(BASE_URL + img_url)
        if resp.ok:
            img = Image.open(BytesIO(resp.content))
            img.save(DEST)
            print(DEST)
