import os
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI
from datetime import datetime
import json
import pickle
load_dotenv()

class DebateEvaluation(BaseModel):
    content_analysis: str
    problematic_usage_patterns: str
    problematic_usage_patterns_issues: str
    problematic_usage_patterns_description: str
    proble
    recommendations: str
    recommendations_suggestions: str
    
    total_points: int
    comments: str

'''
{
  "content_analysis": {
    "word_cloud_image": "https://example.com/wordcloud.png", 
    "summary": "This section provides an analysis of the content you have watched over time, including trends and preferences."
  },
  "problematic_usage_patterns": {
    "issues": [
      {
        "issue": "Excessive binge-watching late at night",
        "description": "You've been watching more than 5 hours of content between 12 AM and 4 AM consistently over the last month."
      },
      {
        "issue": "Frequent exposure to triggering topics",
        "description": "You've been watching content that includes violence and disturbing themes multiple times per week."
      }
    ]
  },
  "recommendations": {
    "suggestions": [
      {
        "recommendation": "Set a viewing limit",
        "details": "Consider setting an automatic reminder to stop watching after 2 hours of late-night sessions."
      },
      {
        "recommendation": "Explore calming or uplifting content",
        "details": "Watch content that promotes relaxation or positive themes to counterbalance disturbing topics."
      }
    ]



'''


# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

