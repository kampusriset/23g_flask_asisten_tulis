import os
import requests
from flask import Blueprint, request, jsonify, session
from app import db
from app.models.chat_history import ChatHistory
from dotenv import load_dotenv

load_dotenv()

gemini_bp = Blueprint('gemini', __name__)


# Ambil API key dari environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}'


@gemini_bp.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }
    try:
        response = requests.post(GEMINI_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        ai_text = result.get('candidates', [{}])[0].get('content', {}).get(
            'parts', [{}])[0].get('text', 'Maaf, tidak ada respons.')

        # Simpan ke database
        chat = ChatHistory(
            user_id=user_id, user_input=user_message, ai_output=ai_text)
        db.session.add(chat)
        db.session.commit()

        return jsonify({'reply': ai_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint untuk mengambil dan menghapus riwayat chat user
@gemini_bp.route('/api/ai-chat-history', methods=['GET', 'DELETE'])
def ai_chat_history():
    user_id = session.get('user_id')
    if not user_id:
        if request.method == 'GET':
            return jsonify({'history': []})
        else:
            return jsonify({'error': 'User not logged in'}), 401

    if request.method == 'GET':
        history = ChatHistory.query.filter_by(user_id=user_id).order_by(
            ChatHistory.created_at.asc()).all()
        result = [
            {
                'user_input': item.user_input,
                'ai_output': item.ai_output,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for item in history
        ]
        return jsonify({'history': result})
    elif request.method == 'DELETE':
        ChatHistory.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({'message': 'Chat history deleted'})
