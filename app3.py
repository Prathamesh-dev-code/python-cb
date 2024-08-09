from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
import requests
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

ORACLE_API_URL = 'http://192.168.100.177:8077/websiteDataApi/saveChatBotData'

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# User interaction states
INITIAL = 'initial'
GREETING = 'greeting'
LEARN_ERP = 'learn_erp'
SUPPORT = 'support'
DEMO = 'demo'
CONTACT = 'contact'
GENERAL = 'general'
END_CONVERSATION = 'end_conversation'
COLLECT_NAME = 'collect_name'
COLLECT_CONTACT = 'collect_contact'
COLLECT_CITY = 'collect_city'
COLLECT_EMAIL = 'collect_email'
COLLECT_COMPANY = 'collect_company'
COLLECT_MESSAGE = 'collect_message'
SERVICE_QUERY = 'service_query'

def store_user_info():
    if all(k in session for k in ('name', 'mobile', 'email', 'company', 'message', 'city')):
        user_data = {
            'Person_name': session['name'],
            'Mobile': session['mobile'],
            'Email': session['email'],
            'Company_name': session['company'],
            'Message': session['message'],
            'City': session['city']
        }
        
        csv_data = ','.join(user_data.values())

        # Logging user data and CSV format
        logging.debug(f"Storing user info: {user_data}")
        logging.debug(f"CSV data to send: {csv_data}")

        try:
            response = requests.post(ORACLE_API_URL, data={'enquiryForm': csv_data})
            response.raise_for_status()
            logging.debug(f"Response from Oracle API: {response.status_code} - {response.text}")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logging.error(f"Error saving data to Oracle API: {e}")
            return False
    else:
        logging.error("Incomplete data in session, cannot store user info.")
        return False

def user_exists(name):
    # Add logic to check if the user exists in your database
    return False

def get_main_menu_options():
    return [
        {"label": "More about LightHouse ERP", "value": LEARN_ERP},
        {"label": "Get Support", "value": SUPPORT},
        {"label": "Request a demo", "value": DEMO},
        {"label": "Contact Us", "value": CONTACT}
    ]

def get_response(state, user_input):
    user_input_lower = user_input.lower().strip()

    if state == INITIAL:
        session['state'] = COLLECT_NAME
        return {"message": "Hello and welcome to Lighthouse Info Systems Pvt. Ltd.! 😊 <br> May I know your <span>name</span>, please?"}

    elif state == COLLECT_NAME:
        session['name'] = user_input
        if user_exists(user_input):
            session['state'] = GREETING
            return {"message": f"Welcome back, {user_input}! How can I assist you today?"}
        else:
            session['state'] = COLLECT_CONTACT
            return {"message": f"Nice to meet you, {user_input}😊! Could you provide <span>your contact number</span> so we can reach out to you if needed?"}

    elif state == COLLECT_CONTACT:
        session['mobile'] = user_input
        session['state'] = COLLECT_CITY
        return {"message": "Could you tell me which <span> city </span> you're located in?"}

    elif state == COLLECT_CITY:
        session['city'] = user_input
        session['state'] = COLLECT_EMAIL
        return {"message": "Thank you! What's the best <span>email</span> address to send information to?"}

    elif state == COLLECT_EMAIL:
        session['email'] = user_input
        session['state'] = COLLECT_COMPANY
        return {"message": "Could you please provide your <span>company name?</span>"}

    elif state == COLLECT_COMPANY:
        session['company'] = user_input
        session['state'] = COLLECT_MESSAGE
        return {"message": "Could you please share a bit about your <span> requirements </span> or what you're looking for?"}

    elif state == COLLECT_MESSAGE:
        session['message'] = user_input
        if store_user_info():
            session['state'] = GREETING
            return {
                "message": "Thank you for providing your details. We will review your information and get back to you shortly!",
                "options": get_main_menu_options()
            }
        else:
            return {
                "message": "There was an error saving your information. Please try again. Please choose one of the options.",
                "options": []
            }

    elif state == GREETING:
        if user_input in [option['value'] for option in get_main_menu_options()]:
            session['state'] = user_input
            return get_response(session['state'], user_input)
        else:
            return {
                "message": "Please choose one of the options.",
                "options": get_main_menu_options()
            }

    elif state == LEARN_ERP:
        session['state'] = GREETING
        return {
            "message": "Discover a wealth of information! Click on this <a href='https://www.lighthouseindia.com/brochures.html' target='_blank'>https://www.lighthouseindia.com/brochures.html</a> to access a variety of PDFs related to ERP. 📚",
            "options": get_main_menu_options()
        }

    elif state == SUPPORT:
        session['state'] = GREETING
        return {
            "message": "For more information, visit this link <a href='https://lcare.lighthouseindia.com' target='_blank'>https://lcare.lighthouseindia.com</a> 🌐.",
            "options": get_main_menu_options()
        }

    elif state == DEMO:
        session['state'] = GREETING
        return {
            "message": "Request a demo by filling out the form <a href='https://www.lighthouseindia.com/request-quote.html' target='_blank'>https://www.lighthouseindia.com/request-quote.html</a> 🚀.",
            "options": get_main_menu_options()
        }

    elif state == CONTACT:
        return {"message": "Please fill out the form below.", "options": []}

    elif state == END_CONVERSATION:
        session['state'] = GREETING
        return {
            "message": "Thank you for connecting with us!",
            "options": get_main_menu_options()
        }

def fixed_menu_options():
    return [
        {"label": "More about LightHouse ERP", "value": LEARN_ERP},
        {"label": "Get Support", "value": SUPPORT},
        {"label": "Request a demo", "value": DEMO},
        {"label": "Contact Us", "value": CONTACT}
    ]

def get_fixed_response(state):
    if state == LEARN_ERP:
        return {
            "message": "Discover a wealth of information! Click on this <a href='https://www.lighthouseindia.com/brochures.html' target='_blank'>https://www.lighthouseindia.com/brochures.html</a> to access a variety of PDFs related to ERP. 📚"
        }

    elif state == SUPPORT:
        return {
            "message": "For more information, visit this link <a href='https://lcare.lighthouseindia.com' target='_blank'>https://lcare.lighthouseindia.com</a> 🌐."
        }

    elif state == DEMO:
        return {
            "message": "Request a demo by filling out the form <a href='https://www.lighthouseindia.com/request-quote.html' target='_blank'>https://www.lighthouseindia.com/request-quote.html</a> 🚀."
        }

    elif state == CONTACT:
        return {"message": "Please fill out the form below."}

@app.route('/')
def index():
    session.clear()
    session['state'] = INITIAL
    return render_template('index.html')

@app.route('/reset-session', methods=['POST'])
def reset_session():
    session.clear()
    return '', 204

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    state = session.get('state', INITIAL)
    response = get_response(state, user_input)
    return jsonify(response)

@app.route('/fixed_options', methods=['GET'])
def fixed_options():
    options = fixed_menu_options()
    return jsonify({'options': options})

@app.route('/fixed_response', methods=['POST'])
def fixed_response():
    user_input = request.json.get('message')
    response = get_fixed_response(user_input)
    return jsonify(response)

@app.route('/submit-contact-form', methods=['POST'])
def submit_contact_form():
    form_data = request.json
    logging.debug(f"Received form data: {form_data}")  # Log received form data

    session['name'] = form_data.get('name')
    session['mobile'] = form_data.get('mobile')
    session['email'] = form_data.get('email')
    session['company'] = form_data.get('company')
    session['message'] = form_data.get('message')
    session['city'] = form_data.get('city')

    if store_user_info():
        # Clear session and reset state
        #session.clear()
        session['state'] = INITIAL
        return jsonify({
            "success": True,
            "message": "Thank you for connecting with us! We will reach out to you soon. ✅<br><strong>Address:</strong><br>14/4, I.T. Park Parsodi,<br>South Ambazari Road,<br>Nagpur, Maharashtra, India<br>Pincode: 440022<br><strong>General Queries and Support:</strong><br>+91 8600004931 / +91 8600004932<br><strong>Product Enquiry and Sales:</strong><br>+91 86006 66106<br><strong>Career / Job Enquiry:</strong><br>+91 86006 66103<br><strong>Email:</strong><br><a href='mailto:mktg@lighthouseindia.com'>mktg@lighthouseindia.com</a>"
        })
    else:
        return jsonify({
            "success": False,
            "message": "There was an error saving your information. Please try again."
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)