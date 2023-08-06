import openai

def check_code(code):
    # Set up the GPT API credentials
    openai.api_key = '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'

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
