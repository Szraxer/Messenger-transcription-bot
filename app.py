import os
import io
import re 
import json
import requests
from flask import Flask, request, jsonify
from pydub import AudioSegment
from dotenv import load_dotenv

app = Flask(__name__)

# loading variables (of tokens) from .env file
load_dotenv()

# getting tokens from .env file
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
WIT_ACCESS_TOKEN = os.getenv("WIT_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

#function responsible for sending messages to user
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    #creating message following facebook schema
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    #http post request to send message 
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200: #200 means successful sent message anything other means error
        print(f"Error: {response.text}")

def transcribe_audio_via_wit(audio_url):
    print(f"Downloading audio from FB")
    try:
        audio_res = requests.get(audio_url)
        print("Converting audio to WAV") 
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_res.content))
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")#conv to WAV because its best working for WIT ai
        wav_data = wav_io.getvalue()
        
        headers = {
            "Authorization": f"Bearer {WIT_ACCESS_TOKEN}",
            "Content-Type": "audio/wav" 
        }
        
        print("Sending to Wit.ai")
        response = requests.post("https://api.wit.ai/speech", headers=headers, data=wav_data)
        
        #parsing data
        full_response = response.text

        #looking for actual text from raw json files which is between "text":"[what we looking for]"
        results = re.findall(r'"text":\s*"(.*?)"', full_response)
        
        if results:
            # wit update next array with every word for example ar[0] = "hi" | ar[3] = "hi how are you" so we take last value
            final_result = results[-1]
            print(f"Extracted text: {final_result}")
            return final_result
        
        print(f"Debug (empty message): {full_response[:200]}")
        return "Speech recognition failed."

    except Exception as e:
        print(f"!!! Error: {e}")
        return "Error during audio conversion"

#facebook verification of webhook
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully")
        return challenge, 200
    else:
        print("Error during verification of webhook")
        return "verification error", 403

#main function responsible for receiving messages
@app.route('/webhook', methods=['POST'])
def handle_messages():
    data = request.json

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]

                # handling voice messages
                if "message" in messaging_event and "attachments" in messaging_event["message"]:
                    for attachment in messaging_event["message"]["attachments"]:
                        if attachment["type"] == "audio":
                            audio_url = attachment["payload"]["url"]
                            send_message(sender_id, "Voice message received. Loading in progress...")
                            
                            # transcription
                            transcript = transcribe_audio_via_wit(audio_url)
                            
                            # text response
                            send_message(sender_id, f"Text from voice message:\n\n{transcript}")

                # handling text messages
                elif "message" in messaging_event and "text" in messaging_event["message"]:
                    user_text = messaging_event["message"]["text"]
                    print(f"Text received: {user_text}")
                    send_message(sender_id, "Send me a voice message and I will transcribe it for you")

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    # Launch on port 5000
    app.run(port=5000, debug=True)