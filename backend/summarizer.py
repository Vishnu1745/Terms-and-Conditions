from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "facebook/bart-large-cnn"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def clean_summary(text):
    text = text.replace("  ", " ")
    text = text.strip()
    return text

def summarize_text(text):
    inputs = tokenizer(
        text,
        max_length=1024,
        return_tensors="pt",
        truncation=True
    )

    summary_ids = model.generate(
    inputs["input_ids"],
    max_length=70,
    min_length=20,
    length_penalty=3.5,   # 🔥 stronger compression
    num_beams=8,          # 🔥 better search
    no_repeat_ngram_size=3,  # 🔥 avoids repetition
    early_stopping=True
)

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return clean_summary(summary)
def detect_risks(text):
    risks = []
    score = 0
    text = text.lower()

    if "must not" in text or "prohibited" in text:
        risks.append("⚠️ Strict usage restrictions")
        score += 1

    if "terminate" in text or "suspend" in text:
        risks.append("⚠️ Account can be terminated anytime")
        score += 2

    if "not responsible" in text or "liability" in text:
        risks.append("⚠️ Company avoids responsibility")
        score += 3

    if "without notice" in text:
        risks.append("⚠️ Terms may change without notice")
        score += 2

    if "unauthorized access" in text:
        risks.append("⚠️ User responsible for security")
        score += 2

    if "data" in text and "share" in text:
        risks.append("⚠️ Data may be shared")
        score += 3

    # 🔥 SCALE (0–10)
    max_score = 10
    scaled_score = min(score, max_score)

    return risks, scaled_score

def get_risk_level(score):
    if score <= 3:
        return "Low"
    elif score <= 6:
        return "Medium"
    else:
        return "High"
def highlight_risks(text):
    sentences = text.split(".")
    results = []

    for s in sentences:
        s_lower = s.lower()

        if "terminate" in s_lower:
            results.append({"text": s.strip(), "reason": "Account can be terminated"})

        elif "not responsible" in s_lower or "liability" in s_lower:
            results.append({"text": s.strip(), "reason": "Company avoids responsibility"})

        elif "unauthorized access" in s_lower:
            results.append({"text": s.strip(), "reason": "User responsible for security"})

        elif "must not" in s_lower:
            results.append({"text": s.strip(), "reason": "Strict restrictions applied"})

    return results