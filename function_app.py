import azure.functions as func
import requests
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Create a single function app instance
app = func.FunctionApp()

# Define one route, handle both functionalities in a single function
@app.route(route="HttpTrigger", auth_level=func.AuthLevel.ANONYMOUS)
def HttpTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request.')

    # Check if repo URL is provided
    repo_url = req.params.get('repoUrl')
    if repo_url:
        try:
            # Fetch Golang code from Stash URL
            response = requests.get(repo_url)
            logging.info(f"Fetched code from stash: {response.text}")
            code = response.text

            # Call GPT-3.5 to generate documentation
            openai_api_url = 'https://api.openai.com/v1/chat/completions'
            headers = {
                'Authorization': f'Bearer {openai_api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': f'Generate documentation for the following Golang code:\n{code}'}
                ],
                'max_tokens': 250
            }
            gpt_response = requests.post(openai_api_url, headers=headers, json=data)
            logging.info(f"GPT-3.5 response: {gpt_response.text}")
            doc_text = gpt_response.json()['choices'][0]['message']['content']

            return func.HttpResponse(doc_text)

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            return func.HttpResponse("Error fetching code or generating documentation", status_code=500)

    # Fallback if repoUrl is not provided, use name-based response
    name = req.params.get('name')
    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name or repoUrl in the query string for a personalized response.",
            status_code=200
        )