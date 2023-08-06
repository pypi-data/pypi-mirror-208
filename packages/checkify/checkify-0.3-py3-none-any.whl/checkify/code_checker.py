import os
import openai
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv('OPENAI_API_KEY')

def check_code(code):
    # Set up the GPT API credentials
    openai.api_key = api_key

    # Call the GPT API to check the code and get the response
    response = openai.Completion.create(
        engine='davinci-codex',
        prompt=code,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.8,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        log_level='info'
    )

    # Extract and return the generated explanation
    explanation = response.choices[0].text.strip()
    return explanation
