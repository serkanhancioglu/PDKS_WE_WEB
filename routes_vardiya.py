"""
Vardiya Yönetimi
"""
from flask import jsonify, request
from datetime import datetime

def register_vardiya_routes(app, query_db, SCHEMA):
    
    def get_db_connection():
        import psycopg2
        import os
        return psycopg2.connect(
            host=os.getenv('PG_HOST', '127.0.0.1'),
            port=int(os.getenv('PG_PORT', '5432')),
            user=os.getenv('PG_USER', 'apibscusr_selamnaber'),
            password=os.getenv('PG_PASSWORD', 'dxCQK{xY7W9j'),
            database=os.getenv('PG_DATABASE', 'apibscusr_test123'),
        )

    @app.route('/api/vardiyalar', methods=['GET'])
    def get_vardiyalar():
        """Vardiya listesi"""
        result = query_db(f'''
            SELECT v.id, v.vardiyaid, 
                   TO_CHAR(v.basla, 'HH24:MI') as basla, 
                   TO_CHAR(v.bitis, 'HH24:MI') as bitis,
                   vg.aciklama as grup_adi
            FROM {SCHEMA}.vardiyalar v
            LEFT JOIN {SCHEMA}.vardiyagruplari vg ON v.vardiyaid = vg.id
            ORDER BY v.basla
        ''')
        return jsonify(result or [])

    @app.route('/api/vardiya/ekle', methods=['POST'])
    def vardiya_ekle():
        """Yeni vardiya ekle"""
        data = request.get_json()
        basla = data.get('basla')
        bitis = data.get('bitis')
        vardiyaid = data.get('vardiyaid', 1)
        if not basla or not bitis:
            return jsonify({'error': 'basla ve bitis gerekli'}), 400
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'db hatasi'}), 500
        try:
            cursor = conn.cursor()
            cursor.execute(f'INSERT INTO {SCHEMA}.vardiyalar (vardiyaid, basla, bitis, gunlukhesapid) VALUES (%s, %s, %s, 1) RETURNING id', (vardiyaid, basla, bitis))
            new_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'id': new_id})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/vardiya/sil/<int:vardiya_id>', methods=['DELETE'])
    def vardiya_sil(vardiya_id):
        """Vardiya sil"""
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'db hatasi'}), 500
        try:
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {SCHEMA}.vardiyalar WHERE id = %s', (vardiya_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/vardiya/guncelle/<int:vardiya_id>', methods=['PUT'])
    def vardiya_guncelle(vardiya_id):
        """Vardiya guncelle"""
        data = request.get_json()
        basla = data.get('basla')
        bitis = data.get('bitis')
        if not basla or not bitis:
            return jsonify({'error': 'basla ve bitis gerekli'}), 400
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'db hatasi'}), 500
        try:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE {SCHEMA}.vardiyalar SET basla = %s, bitis = %s WHERE id = %s', (basla, bitis, vardiya_id))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
