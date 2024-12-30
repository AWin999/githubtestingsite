from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logger.error("No OpenAI API key found in environment variables")
    raise ValueError("OpenAI API key not found")

client = OpenAI(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process-query', methods=['POST'])
def process_query():
    try:
        # Log incoming request
        logger.debug(f"Received request: {request.json}")
        
        # Validate request
        if not request.json:
            logger.error("No JSON data in request")
            return jsonify({'error': 'No JSON data provided'}), 400
        
        user_input = request.json.get('query')
        if not user_input:
            logger.error("No query field in JSON data")
            return jsonify({'error': 'No query provided'}), 400
        
        logger.debug(f"Processing query: {user_input}")
        
        # Query OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Changed from "gpt-3.5-turbo" to "gpt-4 turbo"
            messages=[
                {"role": "user", "content": user_input}
            ]
        )
        
        logger.debug("Successfully received OpenAI response")
        
        ai_response = response.choices[0].message.content
        
        # Simple recommendation logic
        recommendations = []
        if "travel" in user_input.lower():
            recommendations = ["Top 10 Travel Destinations", "How to Save for a Trip"]
        elif "finance" in user_input.lower():
            recommendations = ["Personal Finance Tips", "Budgeting for Beginners"]
        
        return jsonify({
            'response': ai_response,
            'recommendations': recommendations
        })
        
    except Exception as e:
        # Log the full error traceback
        logger.error(f"Error processing request: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a more detailed error response
        error_details = {
            'error': str(e),
            'type': type(e).__name__,
            'details': traceback.format_exc().split('\n')
        }
        return jsonify(error_details), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)