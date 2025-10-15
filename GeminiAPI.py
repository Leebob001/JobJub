import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai.errors import APIError 

load_dotenv()

app = Flask(__name__)

# ✅ แก้ไข: ดึงค่าจากตัวแปรชื่อ "key" ในไฟล์ .env
GEMINI_API_KEY_VALUE = os.environ.get("key") 
client = None

if GEMINI_API_KEY_VALUE:
    try:
        # ✅ สร้าง Client ด้วยค่าที่ดึงมา (แม้ชื่อจะต่างกัน)
        client = genai.Client(api_key=GEMINI_API_KEY_VALUE) 
        print("✅ Gemini Client initialized successfully.")
    except Exception as e:
        print(f"❌ ERROR: Global Gemini Client failed to initialize: {e}")
else:
    print("⚠️ WARNING: API key 'key' not found. API calls will fail.")
# ... ส่วนที่เหลือเหมือนเดิม
CORS(app, resources={r"/ask": {"origins": "*"}})

@app.route('/ask', methods=['POST'])
def handle_gemini_request() : # ✅ เปลี่ยนชื่อฟังก์ชันเพื่อป้องกันความสับสน

    # 1. ตรวจสอบ Client ก่อน
    if not client:
        return jsonify({'error': 'Gemini Client not initialized. Check terminal for API Key warning.'}), 500

    # 2. ตรวจสอบการรับ JSON
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Request body must be valid JSON'}), 400

    user_prompt = data.get('userPrompt')
    if not user_prompt:
        return jsonify({'error': 'No userPrompt found in request'}), 400

    try:
        # 3. ✅ ใช้ client ที่สร้างไว้แล้ว
        answer = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt
            )

        response_data = {
            'text': answer.text,
        }
        
        print("Response sent successfully.")
        return jsonify(response_data)

    except APIError as e:
        print(f"API Error: {e.message}")
        return jsonify({'error': f'Gemini API Error: {e.message}'}), 500
    except Exception as e:
        print(f"Internal Error: {str(e)}")
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

    pass

if __name__ == '__main__':
    app.run(debug=True, port=5001)