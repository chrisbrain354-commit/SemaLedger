from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from parser import parse_message_with_ai, save_to_supabase

app = Flask(__name__)

# This endpoint will "listen" for messages sent from Twilio (WhatsApp)
@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    # 1. Grab the incoming WhatsApp message text
    incoming_msg = request.values.get("Body", "").strip()
    sender_number = request.values.get("From", "")
    
    print(f"\n--- New Message Received from {sender_number} ---")
    print(f"Message: '{incoming_msg}'")
    
    # Create Twilio XML response
    response = MessagingResponse()
    
    if not incoming_msg:
        response.message("Sorry, I didn't receive any text.")
        return str(response)
        
    # 2. Process with our existing AI brain!
    print("Processing with AI...")
    parsed_json = parse_message_with_ai(incoming_msg)
    
    if parsed_json and parsed_json.get("item_name"):
        # 3. Save to Supabase
        save_to_supabase(parsed_json, incoming_msg)
        
        # Send a success confirmation back to the WhatsApp user
        item = parsed_json.get("item_name")
        qty = parsed_json.get("quantity", 1)
        amt = parsed_json.get("amount_kes")
        
        reply_text = f"✅ Sale Logged!\n📦 Item: {item}\n🔢 Qty: {qty}\n💰 Total KES: {amt:,}"
        response.message(reply_text)
    else:
        response.message("❌ Couldn't parse that sale. Please try format: '3 bags of cement 2100 KES'")
        
    return str(response)

if __name__ == "__main__":
    # Run server on port 5000
    app.run(port=5000)
