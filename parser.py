import os
import json
import requests
from supabase import create_client, Client

# ==========================================
# CONFIGURATION
# ==========================================
GROQ_API_KEY = "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"
SUPABASE_URL = "https://ovajjfkuulwnysrqomoq.supabase.co"
SUPABASE_KEY = "sb_secret_mdZzm3H0X3RV_VFVwXZUZw_Ry5wuIOE"
# ==========================================

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def parse_message_with_ai(raw_text: str) -> dict:
    """Sends raw text to Groq's API directly via standard HTTP POST request."""
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_instruction = (
        "You are an expert bookkeeping assistant for Kenyan SMEs. "
        "Your job is to extract sales transaction details from raw, informal text. "
        "You must output ONLY a valid JSON object with the following keys, and absolutely no conversational filler:\n"
        "{\n"
        '  "item_name": "string (The product or service sold)",\n'
        '  "quantity": "integer (Defaults to 1 if not specified)",\n'
        '  "amount_kes": "numeric (The TOTAL transaction value in KES)",\n'
        '  "customer_name": "string or null (Name of buyer if mentioned)"\n'
        "}\n"
        "Ensure quantity is a pure integer and amount_kes is a pure number. "
        "If currency is mentioned in KES or Shillings, extract just the numerical value."
    )
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Parse this message: '{raw_text}'"}
        ],
        "temperature": 0.0
    }

    try:
        # Make a direct HTTP request (bypasses SDK connection issues)
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        # Check if the API key or request had an issue
        if response.status_code != 200:
            print(f"Groq API Error Status {response.status_code}: {response.text}")
            return None
            
        response_data = response.json()
        response_text = response_data["choices"][0]["message"]["content"].strip()
        return json.loads(response_text)
        
    except Exception as e:
        print(f"Error parsing with AI: {e}")
        return None

def save_to_supabase(parsed_data: dict, original_text: str):
    """Inserts the parsed transaction directly into our Supabase sales table."""
    try:
        data_to_insert = {
            "item_name": parsed_data.get("item_name"),
            "quantity": parsed_data.get("quantity", 1),
            "amount_kes": parsed_data.get("amount_kes"),
            "customer_name": parsed_data.get("customer_name"),
            "raw_message": original_text
        }
        
        response = supabase.table("sales").insert(data_to_insert).execute()
        print("🎉 Successfully logged transaction to Supabase!")
        return response
    except Exception as e:
        print(f"Database insertion failed: {e}")
        return None

if __name__ == "__main__":
    test_message = "Sold 5 wheelbarrows at 4500 KES each to Kamau"
    print(f"Original Text: '{test_message}'")
    
    print("Parsing text with Llama-3 on Groq...")
    parsed_json = parse_message_with_ai(test_message)
    
    if parsed_json:
        print(f"Parsed JSON:\n{json.dumps(parsed_json, indent=2)}")
        print("Attempting to save to Supabase...")
        save_to_supabase(parsed_json, test_message)
