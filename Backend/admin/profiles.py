from flask import Blueprint, request, jsonify
from model import Database
from Backend.admin.login import token_required

profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route('/profiles', methods=['GET'])
@token_required
def get_profil(current_user):
    try:
        db = Database()
        query = "SELECT * FROM profiles WHERE user_id = %s"
        result = db.execute_query(query, (current_user,), fetch=True)
        
        if result:
            return jsonify({'success': True, 'data': result[0]}), 200
        else:
            return jsonify({'success': True, 'data': {}}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profiles_bp.route('/profiles', methods=['POST', 'PUT'])
@token_required
def update_profil(current_user):
    try:
        data = request.get_json(silent=True) or {}
        db = Database()

        check_query = "SELECT id FROM profiles WHERE user_id = %s"
        existing = db.execute_query(check_query, (current_user,), fetch=True)

        allowed_fields = [
            'nama_lengkap', 'nama_panggilan', 'tempat_lahir',
            'email', 'telepon', 'universitas', 'fakultas', 'prodi',
            'semester', 'alamat', 'foto_url'
        ]

        updates = []
        values = []

        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])

        if not updates:
            return jsonify({'error': 'Tidak ada data valid untuk diupdate'}), 400

        if existing:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            values.append(current_user)
            query = f"UPDATE profiles SET {', '.join(updates)} WHERE user_id = %s"
        else:
            fields_str = ', '.join([f.split(' = ')[0] for f in updates])
            placeholders = ', '.join(['%s'] * len(updates))
            values.insert(0, current_user)
            query = f"INSERT INTO profiles (user_id, {fields_str}) VALUES (%s, {placeholders})"

        db.execute_query(query, tuple(values))

        saved_profile = db.execute_query(
            "SELECT * FROM profiles WHERE user_id = %s LIMIT 1",
            (current_user,),
            fetch=True
        )

        return jsonify({
            'success': True,
            'message': 'Profil berhasil disimpan',
            'data': saved_profile[0] if saved_profile else {}
        }), 200

    except Exception as e:
        print(f"DEBUG ERROR PROFIL: {str(e)}")
        return jsonify({'error': str(e)}), 500