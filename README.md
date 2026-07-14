# SemaLedger
AI-powered bookkeeping assistant that structures plain-text WhatsApp messages into a SQL database using Flask, Llama 3.1 (Groq), and Supabase.
# 📔 SemaLedger: AI-Powered WhatsApp Bookkeeping Assistant

SemaLedger is an automated, real-time bookkeeping assistant designed to convert casual, conversational sales transactions sent over WhatsApp into structured cloud database records. By leveraging state-of-the-art Large Language Models (LLMs), it eliminates manual data entry, enabling instant record-keeping directly from a mobile device.

---

## 🏗️ System Architecture & Data Flow

Below is the network flow mapping the lifetime of a transactional message:

```text
[WhatsApp User] ──(Plain Text)──► [Twilio API Gateway]
                                          │
                                   (Secure Webhook Route)
                                          ▼
[Supabase Cloud DB] ◄──(JSON)── [Local Flask Server] ◄──(ngrok Tunnel)
                                    │        ▲
                            (Request)        (Parsed Data)
                                    ▼        │
                              [Groq / Llama 3.1 API]
