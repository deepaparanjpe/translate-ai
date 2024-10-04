rom flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from googletrans import Translator

# Initialize Flask app and Translator
app = Flask(__name__)
translator = Translator()

# Function to extract text from a URL
def extract_text_from_url(url):
    try:
        # Fetch the content of the URL
        response = requests.get(url, timeout=10)  # Add timeout for better handling
        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            return None, f"Failed to fetch URL: {response.status_code}"

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text from the parsed HTML
        text = soup.get_text(separator=' ', strip=True)

        if not text:
            return None, "No text found on the page."

        return text, None
    except requests.exceptions.RequestException as e:
        return None, str(e)

# Route to translate the content of a given URL
@app.route('/translate-url', methods=['POST'])
def translate_url():
    data = request.get_json()

    # Check if the required fields are present in the request
    if not data or 'url' not in data or 'target_lang' not in data:
        return jsonify({"error": "Please provide 'url' and 'target_lang' in the request body"}), 400

    url = data['url']
    target_lang = data['target_lang']

    # Extract text from the given URL
    text, error = extract_text_from_url(url)

    if error:
        return jsonify({"error": error}), 500

    try:
        # Translate the extracted text
        text = text[:1000]
        translation = translator.translate(text, dest=target_lang)
        return jsonify({"original_text": text, "translated_text": translation.text, "target_lang": target_lang}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Home route to check service status
@app.route('/')
def index():
    return "URL Translation service is running!"

if __name__ == '__main__':
    app.run(debug=True)
