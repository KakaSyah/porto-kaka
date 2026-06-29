from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from model import Database
import jwt
import datetime
import logging
from functools import wraps
from config import Config

# Setup logger sederhana untuk debugging login
logger = logging.getLogger(__name__)

# PERBAIKAN 1: Tidak ada url_prefix di sini karena sudah diatur global di app.py
login_bp = Blueprint('login', __name__) 

def _get_token_from_request(include_session=True):
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ', 1)[1]

    return session.get('token') if include_session else None


def get_current_user_id(optional=False):
    token = _get_token_from_request(include_session=not optional)

    if not token:
        return None if optional else (jsonify({'error': 'Token tidak ditemukan'}), 401)

    try:
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return data['user_id']
    except jwt.ExpiredSignatureError:
        return None if optional else (jsonify({'error': 'Token telah kadaluarsa'}), 401)
    except jwt.InvalidTokenError:
        return None if optional else (jsonify({'error': 'Token tidak valid'}), 401)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = get_current_user_id()
        if isinstance(current_user, tuple):
            return current_user

        return f(current_user, *args, **kwargs)
    return decorated


# Registration endpoint removed: account creation is disabled. Only admin password change is supported.


@login_bp.route('/login', methods=['POST'])
def login():
    """Endpoint untuk login admin"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body harus JSON'}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username dan password wajib diisi'}), 400
        
        db = Database()
        query = "SELECT id, username, password_hash, role FROM users WHERE username = %s"
        user = db.execute_query(query, (username,), fetch=True)
        
        if not user:
            # Gunakan pesan generik untuk keamanan (mencegah user enumeration)
            return jsonify({'error': 'Username atau password salah'}), 401
        
        user = user[0]
        
        # Verifikasi password. Untuk tugas lokal, password teks biasa tetap didukung.
        is_valid = False
        try:
            is_valid = check_password_hash(user['password_hash'], password)
        except Exception as e:
            logger.warning(f"[LOGIN DEBUG] Werkzeug check failed: {str(e)}. Trying plain comparison.")

        if not is_valid:
            is_valid = (user['password_hash'] == password)
            
        if not is_valid:
            logger.warning(f"[LOGIN DEBUG] Password mismatch for user: {username}")
            return jsonify({'error': 'Username atau password salah'}), 401
        
        # Generate JWT Token
        token_payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(token_payload, Config.SECRET_KEY, algorithm='HS256')
        
        # Set session flags untuk keamanan cookie
        session.permanent = True
        session['token'] = token
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        return jsonify({
            'message': 'Login berhasil',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"[LOGIN ERROR] {str(e)}")
        return jsonify({'error': 'Terjadi kesalahan pada server'}), 500
@login_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint untuk logout"""
    # Hapus semua data session di server-side
    session.clear()
    
    response = jsonify({'message': 'Logout berhasil'})
    # Hapus cookie session browser
    response.delete_cookie('session') 
    return response, 200

@login_bp.route('/auth/check', methods=['GET'])
@token_required
def check_auth(current_user):
    """Cek status autentikasi"""
    return jsonify({
        'authenticated': True,
        'user': {
            'id': current_user,
            'username': session.get('username'),
            'role': session.get('role')
        }
    }), 200
