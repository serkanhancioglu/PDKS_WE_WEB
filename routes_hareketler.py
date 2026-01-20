"""
Hareket Raporları - Orijinal Formüller
Kaynak: Raporlar/01-05 PHP dosyaları
"""
from flask import jsonify, request
from datetime import datetime
from hesap_inc_full import time_to_minute, dakika_to_saat

def register_hareketler_routes(app, query_db, SCHEMA):
    
    @app.route('/api/hareketler', methods=['GET'])
    def get_hareketler():
        """01 - Genel Bazda Hareket"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        result = query_db(f'''
            SELECT 
                TO_CHAR(h.tarih, 'DD.MM.YYYY') as tarih,
                h.personel_id as sicil_no,
                TO_CHAR(h.giris_saat, 'HH24:MI') as giris,
                TO_CHAR(h.cikis_saat, 'HH24:MI') as cikis,
                TO_CHAR(v.basla, 'HH24:MI') as mesai_baslangic,
                TO_CHAR(v.bitis, 'HH24:MI') as mesai_bitis
            FROM {SCHEMA}.hareketler h
            LEFT JOIN {SCHEMA}.personel p ON h.personel_id = p.id
            LEFT JOIN {SCHEMA}.vardiyagruplari vg ON p.hesapgrupkodu = vg.id
            LEFT JOIN {SCHEMA}.vardiyalar v ON vg.id = v.vardiyaid
            WHERE h.tarih BETWEEN %s AND %s
            ORDER BY h.tarih DESC, h.personel_id
        ''', (start, end))
        if not result:
            return jsonify([])
        hareketler = []
        for r in result:
            giris = r.get('giris', '')
            cikis = r.get('cikis', '')
            calisma_dk = 0
            if giris and cikis:
                giris_int = time_to_minute(giris)
                cikis_int = time_to_minute(cikis)
                if giris_int > 0 and cikis_int > 0:
                    calisma_dk = cikis_int - giris_int
            hareketler.append({
                'tarih': r.get('tarih', ''),
                'sicil_no': str(r.get('sicil_no', '')),
                'giris': giris or '-',
                'cikis': cikis or '-',
                'calisma': dakika_to_saat(calisma_dk) if calisma_dk > 0 else '-',
                'mesai_baslangic': r.get('mesai_baslangic') or '-'
            })
        return jsonify(hareketler)

    @app.route('/api/gec-gelenler', methods=['GET'])
    def get_gec_gelenler():
        """05 - Gec Gelenler Raporu - Orijinal formül"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        result = query_db(f'''
            SELECT 
                TO_CHAR(h.tarih, 'DD.MM.YYYY') as tarih,
                h.personel_id as sicil_no,
                TO_CHAR(h.giris_saat, 'HH24:MI') as giris,
                TO_CHAR(v.basla, 'HH24:MI') as mesai_baslangic
            FROM {SCHEMA}.hareketler h
            LEFT JOIN {SCHEMA}.personel p ON h.personel_id = p.id
            LEFT JOIN {SCHEMA}.vardiyagruplari vg ON p.hesapgrupkodu = vg.id
            LEFT JOIN {SCHEMA}.vardiyalar v ON vg.id = v.vardiyaid
            WHERE h.tarih BETWEEN %s AND %s
            AND h.giris_saat > v.basla
            AND v.basla IS NOT NULL
            AND v.basla != '00:00:00'
            ORDER BY h.tarih DESC
        ''', (start, end))
        if not result:
            return jsonify([])
        gec_gelenler = []
        for r in result:
            giris = r.get('giris', '')
            mesai_baslangic = r.get('mesai_baslangic', '')
            if giris and mesai_baslangic:
                giris_int = time_to_minute(giris)
                baslangic_int = time_to_minute(mesai_baslangic)
                if giris_int > baslangic_int:
                    gec_sure = dakika_to_saat(giris_int - baslangic_int)
                    gec_gelenler.append({
                        'tarih': r.get('tarih', ''),
                        'sicil_no': str(r.get('sicil_no', '')),
                        'mesai_baslangic': mesai_baslangic,
                        'giris': giris,
                        'gec_sure': gec_sure
                    })
        return jsonify(gec_gelenler)

    @app.route('/api/erken-cikanlar', methods=['GET'])
    def get_erken_cikanlar():
        """06 - Erken Cikanlar Raporu - Orijinal formül"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        result = query_db(f'''
            SELECT 
                TO_CHAR(h.tarih, 'DD.MM.YYYY') as tarih,
                h.personel_id as sicil_no,
                TO_CHAR(h.cikis_saat, 'HH24:MI') as cikis,
                TO_CHAR(v.bitis, 'HH24:MI') as mesai_bitis
            FROM {SCHEMA}.hareketler h
            LEFT JOIN {SCHEMA}.personel p ON h.personel_id = p.id
            LEFT JOIN {SCHEMA}.vardiyagruplari vg ON p.hesapgrupkodu = vg.id
            LEFT JOIN {SCHEMA}.vardiyalar v ON vg.id = v.vardiyaid
            WHERE h.tarih BETWEEN %s AND %s
            AND h.cikis_saat < v.bitis
            AND v.bitis IS NOT NULL
            AND v.bitis != '00:00:00'
            ORDER BY h.tarih DESC
        ''', (start, end))
        if not result:
            return jsonify([])
        erken_cikanlar = []
        for r in result:
            cikis = r.get('cikis', '')
            mesai_bitis = r.get('mesai_bitis', '')
            if cikis and mesai_bitis:
                cikis_int = time_to_minute(cikis)
                bitis_int = time_to_minute(mesai_bitis)
                if cikis_int < bitis_int:
                    erken_sure = dakika_to_saat(bitis_int - cikis_int)
                    erken_cikanlar.append({
                        'tarih': r.get('tarih', ''),
                        'sicil_no': str(r.get('sicil_no', '')),
                        'cikis': cikis,
                        'mesai_bitis': mesai_bitis,
                        'erken_sure': erken_sure
                    })
        return jsonify(erken_cikanlar)

    @app.route('/api/personel', methods=['GET'])
    def get_personel():
        """Personel listesi"""
        result = query_db(f'''
            SELECT id, kartno, sicilno, adi, soyadi, hesapgrupkodu,
                   TO_CHAR(isegiris, 'DD.MM.YYYY') as ise_giris
            FROM {SCHEMA}.personel
            WHERE isegiris IS NOT NULL AND (isecikis IS NULL)
            ORDER BY adi, soyadi
        ''')
        return jsonify(result or [])

    @app.route('/api/icerdekiler', methods=['GET'])
    def get_icerdekiler():
        """14 - Su an icerideki personeller"""
        today = datetime.now().strftime('%Y-%m-%d')
        result = query_db(f'''
            SELECT h.personel_id as sicil_no, TO_CHAR(h.giris_saat, 'HH24:MI') as giris
            FROM {SCHEMA}.hareketler h
            WHERE h.tarih = %s AND h.giris_saat IS NOT NULL AND h.cikis_saat IS NULL
            ORDER BY h.giris_saat DESC
        ''', (today,))
        return jsonify(result or [])
