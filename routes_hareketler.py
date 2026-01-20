"""
Hareket Raporları
"""
from flask import jsonify, request
from datetime import datetime
from hesap_fonksiyonlar import time_to_minute, dakika_to_saat


def register_hareketler_routes(app, query_db, SCHEMA):
    
    @app.route('/api/hareketler', methods=['GET'])
    def get_hareketler():
        """Genel hareket raporu"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        
        result = query_db(f'''
            SELECT 
                TO_CHAR(h.tarih, 'DD.MM.YYYY') as tarih,
                h.personelid as sicil_no,
                p.adi || ' ' || p.soyadi as personel_adi,
                TO_CHAR(h.girissaat, 'HH24:MI') as giris,
                TO_CHAR(h.cikissaat, 'HH24:MI') as cikis,
                TO_CHAR(v.basla, 'HH24:MI') as mesai_baslangic,
                TO_CHAR(v.bitis, 'HH24:MI') as mesai_bitis
            FROM {SCHEMA}.hareketler h
            LEFT JOIN {SCHEMA}.personel p ON h.personelid = p.id
            LEFT JOIN {SCHEMA}.vardiyagruplari vg ON p.hesapgrupkodu = vg.id
            LEFT JOIN {SCHEMA}.vardiyalar v ON vg.id = v.vardiyaid
            WHERE h.tarih BETWEEN %s AND %s
            ORDER BY h.tarih DESC, p.adi
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
                'personel_adi': r.get('personel_adi', ''),
                'giris': giris or '-',
                'cikis': cikis or '-',
                'calisma': dakika_to_saat(calisma_dk) if calisma_dk > 0 else '-',
                'mesai_baslangic': r.get('mesai_baslangic') or '-'
            })
        
        return jsonify(hareketler)

    @app.route('/api/gec-gelenler', methods=['GET'])
    def get_gec_gelenler():
        """Geç gelenler raporu"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        
        result = query_db(f'''
            SELECT 
                TO_CHAR(h.tarih, 'DD.MM.YYYY') as tarih,
                h.personelid as sicil_no,
                p.adi || ' ' || p.soyadi as personel_adi,
                TO_CHAR(h.girissaat, 'HH24:MI') as giris,
                TO_CHAR(v.basla, 'HH24:MI') as mesai_baslangic
            FROM {SCHEMA}.hareketler h
            LEFT JOIN {SCHEMA}.personel p ON h.personelid = p.id
            LEFT JOIN {SCHEMA}.vardiyagruplari vg ON p.hesapgrupkodu = vg.id
            LEFT JOIN {SCHEMA}.vardiyalar v ON vg.id = v.vardiyaid
            WHERE h.tarih BETWEEN %s AND %s
            AND h.girissaat > v.basla
            AND v.basla IS NOT NULL
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
                        'personel_adi': r.get('personel_adi', ''),
                        'mesai_baslangic': mesai_baslangic,
                        'giris': giris,
                        'gec_sure': gec_sure
                    })
        
        return jsonify(gec_gelenler)

    @app.route('/api/erken-cikanlar', methods=['GET'])
    def get_erken_cikanlar():
        """Erken çıkanlar raporu"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        
        result = query_db(f'''
            SELECT 
                TO_CHAR(h.tarih, 'DD.MM.YYYY') as tarih,
                h.personelid as sicil_no,
                p.adi || ' ' || p.soyadi as personel_adi,
                TO_CHAR(h.cikissaat, 'HH24:MI') as cikis,
                TO_CHAR(v.bitis, 'HH24:MI') as mesai_bitis
            FROM {SCHEMA}.hareketler h
            LEFT JOIN {SCHEMA}.personel p ON h.personelid = p.id
            LEFT JOIN {SCHEMA}.vardiyagruplari vg ON p.hesapgrupkodu = vg.id
            LEFT JOIN {SCHEMA}.vardiyalar v ON vg.id = v.vardiyaid
            WHERE h.tarih BETWEEN %s AND %s
            AND h.cikissaat < v.bitis
            AND v.bitis IS NOT NULL
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
                        'personel_adi': r.get('personel_adi', ''),
                        'cikis': cikis,
                        'mesai_bitis': mesai_bitis,
                        'erken_sure': erken_sure
                    })
        
        return jsonify(erken_cikanlar)

    @app.route('/api/devamsizlik', methods=['GET'])
    def get_devamsizlik():
        """Devamsızlık raporu"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        
        result = query_db(f'''
            SELECT p.id, p.sicilno, p.adi || ' ' || p.soyadi as personel_adi
            FROM {SCHEMA}.personel p
            WHERE p.aktif = 1
            AND p.id NOT IN (
                SELECT DISTINCT personelid FROM {SCHEMA}.hareketler 
                WHERE tarih BETWEEN %s AND %s
            )
            ORDER BY p.adi
        ''', (start, end))
        
        return jsonify(result or [])

    @app.route('/api/icerdekiler', methods=['GET'])
    def get_icerdekiler():
        """Şu an içerideki personeller"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        result = query_db(f'''
            SELECT 
                h.personelid as sicil_no,
                p.adi || ' ' || p.soyadi as personel_adi,
                TO_CHAR(h.girissaat, 'HH24:MI') as giris
            FROM {SCHEMA}.hareketler h
            LEFT JOIN {SCHEMA}.personel p ON h.personelid = p.id
            WHERE h.tarih = %s 
            AND h.girissaat IS NOT NULL 
            AND h.cikissaat IS NULL
            ORDER BY h.girissaat DESC
        ''', (today,))
        
        return jsonify(result or [])
