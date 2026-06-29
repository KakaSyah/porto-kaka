from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from Backend.admin.login import token_required
from model import Database

akun_bp = Blueprint('akun', __name__)


@akun_bp.route('/akun/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    try:
        data = request.get_json() or {}
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')

        if not old_password or not new_password:
            return jsonify({'error': 'Password lama dan baru wajib diisi'}), 400
        if len(new_password) < 6:
            return jsonify({'error': 'Password baru minimal 6 karakter'}), 400

        db = Database()
        result = db.execute_query(
            "SELECT password_hash FROM users WHERE id = %s",
            (current_user,),
            fetch=True
        )

        if not result:
            return jsonify({'error': 'Akun tidak ditemukan'}), 404

        stored_hash = result[0]['password_hash']
        if not check_password_hash(stored_hash, old_password) and stored_hash != old_password:
            return jsonify({'error': 'Password lama salah'}), 401

        new_hash = generate_password_hash(new_password)
        db.execute_query("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, current_user))
        return jsonify({'success': True, 'message': 'Password berhasil diganti'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
