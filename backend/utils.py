import requests
from bs4 import BeautifulSoup
import pytesseract
from PIL import Image


# 🌐 Extract text from URL
def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = soup.find_all("p")
    text = " ".join([p.get_text() for p in paragraphs])

    return text


# 🖼️ Extract text from image
def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text