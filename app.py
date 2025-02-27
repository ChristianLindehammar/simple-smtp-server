from flask import Flask, render_template, jsonify, request, send_from_directory
import random
import string
import logging
import requests
import os
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask application with explicit template folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

# Domain name used for email addresses
EMAIL_DOMAIN = "tempmail.local"  # Change this to your actual domain when using Cloudflare

# API key for accessing our own API
API_KEY = os.environ.get('API_KEY', 'your-secure-api-key-here')
API_HOST = os.environ.get('API_HOST', 'localhost')
API_ENDPOINT = f"http://{API_HOST}:8025"  # Using environment variable for hostname

def generate_random_email():
    """Generate a random email address"""
    username_length = 10
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
    return f"{username}@{EMAIL_DOMAIN}"

@app.route('/')
def index():
    """Main page that generates a random email"""
    try:
        logger.debug(f"Template directory: {template_dir}")
        logger.debug(f"Available templates: {os.listdir(template_dir) if os.path.exists(template_dir) else 'Directory not found'}")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        logger.error(traceback.format_exc())
        return f"<h1>Error loading page</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>"

@app.route('/debug')
def debug_info():
    """Endpoint to show debug information"""
    info = {
        "flask_path": app.root_path,
        "template_dir": template_dir,
        "template_dir_exists": os.path.exists(template_dir),
        "template_files": os.listdir(template_dir) if os.path.exists(template_dir) else [],
        "working_dir": os.getcwd(),
        "api_endpoint": API_ENDPOINT
    }
    return jsonify(info)

@app.route('/api/generate-email', methods=['GET'])
def generate_email():
    """API endpoint to generate a new random email"""
    email = generate_random_email()
    return jsonify({'email': email})

@app.route('/api/check-emails', methods=['POST'])
def check_emails():
    """API endpoint to check for new emails"""
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({'error': 'Username not provided'}), 400
    
    # Clean up username if full email was provided
    if '@' in username:
        username = username.split('@')[0]
    
    logger.info(f"Checking emails for username: {username}")
    
    # Call the API server to get emails
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(f"{API_ENDPOINT}/api/emails/{username}", headers=headers)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'API returned status {response.status_code}', 'emails': []}), 400
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        return jsonify({'error': str(e), 'emails': []}), 500

if __name__ == '__main__':
    # Make sure template directory exists
    os.makedirs(template_dir, exist_ok=True)
    
    # Run the Flask app with debug enabled
    app.run(host='0.0.0.0', port=8000, debug=True)
