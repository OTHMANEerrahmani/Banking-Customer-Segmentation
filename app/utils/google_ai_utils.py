import google.generativeai as genai
import os
import logging
import json
from google.api_core import exceptions


def check_api_key() -> bool:
    """Checks if the Google API key is set in the environment."""
    return "GOOGLE_API_KEY" in os.environ and os.environ["GOOGLE_API_KEY"] != ""


def configure_genai():
    """Configures the Generative AI model."""
    if not check_api_key():
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def generate_cluster_insights(cluster_profiles: dict) -> dict:
    """Generates marketing insights and personas for customer clusters using Google's Gemini model."""
    configure_genai()
    model = genai.GenerativeModel("gemini-2.5-flash")
    summary_df_data = cluster_profiles.get("summary_df", {})
    distinguishing_features = {
        k: v["distinguishing_features"]
        for k, v in cluster_profiles.items()
        if k not in ["summary_df", "feature_names"]
    }
    prompt = f"As a senior marketing analyst, you have been given customer segmentation data. Your task is to provide actionable marketing insights and create customer personas.\n\nDATA PROVIDED:\n1.  **Cluster Feature Averages**: A summary of the average values for key features within each customer cluster.\n    {json.dumps(summary_df_data, indent=2)}\n    \n2.  **Top Distinguishing Features**: The top 3 features that make each cluster unique compared to the average customer.\n    {json.dumps(distinguishing_features, indent=2)}\n\nYOUR TASK (Respond in valid JSON format):\nBased on the provided data, generate the following:\n1.  **marketing_recommendations**: A single, overarching summary of actionable marketing strategies. Address how to target these different segments. Be specific. For example, 'Target Cluster 0 with loyalty programs, as they have high tenure but low recent spending. Engage Cluster 2 with introductory offers, as they are new customers with high income.'\n2.  **personas**: A detailed persona for each cluster. For each cluster, provide a descriptive name (e.g., 'Loyal Savers', 'High-Value Spenders'), a short paragraph describing their likely characteristics, and 2-3 bullet points of their key traits.\n\nEnsure your entire output is a single, valid JSON object with keys 'marketing_recommendations' and 'personas'. Do not include any text outside of the JSON block.\n\nExample Persona Structure:\n"
    try:
        logging.info("Generating AI insights with prompt...")
        response = model.generate_content(prompt, request_options={"timeout": 60})
        cleaned_response = response.text.strip().replace("`", "").replace("json", "")
        logging.info("Successfully received and cleaned AI response.")
        return json.loads(cleaned_response)
    except exceptions.PermissionDenied as e:
        logging.exception(f"Google AI Permission Denied: {e}")
        return {
            "error": "API Permission Denied",
            "marketing_recommendations": "Could not generate AI recommendations. The Google Generative Language API is not enabled for your project. Please enable it in your Google Cloud Console and try again.",
        }
    except Exception as e:
        logging.exception(f"Error generating AI insights: {e}")
        return {
            "error": "Generation Failed",
            "marketing_recommendations": f"Could not generate AI recommendations. An unexpected error occurred: {str(e)}",
        }