import openai

def check_code(code):
    # Ask the user for their OpenAI API key
    api_key = input("Please enter your OpenAI API key: ")

    try:
        # Set up the GPT API credentials
        openai.api_key = api_key

        # Call the GPT API to check the code and get the response
        response = openai.Completion.create(
            engine='davinci',
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

    except openai.error.AuthenticationError:
        print("Invalid API key. Authentication failed.")
        return None

    except openai.error.OpenAIError as e:
        print("An error occurred while communicating with the OpenAI API:", str(e))
        return None
