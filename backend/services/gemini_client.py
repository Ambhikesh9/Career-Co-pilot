import os
import google.generativeai as genai
from dotenv import load_dotenv
# Import specific errors
from google.api_core.exceptions import ResourceExhausted, InternalServerError
import time

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment (.env)")

genai.configure(api_key=API_KEY)

def generate_text(prompt: str, model_name: str = "gemini-2.5-pro"):
    """
    Handles API call with error handling, content block checks, and retry logic.
    """
    model = genai.GenerativeModel(model_name)
    
    try:
        response = model.generate_content(prompt)
        
        # --- NEW: Check if the response was blocked or empty ---
        if not response.parts:
            feedback = response.prompt_feedback
            block_reason = feedback.block_reason
            safety_ratings = str(feedback.safety_ratings)
            
            print(f"API call blocked. Reason: {block_reason}")
            # Return a clear error to the frontend
            return f"Error: Content blocked by API. Reason: {block_reason}. Ratings: {safety_ratings}"

        # --- NEW: Safer text access ---
        try:
            return response.text
        except ValueError as ve:
            # This can happen if .text is not available even if parts exist
            print(f"ValueError accessing response.text: {ve}")
            return f"Error: Failed to access response text. Full feedback: {response.prompt_feedback}"
        # ----------------------------------------

    except ResourceExhausted as e:
        print("Rate limit hit. Waiting 60 seconds...")
        time.sleep(60)
        try:
            # Retry once after waiting
            response = model.generate_content(prompt)
            if not response.parts:
                return f"Error: Content blocked on retry. Reason: {response.prompt_feedback.block_reason}"
            return response.text
        except Exception as e2:
            print(f"An unexpected error occurred on retry: {e2}")
            return f"Error on retry: {e2}"
    
    except InternalServerError as e:
        # Handle if Google has an internal error
        print(f"Google Internal Server Error: {e}")
        return f"Error: The remote API (Gemini) had an internal server error. Please try again later. Details: {e}"

    except Exception as e:
        # Catch any other unexpected error
        print(f"An unexpected error occurred: {e}")
        return f"Error: An unexpected client-side error occurred. Details: {str(e)}"