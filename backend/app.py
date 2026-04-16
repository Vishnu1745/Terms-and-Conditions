from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from summarizer import summarize_text, detect_risks, highlight_risks

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    text: str

def get_risk_level(score):
    if score <= 3:
        return "Low"
    elif score <= 6:
        return "Medium"
    else:
        return "High"
    
@app.post("/summarize")
def summarize(data: RequestData):
    summary = summarize_text(data.text)
    risks, score = detect_risks(data.text)
    highlights = highlight_risks(data.text)
    return {
        "summary": summary,
        "risks": risks,
        "risk_score": score,
        "risk_level": get_risk_level(score),
        "highlights": highlights
    }


@app.get("/")
def home():
    return {"message": "API running"}