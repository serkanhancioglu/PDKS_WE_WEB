"""
Mesai Raporları - Orijinal Formüller
Kaynak: Raporlar/04-Fazla Mesai.php, Hesap.inc
"""
from flask import jsonify, request
from datetime import datetime
from hesap_inc_full import time_to_minute, dakika_to_saat, saat_hesapla

def register_mesai_routes(app, query_db, SCHEMA):
    
    @app.route('/api/fazla-mesai', methods=['GET'])
    def get_fazla_mesai():
        """04 - Fazla Mesai Raporu - ORİJİNAL FORMÜL
        
        Orijinal mantık (Hesap.inc):
        1. gunluk_hesap_bordrolar tablosundan bordro saatlerini al
        2. bordroalanlari.bordrotipi = 5 ise FAZLA MESAİ
        3. saat_hesapla() ile kesişim hesapla
        """
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        
        # Bordro tanımlarını al (bordrotipi=5 -> fazla mesai)
        bordro_tanimlari = query_db(f'''
            SELECT ghb.gunlukhesapid, 
                   TO_CHAR(ghb.basla, 'HH24:MI') as bordro_basla,
                   TO_CHAR(ghb.bitis, 'HH24:MI') as bordro_bitis,
                   EXTRACT(EPOCH FROM ghb.min)/60 as min_dk,
                   EXTRACT(EPOCH FROM ghb.ekle)/60 as ekle_dk,
                   ba.bordrotipi
            FROM {SCHEMA}.gunluk_hesap_bordrolar ghb
            JOIN {SCHEMA}.bordroalanlari ba ON ghb.bordroid = ba.id
            WHERE ba.bordrotipi = 5
        ''')
        
        if not bordro_tanimlari:
            return jsonify([])
        
        # Bordroları gunlukhesapid'ye göre grupla
        bordro_map = {}
        for b in bordro_tanimlari:
            ghid = b.get('gunlukhesapid')
            if ghid not in bordro_map:
                bordro_map[ghid] = []
            bordro_map[ghid].append(b)
        
        # Hareketleri al
        result = query_db(f'''
            SELECT 
                TO_CHAR(h.tarih, 'DD.MM.YYYY') as tarih,
                h.personel_id as sicil_no,
                TO_CHAR(h.giris_saat, 'HH24:MI') as giris,
                TO_CHAR(h.cikis_saat, 'HH24:MI') as cikis,
                v.gunlukhesapid
            FROM {SCHEMA}.hareketler h
            LEFT JOIN {SCHEMA}.personel p ON h.personel_id = p.id
            LEFT JOIN {SCHEMA}.vardiyagruplari vg ON p.hesapgrupkodu = vg.id
            LEFT JOIN {SCHEMA}.vardiyalar v ON vg.id = v.vardiyaid
            WHERE h.tarih BETWEEN %s AND %s
            AND h.giris_saat IS NOT NULL
            AND h.cikis_saat IS NOT NULL
            ORDER BY h.tarih DESC
        ''', (start, end))
        
        if not result:
            return jsonify([])
        
        fazla_mesailer = []
        for r in result:
            giris = r.get('giris', '')
            cikis = r.get('cikis', '')
            gunlukhesapid = r.get('gunlukhesapid')
            
            if not giris or not cikis:
                continue
            
            giris_int = time_to_minute(giris)
            cikis_int = time_to_minute(cikis)
            
            if giris_int < 0 or cikis_int < 0:
                continue
            
            # Bu vardiya için fazla mesai bordroları
            bordrolar = bordro_map.get(gunlukhesapid, [])
            
            toplam_fazla_mesai = 0
            for bordro in bordrolar:
                bordro_basla = time_to_minute(bordro.get('bordro_basla', '00:00'))
                bordro_bitis = time_to_minute(bordro.get('bordro_bitis', '00:00'))
                min_dk = int(bordro.get('min_dk', 0) or 0)
                ekle_dk = int(bordro.get('ekle_dk', 0) or 0)
                
                # Gece vardiyası düzeltmesi
                if bordro_basla > bordro_bitis:
                    bordro_bitis += 1440  # +24 saat
                
                # saat_hesapla - orijinal formül (Hesap.inc)
                kesisim = saat_hesapla(giris_int, cikis_int, bordro_basla, bordro_bitis)
                
                # Minimum süre kontrolü
                if kesisim > min_dk:
                    kesisim += ekle_dk
                    toplam_fazla_mesai += kesisim
            
            if toplam_fazla_mesai > 0:
                fazla_mesailer.append({
                    'tarih': r.get('tarih', ''),
                    'sicil_no': str(r.get('sicil_no', '')),
                    'giris': giris,
                    'cikis': cikis,
                    'fazla_mesai': dakika_to_saat(toplam_fazla_mesai)
                })
        
        return jsonify(fazla_mesailer)

    @app.route('/api/gec-erken', methods=['GET'])
    def get_gec_erken():
        """07 - Gec Gelme Erken Cikma Raporu"""
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
            ORDER BY h.tarih DESC
        ''', (start, end))
        if not result:
            return jsonify([])
        rapor = []
        for r in result:
            giris = r.get('giris', '')
            cikis = r.get('cikis', '')
            mesai_baslangic = r.get('mesai_baslangic', '')
            mesai_bitis = r.get('mesai_bitis', '')
            gec_gelme = ''
            erken_cikma = ''
            if giris and mesai_baslangic:
                giris_int = time_to_minute(giris)
                baslangic_int = time_to_minute(mesai_baslangic)
                if baslangic_int > 0 and giris_int > baslangic_int:
                    gec_gelme = dakika_to_saat(giris_int - baslangic_int)
            if cikis and mesai_bitis:
                cikis_int = time_to_minute(cikis)
                bitis_int = time_to_minute(mesai_bitis)
                if bitis_int > 0 and cikis_int < bitis_int:
                    erken_cikma = dakika_to_saat(bitis_int - cikis_int)
            if gec_gelme or erken_cikma:
                rapor.append({
                    'tarih': r.get('tarih', ''),
                    'sicil_no': str(r.get('sicil_no', '')),
                    'giris': giris,
                    'cikis': cikis,
                    'gec_gelme': gec_gelme,
                    'erken_cikma': erken_cikma
                })
        return jsonify(rapor)
