# config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///job_candidate_manager.db')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    # Add other configurations as needed
