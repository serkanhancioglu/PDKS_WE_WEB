"""
Hesap.inc - Veritabani Sorgu Fonksiyonlari
BIREBIR PHP karsiliklari - DB baglantisi gerektirir
Kaynak: /MikroPer/Raporlar/Hesap.inc
"""
from datetime import datetime, timedelta
from hesap_fonksiyonlar import time_to_minute, dakika_to_saat, saat_hesapla


def hareketleri_al(db_cursor, schema, per_id, aktif_tarih, ilk_vardiya_dunmu, en_erken_giris, yarin_en_erken_giris):
    """Orijinal: function hareketleri_al
    
    Personelin belirli tarihteki hareketlerini alir
    Gece vardiyasi icin ertesi gun hareketlerini de kontrol eder
    """
    hareketler_tmp = []
    
    tarih1 = aktif_tarih
    tarih2 = (datetime.strptime(aktif_tarih, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    
    en_erken_giris_saat = dakika_to_saat(en_erken_giris) or "00:00"
    yarin_en_erken_giris_saat = dakika_to_saat(yarin_en_erken_giris) or "00:00"
    
    # Bugunun hareketleri
    sorgu = f"""
        SELECT tarih, girissaat, giriscihazid, girismudahale, 
               tarihcikis, cikissaat, cikiscihazid, cikismudahale
        FROM {schema}.hareketler
        WHERE personelid = %s AND tarih = %s
        AND ((girissaat >= %s) OR (girissaat IS NULL AND cikissaat > %s))
        ORDER BY girissaat, cikissaat
    """
    db_cursor.execute(sorgu, (per_id, tarih1, en_erken_giris_saat, en_erken_giris_saat))
    
    for row in db_cursor.fetchall():
        tarih, giris_saat, giris_cihaz, giris_mudahale, tarih_cikis, cikis_saat, cikis_cihaz, cikis_mudahale = row
        
        giris_int = time_to_minute(str(giris_saat) if giris_saat else None)
        cikis_int = time_to_minute(str(cikis_saat) if cikis_saat else None)
        
        if (giris_int > cikis_int) and (cikis_int > -1):
            cikis_int += 1440
        
        en_kucuk_giris = giris_int if giris_int > -1 else cikis_int
        en_buyuk_cikis = cikis_int if cikis_int > -1 else giris_int
        
        hareketler_tmp.append({
            "tarih": str(tarih),
            "giris_int": giris_int,
            "cikis_int": cikis_int,
            "giris_saat": str(giris_saat) if giris_saat else "",
            "cikis_saat": str(cikis_saat) if cikis_saat else "",
            "giris_mudahale": giris_mudahale or 0,
            "cikis_mudahale": cikis_mudahale or 0,
            "giris_cihaz": giris_cihaz or 0,
            "cikis_cihaz": cikis_cihaz or 0,
            "en_kucuk_giris": en_kucuk_giris,
            "en_buyuk_cikis": en_buyuk_cikis,
            "siralama_saati": giris_int if giris_int > -5000 else cikis_int,
            "islem_giris": giris_int if giris_int > -5000 else cikis_int,
            "islem_cikis": cikis_int if cikis_int > -5000 else giris_int
        })
    
    # Ertesi gunun erken hareketleri (gece vardiyasi)
    sorgu2 = f"""
        SELECT tarih, girissaat, giriscihazid, girismudahale,
               tarihcikis, cikissaat, cikiscihazid, cikismudahale
        FROM {schema}.hareketler
        WHERE personelid = %s AND tarih = %s
        AND ((girissaat < %s) OR (girissaat IS NULL AND cikissaat < %s))
        ORDER BY girissaat, cikissaat
    """
    db_cursor.execute(sorgu2, (per_id, tarih2, yarin_en_erken_giris_saat, yarin_en_erken_giris_saat))
    
    for row in db_cursor.fetchall():
        tarih, giris_saat, giris_cihaz, giris_mudahale, tarih_cikis, cikis_saat, cikis_cihaz, cikis_mudahale = row
        
        giris_int = time_to_minute(str(giris_saat) if giris_saat else None) + 1440
        cikis_int = time_to_minute(str(cikis_saat) if cikis_saat else None) + 1440
        
        if (giris_int > cikis_int) and (cikis_int > -1):
            cikis_int += 1440
        
        en_kucuk_giris = giris_int if giris_int > -1 else cikis_int
        en_buyuk_cikis = cikis_int if cikis_int > -1 else giris_int
        
        hareketler_tmp.append({
            "tarih": str(tarih),
            "giris_int": giris_int,
            "cikis_int": cikis_int,
            "giris_saat": str(giris_saat) if giris_saat else "",
            "cikis_saat": str(cikis_saat) if cikis_saat else "",
            "giris_mudahale": giris_mudahale or 0,
            "cikis_mudahale": cikis_mudahale or 0,
            "giris_cihaz": giris_cihaz or 0,
            "cikis_cihaz": cikis_cihaz or 0,
            "en_kucuk_giris": en_kucuk_giris,
            "en_buyuk_cikis": en_buyuk_cikis,
            "siralama_saati": giris_int if giris_int > -5000 else cikis_int,
            "islem_giris": giris_int if giris_int > -5000 else cikis_int,
            "islem_cikis": cikis_int if cikis_int > -5000 else giris_int
        })
    
    hareketler_tmp.sort(key=lambda x: x.get("siralama_saati", 0))
    return hareketler_tmp


def bordrolari_al(db_cursor, schema, vardiya):
    """Orijinal: function bordrolari_al
    
    Vardiya icin bordro tanimlarini alir
    BordroTipi: 1=Normal, 5=Fazla Mesai
    """
    bordrolar = []
    
    vardiya_id = vardiya.get("vardiya_id") or vardiya.get("gunlukhesapid")
    en_erken_giris = vardiya.get("en_erken_giris", 0)
    en_erken_giris_str = dakika_to_saat(en_erken_giris % 1440) or "00:00"
    
    # En erken giristen sonraki bordrolar
    sorgu1 = f"""
        SELECT g.basla, g.bitis, g.min, g.max, g.ekle, b.bordrotipi
        FROM {schema}.gunluk_hesap_bordrolar g
        LEFT JOIN {schema}.bordroalanlari b ON b.id = g.bordroid
        WHERE g.gunlukhesapid = %s AND b.bordrotipi IN (1, 5) AND g.basla >= %s
        ORDER BY g.basla
    """
    db_cursor.execute(sorgu1, (vardiya_id, en_erken_giris_str))
    
    for row in db_cursor.fetchall():
        basla, bitis, min_val, max_val, ekle, bordro_tipi = row
        
        bordro_basla = time_to_minute(str(basla) if basla else None)
        bordro_bitis = time_to_minute(str(bitis) if bitis else None)
        
        if bordro_basla > bordro_bitis:
            bordro_bitis += 1440
        if en_erken_giris >= 1440:
            bordro_basla += 1440
            bordro_bitis += 1440
        
        bordrolar.append({
            "bordro_basla": bordro_basla,
            "bordro_bitis": bordro_bitis,
            "min": time_to_minute(str(min_val) if min_val else None),
            "max": time_to_minute(str(max_val) if max_val else None),
            "ekle": time_to_minute(str(ekle) if ekle else None),
            "bordro_tipi": bordro_tipi
        })
    
    # En erken giristen onceki bordrolar (ertesi gune ait)
    sorgu2 = f"""
        SELECT g.basla, g.bitis, g.min, g.max, g.ekle, b.bordrotipi
        FROM {schema}.gunluk_hesap_bordrolar g
        LEFT JOIN {schema}.bordroalanlari b ON b.id = g.bordroid
        WHERE g.gunlukhesapid = %s AND b.bordrotipi IN (1, 5) AND g.basla < %s
        ORDER BY g.basla
    """
    db_cursor.execute(sorgu2, (vardiya_id, en_erken_giris_str))
    
    for row in db_cursor.fetchall():
        basla, bitis, min_val, max_val, ekle, bordro_tipi = row
        
        bordro_basla = time_to_minute(str(basla) if basla else None) + 1440
        bordro_bitis = time_to_minute(str(bitis) if bitis else None) + 1440
        
        if bordro_basla > bordro_bitis:
            bordro_bitis += 1440
        
        bordrolar.append({
            "bordro_basla": bordro_basla,
            "bordro_bitis": bordro_bitis,
            "min": time_to_minute(str(min_val) if min_val else None),
            "max": time_to_minute(str(max_val) if max_val else None),
            "ekle": time_to_minute(str(ekle) if ekle else None),
            "bordro_tipi": bordro_tipi
        })
    
    return bordrolar


def molalari_al(db_cursor, schema, vardiya):
    """Orijinal: function molalari_al - Mola tanimlari"""
    molalar = []
    vardiya_id = vardiya.get("vardiya_id") or vardiya.get("gunlukhesapid")
    en_erken_giris = vardiya.get("en_erken_giris", 0)
    
    try:
        sorgu = f"SELECT basla, bitis, sure FROM {schema}.gunluk_mola WHERE gunlukhesapid = %s ORDER BY basla"
        db_cursor.execute(sorgu, (vardiya_id,))
        
        for row in db_cursor.fetchall():
            basla, bitis, sure = row
            mola_basla = time_to_minute(str(basla) if basla else None)
            mola_bitis = time_to_minute(str(bitis) if bitis else None)
            
            if mola_basla > mola_bitis:
                mola_bitis += 1440
            if en_erken_giris >= 1440:
                mola_basla += 1440
                mola_bitis += 1440
            
            molalar.append({
                "mola_basla": mola_basla,
                "mola_bitis": mola_bitis,
                "mola_sure": time_to_minute(str(sure) if sure else None)
            })
    except:
        pass
    return molalar


def vardiyalari_al(db_cursor, schema, gunluk_plan_id, ilk_vardiya_dunmu=0, ilk_vardiya_id=0):
    """Orijinal: function vardiyalari_al - Vardiya tanimlari
    
    PHP'deki tum alanlar dahil edildi:
    - vardiya_gun: Vardiya gun sayisi
    - gec_erken_hesaplama: Gec gelme/erken cikma hesaplama yontemi
    """
    vardiyalar = []
    
    sorgu = f"""
        SELECT v.id, v.basla, v.bitis, v.gunlukhesapid, v.tatildurumu,
               g.girissaati, g.cikissaati, g.gecgelme, g.erkencikma,
               g.enerkengiris, g.engeccikis, g.hesaptipi,
               g.vardiyagun, g.gecerkenhesaplama
        FROM {schema}.vardiyalar v
        LEFT JOIN {schema}.gunluk_hesap g ON v.gunlukhesapid = g.id
        WHERE v.vardiyaid = %s ORDER BY g.vardiyagun DESC, v.basla
    """
    db_cursor.execute(sorgu, (gunluk_plan_id,))
    
    for row in db_cursor.fetchall():
        (v_id, basla, bitis, gunlukhesapid, tatildurumu,
         giris_saati, cikis_saati, gec_gelme, erken_cikma,
         en_erken_giris, en_gec_cikis, hesap_tipi,
         vardiya_gun, gec_erken_hesaplama) = row
        
        vardiya = {
            "vardiya_id": gunlukhesapid,
            "tatil_id": tatildurumu or 0,
            "hesap_tipi": hesap_tipi or 0,
            "vardiya_gun": vardiya_gun or 0,
            "gec_erken_hesaplama": gec_erken_hesaplama or 0,
            "giris_saat": time_to_minute(str(giris_saati) if giris_saati else None),
            "cikis_saat": time_to_minute(str(cikis_saati) if cikis_saati else None),
            "gec_gelme": time_to_minute(str(gec_gelme) if gec_gelme else None),
            "erken_cikma": time_to_minute(str(erken_cikma) if erken_cikma else None),
            "en_erken_giris": time_to_minute(str(en_erken_giris) if en_erken_giris else None),
            "en_gec_cikis": time_to_minute(str(en_gec_cikis) if en_gec_cikis else None)
        }
        
        # Gece vardiyasi duzeltmeleri
        if vardiya["giris_saat"] > vardiya["en_erken_giris"]:
            vardiya["en_erken_giris"] += 1440
        if vardiya["giris_saat"] > vardiya["en_gec_cikis"]:
            vardiya["en_gec_cikis"] += 1440
        if vardiya["giris_saat"] > vardiya["gec_gelme"]:
            vardiya["gec_gelme"] += 1440
        if vardiya["giris_saat"] > vardiya["erken_cikma"]:
            vardiya["erken_cikma"] += 1440
        if vardiya["giris_saat"] > vardiya["cikis_saat"]:
            vardiya["cikis_saat"] += 1440
        
        vardiyalar.append(vardiya)
    
    return vardiyalar


def gunluk_plan_al(db_cursor, schema, tarih, personel_id, hesap_kodu):
    """Orijinal: function gunluk_plan_al
    
    Oncelik: Personel Ozel Plan > Grup Ozel Plan > Haftalik Plan
    """
    gunler = ['pazar', 'pazartesi', 'sali', 'carsamba', 'persembe', 'cuma', 'cumartesi']
    
    # 1. Personel Ozel Plani
    try:
        sorgu1 = f"SELECT vardiyaid FROM {schema}.personel_ozel_planlari WHERE vardiyaid > 0 AND personelid = %s AND tarih = %s"
        db_cursor.execute(sorgu1, (personel_id, tarih))
        row = db_cursor.fetchone()
        if row:
            return row[0]
    except:
        pass
    
    # 2. Grup Ozel Plani
    try:
        sorgu2 = f"SELECT vardiyaid FROM {schema}.grupozelplanlari WHERE vardiyaid > 0 AND grupid = %s AND tarih = %s"
        db_cursor.execute(sorgu2, (hesap_kodu, tarih))
        row = db_cursor.fetchone()
        if row:
            return row[0]
    except:
        pass
    
    # 3. Haftalik Plan
    try:
        tarih_obj = datetime.strptime(tarih, '%Y-%m-%d')
        gun_index = (tarih_obj.weekday() + 1) % 7
        haftanin_gunu = gunler[gun_index]
        
        sorgu3 = f"SELECT {haftanin_gunu} FROM {schema}.planlar WHERE grupid = %s AND tarih <= %s ORDER BY tarih DESC LIMIT 1"
        db_cursor.execute(sorgu3, (hesap_kodu, tarih))
        row = db_cursor.fetchone()
        if row:
            return row[0]
    except:
        pass
    
    return -1


def gunluk_izin_al(db_cursor, schema, per_id, aktif_tarih, vardiya):
    """Orijinal: function gunluk_izin_al - Izin durumu"""
    gunluk_izin = {}
    
    try:
        sorgu = f"""
            SELECT p.aciklama, t.id, t.tatiladi, t.ucrettipi
            FROM {schema}.personelizin p
            LEFT JOIN {schema}.tatiller t ON t.id = p.tatilid
            WHERE p.personelid = %s AND p.tarih = %s AND (p.guniciizin = 0 OR p.guniciizin IS NULL)
            ORDER BY p.id DESC
        """
        db_cursor.execute(sorgu, (per_id, aktif_tarih))
        row = db_cursor.fetchone()
        
        if row:
            aciklama, tatil_id, tatil_adi, ucret_tipi = row
            gunluk_izin = {"tatil_id": tatil_id, "tatil_adi": tatil_adi, "aciklama": aciklama, "ucret_tipi": ucret_tipi, "plan_tatil": 0}
        elif vardiya and vardiya.get("tatil_id", 0) > 0:
            sorgu2 = f"SELECT tatiladi, ucrettipi FROM {schema}.tatiller WHERE id = %s"
            db_cursor.execute(sorgu2, (vardiya["tatil_id"],))
            row2 = db_cursor.fetchone()
            if row2:
                gunluk_izin = {"tatil_id": vardiya["tatil_id"], "tatil_adi": row2[0], "ucret_tipi": row2[1], "plan_tatil": 1}
    except:
        pass
    
    return gunluk_izin


def saatlik_izinleri_al(db_cursor, schema, per_id, tarih, vardiya):
    """Orijinal: function saatlik_izinleri_al - Gun ici izinler"""
    izinler = []
    try:
        sorgu = f"""
            SELECT p.basla, p.bitis, p.aciklama, t.tatiladi
            FROM {schema}.personelizin p
            LEFT JOIN {schema}.tatiller t ON t.id = p.tatilid
            WHERE p.personelid = %s AND p.tarih = %s AND p.guniciizin = 1
            ORDER BY p.basla
        """
        db_cursor.execute(sorgu, (per_id, tarih))
        for row in db_cursor.fetchall():
            basla, bitis, aciklama, tatil_adi = row
            izinler.append({
                "basla": time_to_minute(str(basla) if basla else None),
                "bitis": time_to_minute(str(bitis) if bitis else None),
                "aciklama": aciklama, "tatil_adi": tatil_adi
            })
    except:
        pass
    return izinler


def gunluk_izinleri_al(db_cursor, schema, per_id, tarih):
    """Orijinal: function gunluk_izinleri_al - String donusu"""
    try:
        sorgu = f"""
            SELECT t.tatiladi, p.aciklama
            FROM {schema}.personelizin p
            INNER JOIN {schema}.tatiller t ON p.tatilid = t.id
            WHERE p.personelid = %s AND p.tarih = %s AND (p.guniciizin != 1 OR p.guniciizin IS NULL)
        """
        db_cursor.execute(sorgu, (per_id, tarih))
        row = db_cursor.fetchone()
        if row:
            tatil_adi, aciklama = row
            return f"{tatil_adi} ({aciklama})" if aciklama else tatil_adi
    except:
        pass
    return ""


def fazla_mesai_hesapla(db_cursor, schema, hareket, vardiya):
    """Fazla mesai hesaplama - Orijinal PHP mantigina gore"""
    toplam_fm = 0
    
    if not hareket or not vardiya:
        return toplam_fm
    
    giris_int = hareket.get("giris_int", -1)
    cikis_int = hareket.get("cikis_int", -1)
    
    if giris_int < 0 or cikis_int < 0:
        return toplam_fm
    
    bordrolar = bordrolari_al(db_cursor, schema, vardiya)
    
    for bordro in bordrolar:
        if bordro.get("bordro_tipi") != 5:
            continue
        
        bordro_basla = bordro.get("bordro_basla", 0)
        bordro_bitis = bordro.get("bordro_bitis", 0)
        min_dk = bordro.get("min", 0)
        max_dk = bordro.get("max", 0)
        ekle_dk = bordro.get("ekle", 0)
        
        kesisim = saat_hesapla(giris_int, cikis_int, bordro_basla, bordro_bitis)
        
        if min_dk > 0 and kesisim < min_dk:
            kesisim = 0
        if max_dk > 0 and kesisim > max_dk:
            kesisim = max_dk
        if kesisim > 0 and ekle_dk > 0:
            kesisim += ekle_dk
        
        toplam_fm += kesisim
    
    return toplam_fm
