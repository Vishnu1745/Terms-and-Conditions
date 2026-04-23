import requests
from bs4 import BeautifulSoup
import pytesseract
from PIL import Image
import io

# Try pdfplumber first (better extraction), fall back to PyPDF2
try:
    import pdfplumber
    USE_PDFPLUMBER = True
except ImportError:
    import PyPDF2
    USE_PDFPLUMBER = False

# ✅ Set correct Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"E:/terms-summarizer/tesseract/tesseract.exe"


# 🌐 Extract text from URL
def extract_text_from_url(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts, styles, nav, footer etc.
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Try to grab article/main content first
    main = soup.find("main") or soup.find("article") or soup.find(id="content") or soup.body
    paragraphs = main.find_all(["p", "li", "h2", "h3"]) if main else soup.find_all("p")

    text = " ".join(el.get_text(separator=" ").strip() for el in paragraphs if el.get_text(strip=True))

    if not text.strip():
        raise ValueError("Could not extract text from this URL. The page may require JavaScript.")

    return text


# 🖼️ Extract text from image using Tesseract OCR
def extract_text_from_image(image_path: str) -> str:
    img = Image.open(image_path)

    # Improve OCR accuracy — convert to grayscale, scale up
    img = img.convert("L")
    w, h = img.size
    if w < 1000:
        img = img.resize((w * 2, h * 2), Image.LANCZOS)

    text = pytesseract.image_to_string(img, config="--psm 6")

    if not text.strip():
        raise ValueError("Could not extract text from image. Make sure the image contains readable text.")

    return text


# 📄 Extract text from PDF
def extract_text_from_pdf(path: str) -> str:
    text = ""

    if USE_PDFPLUMBER:
        # pdfplumber — much better for modern PDFs
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    else:
        # PyPDF2 fallback
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

    if not text.strip():
        raise ValueError(
            "Could not extract text from PDF. The PDF may be image-based — "
            "try uploading it as an image (PNG/JPG) for OCR processing."
        )

    return text.strip()