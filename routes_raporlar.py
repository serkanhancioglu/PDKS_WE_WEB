"""
MikroPer Ek Raporlar
PHP kaynaklarından birebir çeviri
"""
from flask import request, jsonify
from datetime import datetime, timedelta


def register_rapor_routes(app, query_db, SCHEMA):
    
    # =========================================================================
    # 03 - DEVAMSIZLIK RAPORU
    # =========================================================================
    @app.route('/api/devamsizlik', methods=['GET'])
    def get_devamsizlik_raporu():
        """03 - Devamsızlık Raporu - Hareket kaydı olmayan personeller"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        izinlileri_goster = request.args.get('izinlileri_goster', '0') == '1'
        
        devamsizlar = []
        
        # Tüm aktif personelleri al
        personeller = query_db(f'''
            SELECT id, kartno, sicilno, adi, soyadi, hesapgrupkodu
            FROM {SCHEMA}.personel
            WHERE isegiris IS NOT NULL AND (isecikis IS NULL OR isecikis > %s)
            ORDER BY adi, soyadi
        ''', (end,))
        
        if not personeller:
            return jsonify([])
        
        # Tarih aralığındaki günler
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        
        current = start_date
        while current <= end_date:
            tarih = current.strftime('%Y-%m-%d')
            tarih_str = current.strftime('%d.%m.%Y')
            
            for per in personeller:
                # Bu tarihte hareket var mı?
                hareket = query_db(f'''
                    SELECT id FROM {SCHEMA}.hareketler
                    WHERE personelid = %s AND tarih = %s
                    LIMIT 1
                ''', (per['id'], tarih))
                
                if not hareket:
                    # İzin kontrolü
                    izin = query_db(f'''
                        SELECT t.tatiladi, p.aciklama
                        FROM {SCHEMA}.personelizin p
                        LEFT JOIN {SCHEMA}.tatiller t ON t.id = p.tatilid
                        WHERE p.personelid = %s AND p.tarih = %s
                    ''', (per['id'], tarih))
                    
                    durum = "DEVAMSIZ"
                    if izin and len(izin) > 0:
                        durum = izin[0].get('tatiladi', 'İZİNLİ')
                        if not izinlileri_goster:
                            continue
                    
                    devamsizlar.append({
                        'tarih': tarih_str,
                        'kartno': per.get('kartno', ''),
                        'sicilno': per.get('sicilno', ''),
                        'adi': per.get('adi', ''),
                        'soyadi': per.get('soyadi', ''),
                        'durum': durum
                    })
            
            current += timedelta(days=1)
        
        return jsonify(devamsizlar)
    
    # =========================================================================
    # 11/12/13 - KART BASMAYANLAR RAPORU
    # =========================================================================
    @app.route('/api/kart-basmayanlar', methods=['GET'])
    def get_kart_basmayanlar():
        """13 - Giriş ya da Çıkışta Kart Basmayanlar"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        tip = request.args.get('tip', 'tum')  # giris, cikis, tum
        
        if tip == 'giris':
            condition = "AND h.girissaat IS NULL AND h.cikissaat IS NOT NULL"
        elif tip == 'cikis':
            condition = "AND h.girissaat IS NOT NULL AND h.cikissaat IS NULL"
        else:
            condition = "AND (h.girissaat IS NULL OR h.cikissaat IS NULL)"
        
        result = query_db(f'''
            SELECT 
                TO_CHAR(h.tarih, 'DD.MM.YYYY') as tarih,
                p.kartno, p.sicilno, p.adi, p.soyadi,
                TO_CHAR(h.girissaat, 'HH24:MI') as giris,
                TO_CHAR(h.cikissaat, 'HH24:MI') as cikis,
                CASE 
                    WHEN h.girissaat IS NULL THEN 'Giriş Yok'
                    WHEN h.cikissaat IS NULL THEN 'Çıkış Yok'
                    ELSE ''
                END as eksik
            FROM {SCHEMA}.hareketler h
            LEFT JOIN {SCHEMA}.personel p ON h.personelid = p.id
            WHERE h.tarih BETWEEN %s AND %s
            {condition}
            ORDER BY h.tarih DESC, p.adi
        ''', (start, end))
        
        return jsonify(result or [])
    
    # =========================================================================
    # 15 - ELLE MÜDAHALE YAPILAN HAREKETLER
    # =========================================================================
    @app.route('/api/elle-mudahale', methods=['GET'])
    def get_elle_mudahale():
        """15 - Elle Müdahale Yapılan Hareketler"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        
        result = query_db(f'''
            SELECT 
                TO_CHAR(h.tarih, 'DD.MM.YYYY') as tarih,
                p.kartno, p.sicilno, p.adi, p.soyadi,
                TO_CHAR(h.girissaat, 'HH24:MI') as giris,
                TO_CHAR(h.cikissaat, 'HH24:MI') as cikis,
                CASE WHEN h.girismudahale = 1 THEN 'Evet' ELSE 'Hayır' END as giris_mudahale,
                CASE WHEN h.cikismudahale = 1 THEN 'Evet' ELSE 'Hayır' END as cikis_mudahale
            FROM {SCHEMA}.hareketler h
            LEFT JOIN {SCHEMA}.personel p ON h.personelid = p.id
            WHERE h.tarih BETWEEN %s AND %s
            AND (h.girismudahale = 1 OR h.cikismudahale = 1)
            ORDER BY h.tarih DESC, p.adi
        ''', (start, end))
        
        return jsonify(result or [])
    
    # =========================================================================
    # 16 - İŞE GİREN PERSONELLER
    # =========================================================================
    @app.route('/api/ise-girenler', methods=['GET'])
    def get_ise_girenler():
        """16 - İşe Giren Personeller"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        
        result = query_db(f'''
            SELECT 
                kartno, sicilno, adi, soyadi,
                TO_CHAR(isegiris, 'DD.MM.YYYY') as ise_giris_tarihi
            FROM {SCHEMA}.personel
            WHERE isegiris BETWEEN %s AND %s
            ORDER BY isegiris DESC, adi
        ''', (start, end))
        
        return jsonify(result or [])
    
    # =========================================================================
    # 17 - İŞTEN AYRILAN PERSONELLER
    # =========================================================================
    @app.route('/api/isten-ayrilanlar', methods=['GET'])
    def get_isten_ayrilanlar():
        """17 - İşten Ayrılan Personeller"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        
        result = query_db(f'''
            SELECT 
                kartno, sicilno, adi, soyadi,
                TO_CHAR(isegiris, 'DD.MM.YYYY') as ise_giris_tarihi,
                TO_CHAR(isecikis, 'DD.MM.YYYY') as isten_cikis_tarihi
            FROM {SCHEMA}.personel
            WHERE isecikis BETWEEN %s AND %s
            ORDER BY isecikis DESC, adi
        ''', (start, end))
        
        return jsonify(result or [])
    
    # =========================================================================
    # 18 - PERSONEL İRTİBAT BİLGİLERİ
    # =========================================================================
    @app.route('/api/personel-irtibat', methods=['GET'])
    def get_personel_irtibat():
        """18 - Personel İrtibat Bilgileri"""
        result = query_db(f'''
            SELECT 
                kartno, sicilno, adi, soyadi,
                telefon, cepno, eposta, adres
            FROM {SCHEMA}.personel
            WHERE isegiris IS NOT NULL AND (isecikis IS NULL)
            ORDER BY adi, soyadi
        ''')
        
        return jsonify(result or [])
    
    # =========================================================================
    # 19 - TATİL GÜNÜ ÇALIŞANLAR
    # =========================================================================
    @app.route('/api/tatil-calisanlar', methods=['GET'])
    def get_tatil_calisanlar():
        """19 - Tatil Günü Çalışanlar"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        
        result = query_db(f'''
            SELECT 
                TO_CHAR(h.tarih, 'DD.MM.YYYY') as tarih,
                p.kartno, p.sicilno, p.adi, p.soyadi,
                TO_CHAR(h.girissaat, 'HH24:MI') as giris,
                TO_CHAR(h.cikissaat, 'HH24:MI') as cikis,
                t.tatiladi
            FROM {SCHEMA}.hareketler h
            LEFT JOIN {SCHEMA}.personel p ON h.personelid = p.id
            INNER JOIN {SCHEMA}.geneltatiller gt ON h.tarih = gt.tarih
            LEFT JOIN {SCHEMA}.tatiller t ON gt.tatilid = t.id
            WHERE h.tarih BETWEEN %s AND %s
            ORDER BY h.tarih, p.adi
        ''', (start, end))
        
        return jsonify(result or [])
    
    # =========================================================================
    # 20 - İZİN KULLANANLAR
    # =========================================================================
    @app.route('/api/izin-kullananlar', methods=['GET'])
    def get_izin_kullananlar():
        """20 - İzin Kullananlar"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        
        result = query_db(f'''
            SELECT 
                TO_CHAR(pi.tarih, 'DD.MM.YYYY') as tarih,
                p.kartno, p.sicilno, p.adi, p.soyadi,
                t.tatiladi as izin_tipi,
                pi.aciklama,
                CASE WHEN pi.guniciizin = 1 THEN 'Saatlik' ELSE 'Günlük' END as izin_suresi
            FROM {SCHEMA}.personelizin pi
            LEFT JOIN {SCHEMA}.personel p ON pi.personelid = p.id
            LEFT JOIN {SCHEMA}.tatiller t ON pi.tatilid = t.id
            WHERE pi.tarih BETWEEN %s AND %s
            ORDER BY pi.tarih DESC, p.adi
        ''', (start, end))
        
        return jsonify(result or [])
    
    # =========================================================================
    # 02 - PERSONEL BAZINDA HAREKET
    # =========================================================================
    @app.route('/api/personel-hareket', methods=['GET'])
    def get_personel_hareket():
        """02 - Personel Bazında Hareket Raporu"""
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        personel_id = request.args.get('personel_id')
        
        if not personel_id:
            return jsonify({'error': 'personel_id gerekli'}), 400
        
        result = query_db(f'''
            SELECT 
                TO_CHAR(h.tarih, 'DD.MM.YYYY') as tarih,
                TO_CHAR(h.girissaat, 'HH24:MI') as giris,
                TO_CHAR(h.cikissaat, 'HH24:MI') as cikis,
                EXTRACT(EPOCH FROM (h.cikissaat - h.girissaat))/60 as calisma_dk
            FROM {SCHEMA}.hareketler h
            WHERE h.personelid = %s AND h.tarih BETWEEN %s AND %s
            ORDER BY h.tarih
        ''', (personel_id, start, end))
        
        return jsonify(result or [])
    
    # =========================================================================
    # 23 - DEVAM DURUM ÇİZELGESİ
    # =========================================================================
    @app.route('/api/devam-cizelge', methods=['GET'])
    def get_devam_cizelge():
        """23 - Devam Durum Çizelgesi - Aylık özet"""
        yil = request.args.get('yil', datetime.now().year)
        ay = request.args.get('ay', datetime.now().month)
        
        # Ayın ilk ve son günü
        start = f"{yil}-{int(ay):02d}-01"
        if int(ay) == 12:
            end = f"{int(yil)+1}-01-01"
        else:
            end = f"{yil}-{int(ay)+1:02d}-01"
        
        # Personel listesi
        personeller = query_db(f'''
            SELECT id, kartno, sicilno, adi, soyadi
            FROM {SCHEMA}.personel
            WHERE isegiris IS NOT NULL AND (isecikis IS NULL OR isecikis >= %s)
            ORDER BY adi, soyadi
        ''', (start,))
        
        cizelge = []
        for per in (personeller or []):
            # Ay içindeki hareketler
            hareketler = query_db(f'''
                SELECT 
                    EXTRACT(DAY FROM tarih) as gun,
                    girissaat, cikissaat
                FROM {SCHEMA}.hareketler
                WHERE personelid = %s AND tarih >= %s AND tarih < %s
            ''', (per['id'], start, end))
            
            # İzinler
            izinler = query_db(f'''
                SELECT 
                    EXTRACT(DAY FROM tarih) as gun,
                    t.tatiladi
                FROM {SCHEMA}.personelizin pi
                LEFT JOIN {SCHEMA}.tatiller t ON pi.tatilid = t.id
                WHERE pi.personelid = %s AND pi.tarih >= %s AND pi.tarih < %s
            ''', (per['id'], start, end))
            
            gunler = {}
            for h in (hareketler or []):
                gun = int(h['gun'])
                gunler[gun] = 'G'  # Geldi
            
            for i in (izinler or []):
                gun = int(i['gun'])
                gunler[gun] = 'İ'  # İzinli
            
            cizelge.append({
                'sicilno': per.get('sicilno', ''),
                'adi': per.get('adi', ''),
                'soyadi': per.get('soyadi', ''),
                'gunler': gunler,
                'toplam_gun': len([g for g in gunler.values() if g == 'G']),
                'izin_gun': len([g for g in gunler.values() if g == 'İ'])
            })
        
        return jsonify(cizelge)
