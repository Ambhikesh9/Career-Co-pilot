import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment (.env)")

genai.configure(api_key=API_KEY)

# small helper — call model and return text
def generate_text(prompt: str, model_name: str = "gemini-2.5-pro"):
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    # response may have text in .text
    return response.text if hasattr(response, "text") else str(response)
