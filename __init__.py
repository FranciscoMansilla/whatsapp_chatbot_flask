from flask import Flask, jsonify, request
import re
import os
from dotenv import load_dotenv

# Si estás utilizando python-dotenv, carga las variables desde el archivo .env
load_dotenv()

app = Flask(__name__)

def send_whatsapp_message(phone_number, message):
    from heyoo import WhatsApp

    # Case to numbers from argentina
    if phone_number.startswith("549"):
        phone_number = phone_number.replace("549","54")

    # Access token of Meta
    token=os.getenv('META_TOKEN')
    # Id of sender phone number
    phone_number_id = os.getenv('PHONE_NUMBER_ID')
    # Init of whatsapp messages
    w_messages = WhatsApp(token, phone_number_id)
    # Send the response
    w_messages.send_message(message, phone_number)

# Test route
@app.route("/hello_world/", methods=["GET"])
def hello_world():
    return {
        "hello": "world"
    }, 200

# Route of whatsapp bot webhook
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    # If there are data received to get
    if request.method == "GET":
        # If the token is equal to that received
        # Returns the value of the challenge received from meta
        verify_token = os.getenv('VERIFY_TOKEN')
        if request.args.get('hub.verify_token') == verify_token:
            return request.args.get('hub.challenge')
        else:
            # Else returns a error message
            return "Auth error."

    # Case post
    # We received all data like json
    # We extract phone number, whatsapp id and message timestamp from the array

    data=request.get_json()
    phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    idWA = data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    timestamp = data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']

    # If there is message 
    if message is not None:
        from rivescript import RiveScript
        # Init rivescript and load the conversation
        bot = RiveScript()
        bot.load_file('restaurant.rive')
        bot.sort_replies()

        # Get the response
        response = bot.reply("localuser", message)
        response = response.replace("\\n", "\\\n")
        response = response.replace("\\","")
        send_whatsapp_message(phone_number, response)

        # Returns the status in json
        return jsonify({"status": "success"}, 200)

# Init flask
if __name__ == "__main__":
    app.run(debug=True)