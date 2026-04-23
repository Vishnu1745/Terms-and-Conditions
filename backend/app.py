from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os

from summarizer import summarize_text, detect_risks, highlight_risks
from utils import extract_text_from_image, extract_text_from_url, extract_text_from_pdf

app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Risk Level Function
def get_risk_level(score):
    if score <= 3:
        return "Low"
    elif score <= 6:
        return "Medium"
    else:
        return "High"


# 🚀 MAIN MULTI-INPUT API
@app.post("/analyze")
async def analyze(
    text: str = Form(None),
    url: str = Form(None),
    file: UploadFile = File(None)
):
    final_text = ""

    try:
        # 🔹 TEXT INPUT
        if text:
            final_text = text

        # 🔹 URL INPUT
        elif url:
            final_text = extract_text_from_url(url)

        # 🔹 FILE INPUT (IMAGE / PDF)
        elif file:
            filename = file.filename.lower()
            temp_path = "temp_file"

            # Save file temporarily
            with open(temp_path, "wb") as f:
                f.write(await file.read())

            # IMAGE
            if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
                final_text = extract_text_from_image(temp_path)

            # PDF
            elif filename.endswith(".pdf"):
                final_text = extract_text_from_pdf(temp_path)

            else:
                return {"error": "Unsupported file type"}

            # Clean up
            os.remove(temp_path)

        else:
            return {"error": "No input provided"}

        # 🔹 NLP PROCESSING
        summary = summarize_text(final_text)
        risks, score = detect_risks(final_text)
        highlights = highlight_risks(final_text)

        return {
            "summary": summary,
            "risks": risks,
            "risk_score": score,
            "risk_level": get_risk_level(score),
            "highlights": highlights
        }

    except Exception as e:
        return {"error": str(e)}


# ✅ HEALTH CHECK
@app.get("/")
def home():
    return {"message": "AI Terms Analyzer API is running"}