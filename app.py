"""
MikroPer API - Ana Uygulama
Modüler yapı - 150 satır
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Veritabanı ayarları
PG_CONFIG = {
    'host': os.getenv('PG_HOST', '127.0.0.1'),
    'port': int(os.getenv('PG_PORT', '5432')),
    'user': os.getenv('PG_USER', 'apibscusr_selamnaber'),
    'password': os.getenv('PG_PASSWORD', 'dxCQK{xY7W9j'),
    'database': os.getenv('PG_DATABASE', 'apibscusr_test123'),
}

SCHEMA = 'mikroper'

def get_db_connection():
    """Veritabanı bağlantısı"""
    try:
        return psycopg2.connect(**PG_CONFIG)
    except Exception as e:
        print(f'DB hata: {e}')
        return None

def query_db(sql, params=None):
    """SQL sorgusu çalıştır"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f'Query hata: {e}')
        return None

# Route modüllerini import et
from routes_hareketler import register_hareketler_routes
from routes_mesai import register_mesai_routes
from routes_vardiya import register_vardiya_routes
from routes_raporlar import register_rapor_routes

# Route'ları kaydet
register_hareketler_routes(app, query_db, SCHEMA)
register_mesai_routes(app, query_db, SCHEMA)
register_vardiya_routes(app, query_db, SCHEMA)
register_rapor_routes(app, query_db, SCHEMA)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """İstatistikler"""
    stats = {'total_personel': 129, 'today_present': 0, 'late': 0, 'absent': 0}
    today = datetime.now().strftime('%Y-%m-%d')
    result = query_db(f'SELECT COUNT(DISTINCT personel_id) as cnt FROM {SCHEMA}.hareketler WHERE tarih = %s', (today,))
    if result:
        stats['today_present'] = result[0].get('cnt', 0)
    stats['absent'] = max(0, stats['total_personel'] - stats['today_present'])
    return jsonify(stats)

@app.route('/api/test', methods=['GET'])
def test_connection():
    """Bağlantı testi"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM {SCHEMA}.hareketler')
            hareket = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'connected',
                'db': 'PostgreSQL',
                'schema': SCHEMA,
                'hareket_count': hareket,
                'mesaj': 'ORIJINAL FORMUL - Hesap.inc mantigi'
            })
        except Exception as e:
            return jsonify({'status': 'error', 'error': str(e)})
    return jsonify({'status': 'disconnected'})

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
