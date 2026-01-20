"""
Hesap.inc - Orijinal PHP fonksiyonlarinin BIREBIR Python karsiliklari
VARSAYIM YOK - Orijinal mantik korunmustur
Kaynak: /MikroPer/Raporlar/Hesap.inc (2296 satir)
"""
from datetime import datetime, timedelta
import math


def durum_hesapla(pay, payda, alt_pay, alt_payda, carpan, ekle):
    """Orijinal: function durum_hesapla - Progress bar hesaplama"""
    return math.floor(carpan * ((pay + (alt_pay / alt_payda)) / payda)) + ekle


def tarih_gun_farki(tarihinden, tarihine):
    """Orijinal: function tarih_gun_farki - Tarih farki (gun)"""
    try:
        d1 = datetime.strptime(str(tarihinden), '%Y-%m-%d')
        d2 = datetime.strptime(str(tarihine), '%Y-%m-%d')
        return (d2 - d1).days
    except:
        return 0


def time_to_minute(saat):
    """Orijinal: function time_to_minute - Saat -> dakika"""
    if not saat or saat == "" or saat == "--:--" or saat is None:
        return -10000
    try:
        saat = str(saat).strip()
        if ':' in saat:
            parts = saat.split(':')
            h = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else 0
            return (h * 60) + m
        return -10000
    except:
        return -10000


def time_to_minute_saat3hane(saat):
    """Orijinal: function time_to_minute_saat3hane - 3 haneli saat (orn: 100:30)"""
    if not saat or saat == "" or saat == "---:--":
        return -10000
    try:
        saat = str(saat).strip()
        gelen_saat = int(saat[0:3])
        gelen_dakika = int(saat[4:6])
        return (gelen_saat * 60) + gelen_dakika
    except:
        return -10000


def saat_dakika(saat_str):
    """Orijinal: function saat_dakika - Format duzenleme (HH:MM)"""
    if not saat_str:
        return saat_str
    saat_str = str(saat_str).strip()
    if len(saat_str) > 5:
        return saat_str[0:5]
    return saat_str


def saat_dakika_bos(saat_str):
    """Orijinal: function saat_dakika_bos - Bos saat kontrolu"""
    if not saat_str:
        return saat_str
    saat_str = str(saat_str).strip()
    if len(saat_str) > 5:
        return saat_str[0:5]
    if saat_str == "":
        return "- : -"
    return saat_str


def saatdakika_int(gelensaat):
    """Orijinal: function saatdakika_int - Saat string -> integer dakika"""
    if not gelensaat:
        return 0
    gelensaat = str(gelensaat).strip()
    try:
        if len(gelensaat) > 5:
            s_saat = int(gelensaat[0:3])
            s_dakika = int(gelensaat[4:6])
        else:
            s_saat = int(gelensaat[0:2])
            s_dakika = int(gelensaat[3:5])
        return (s_saat * 60) + s_dakika
    except:
        return 0


def sql_tarih_to_tarih(tarih):
    """Orijinal: function sql_tarih_to_tarih - YYYY-MM-DD -> DD.MM.YYYY"""
    if not tarih or tarih == "":
        return ""
    tarih = str(tarih)
    if len(tarih) >= 10:
        return f"{tarih[8:10]}.{tarih[5:7]}.{tarih[0:4]}"
    return ""


def dakika_to_saat(dakika):
    """Orijinal: function dakika_to_saat - Dakika -> HH:MM"""
    if dakika == 0 or dakika == "" or dakika is None:
        return ""
    try:
        dakika = int(dakika)
        ekran_saat = dakika // 60
        ekran_dakika = dakika % 60
        return f"{ekran_saat:02d}:{ekran_dakika:02d}"
    except:
        return ""


def saat_hesapla(giris, cikis, basla, bitis):
    """Orijinal: function saat_hesapla - BIREBIR PHP mantigi
    
    Bordro saat kesisim hesaplama
    Giris/cikis ile bordro baslangic/bitis arasindaki kesisimi hesaplar
    """
    if (giris < bitis) and (cikis > basla):
        if (giris < basla) or (cikis > bitis):
            if (giris > basla) or (cikis < bitis):
                if cikis < bitis:
                    sonuc = cikis - basla
                else:
                    sonuc = bitis - giris
            else:
                sonuc = bitis - basla
        else:
            sonuc = cikis - giris
    else:
        sonuc = 0
    return sonuc


def ilkgiris_soncikis_hesapla(hareketler):
    """Orijinal: function ilkgiris_soncikis_hesapla
    
    Birden fazla hareket varsa ilk giris ve son cikisi hesaplar
    """
    if not hareketler or len(hareketler) == 0:
        return hareketler
    
    hareket_sonuc = {}
    
    for hs, hareket in enumerate(hareketler):
        if hs == 0:
            hareket_sonuc = hareket.copy()
            
            if hareket_sonuc.get("giris_int", -1) < 0:
                hareket_sonuc["en_kucuk_giris"] = hareket_sonuc.get("cikis_int", -1)
                hareket_sonuc["giris_int"] = hareket_sonuc.get("cikis_int", -1)
                hareket_sonuc["giris_saat"] = hareket_sonuc.get("cikis_saat", "")
                hareket_sonuc["giris_mudahale"] = hareket_sonuc.get("cikis_mudahale", 0)
                hareket_sonuc["giris_cihaz"] = hareket_sonuc.get("cikis_cihaz", 0)
            
            if hareket_sonuc.get("cikis_int", -1) < 0:
                hareket_sonuc["en_buyuk_cikis"] = hareket_sonuc.get("giris_int", -1)
                hareket_sonuc["cikis_int"] = hareket_sonuc.get("giris_int", -1)
                hareket_sonuc["cikis_saat"] = hareket_sonuc.get("giris_saat", "")
                hareket_sonuc["cikis_mudahale"] = hareket_sonuc.get("giris_mudahale", 0)
                hareket_sonuc["cikis_cihaz"] = hareket_sonuc.get("giris_cihaz", 0)
        else:
            # Daha kucuk giris bul
            if hareket.get("giris_int", -1) > -1 and hareket.get("giris_int", 99999) < hareket_sonuc.get("giris_int", 99999):
                hareket_sonuc["giris_int"] = hareket["giris_int"]
                hareket_sonuc["giris_saat"] = hareket.get("giris_saat", "")
                hareket_sonuc["giris_mudahale"] = hareket.get("giris_mudahale", 0)
                hareket_sonuc["giris_cihaz"] = hareket.get("giris_cihaz", 0)
                hareket_sonuc["en_kucuk_giris"] = hareket["giris_int"]
            
            # Cikis da girise gore kucukse
            if hareket.get("cikis_int", -1) > -1 and hareket.get("cikis_int", 99999) < hareket_sonuc.get("giris_int", 99999):
                hareket_sonuc["giris_int"] = hareket["cikis_int"]
                hareket_sonuc["giris_saat"] = hareket.get("cikis_saat", "")
                hareket_sonuc["giris_mudahale"] = hareket.get("cikis_mudahale", 0)
                hareket_sonuc["giris_cihaz"] = hareket.get("cikis_cihaz", 0)
                hareket_sonuc["en_kucuk_giris"] = hareket["cikis_int"]
            
            # Daha buyuk cikis bul
            if hareket.get("cikis_int", -1) > -1 and hareket.get("cikis_int", -1) > hareket_sonuc.get("cikis_int", -1):
                hareket_sonuc["cikis_int"] = hareket["cikis_int"]
                hareket_sonuc["cikis_saat"] = hareket.get("cikis_saat", "")
                hareket_sonuc["cikis_mudahale"] = hareket.get("cikis_mudahale", 0)
                hareket_sonuc["cikis_cihaz"] = hareket.get("cikis_cihaz", 0)
                hareket_sonuc["en_buyuk_cikis"] = hareket["cikis_int"]
            
            # Giris da cikisa gore buyukse
            if hareket.get("giris_int", -1) > -1 and hareket.get("giris_int", -1) > hareket_sonuc.get("cikis_int", -1):
                hareket_sonuc["cikis_int"] = hareket["giris_int"]
                hareket_sonuc["cikis_saat"] = hareket.get("giris_saat", "")
                hareket_sonuc["cikis_mudahale"] = hareket.get("giris_mudahale", 0)
                hareket_sonuc["cikis_cihaz"] = hareket.get("giris_cihaz", 0)
                hareket_sonuc["en_buyuk_cikis"] = hareket["giris_int"]
    
    return [hareket_sonuc]


# ============================================================================
# VERITABANI SORGULARI - Bu fonksiyonlar db baglantisi gerektirir
# ============================================================================

def hareketleri_al(db_cursor, schema, per_id, aktif_tarih, ilk_vardiya_dunmu, en_erken_giris, yarin_en_erken_giris):
    """Orijinal: function hareketleri_al
    
    Personelin belirli tarihteki hareketlerini alir
    Gece vardiyasi icin ertesi gun hareketlerini de kontrol eder
    """
    hareketler_tmp = []
    
    tarih1 = aktif_tarih
    # Ertesi gun
    tarih2 = (datetime.strptime(aktif_tarih, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    
    en_erken_giris_saat = dakika_to_saat(en_erken_giris)
    yarin_en_erken_giris_saat = dakika_to_saat(yarin_en_erken_giris)
    
    # Ilk sorgu - bugunun hareketleri
    sorgu = f"""
        SELECT tarih, girissaat, giriscihazid, girismudahale, 
               tarihcikis, cikissaat, cikiscihazid, cikismudahale
        FROM {schema}.hareketler
        WHERE personelid = %s AND tarih = %s
        AND ((girissaat >= %s) OR (girissaat IS NULL AND cikissaat > %s))
        ORDER BY girissaat, cikissaat
    """
    db_cursor.execute(sorgu, (per_id, tarih1, en_erken_giris_saat, en_erken_giris_saat))
    rows = db_cursor.fetchall()
    
    for row in rows:
        tarih, giris_saat, giris_cihaz, giris_mudahale, tarih_cikis, cikis_saat, cikis_cihaz, cikis_mudahale = row
        
        giris_int = time_to_minute(str(giris_saat) if giris_saat else None)
        cikis_int = time_to_minute(str(cikis_saat) if cikis_saat else None)
        
        # Gece vardiyasi - cikis ertesi gune tasiyorsa
        if (giris_int > cikis_int) and (cikis_int > -1):
            cikis_int += 1440
        
        en_kucuk_giris = giris_int if giris_int > -1 else cikis_int
        en_buyuk_cikis = cikis_int if cikis_int > -1 else giris_int
        
        hareket = {
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
        }
        hareketler_tmp.append(hareket)
    
    # Ikinci sorgu - ertesi gunun erken hareketleri (gece vardiyasi icin)
    sorgu2 = f"""
        SELECT tarih, girissaat, giriscihazid, girismudahale,
               tarihcikis, cikissaat, cikiscihazid, cikismudahale
        FROM {schema}.hareketler
        WHERE personelid = %s AND tarih = %s
        AND ((girissaat < %s) OR (girissaat IS NULL AND cikissaat < %s))
        ORDER BY girissaat, cikissaat
    """
    db_cursor.execute(sorgu2, (per_id, tarih2, yarin_en_erken_giris_saat, yarin_en_erken_giris_saat))
    rows2 = db_cursor.fetchall()
    
    for row in rows2:
        tarih, giris_saat, giris_cihaz, giris_mudahale, tarih_cikis, cikis_saat, cikis_cihaz, cikis_mudahale = row
        
        # Ertesi gun +1440 dk ekle
        giris_int = time_to_minute(str(giris_saat) if giris_saat else None) + 1440
        cikis_int = time_to_minute(str(cikis_saat) if cikis_saat else None) + 1440
        
        if (giris_int > cikis_int) and (cikis_int > -1):
            cikis_int += 1440
        
        en_kucuk_giris = giris_int if giris_int > -1 else cikis_int
        en_buyuk_cikis = cikis_int if cikis_int > -1 else giris_int
        
        hareket = {
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
        }
        hareketler_tmp.append(hareket)
    
    # Siralama saatine gore sirala
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
    
    en_erken_giris_str = dakika_to_saat(en_erken_giris % 1440)
    if not en_erken_giris_str:
        en_erken_giris_str = "00:00"
    
    # Ilk sorgu - en erken giristen sonraki bordrolar
    sorgu1 = f"""
        SELECT g.basla, g.bitis, g.min, g.max, g.ekle, b.bordrotipi
        FROM {schema}.gunluk_hesap_bordrolar g
        LEFT JOIN {schema}.bordroalanlari b ON b.id = g.bordroid
        WHERE g.gunlukhesapid = %s 
        AND b.bordrotipi IN (1, 5)
        AND g.basla >= %s
        ORDER BY g.basla
    """
    db_cursor.execute(sorgu1, (vardiya_id, en_erken_giris_str))
    rows1 = db_cursor.fetchall()
    
    for row in rows1:
        basla, bitis, min_val, max_val, ekle, bordro_tipi = row
        
        bordro_basla = time_to_minute(str(basla) if basla else None)
        bordro_bitis = time_to_minute(str(bitis) if bitis else None)
        
        # Gece vardiyasi - bitis ertesi gune tasiyorsa
        if bordro_basla > bordro_bitis:
            bordro_bitis += 1440
        
        # Eger en erken giris 1440'tan buyukse (ertesi gun)
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
    
    # Ikinci sorgu - en erken giristen onceki bordrolar
    sorgu2 = f"""
        SELECT g.basla, g.bitis, g.min, g.max, g.ekle, b.bordrotipi
        FROM {schema}.gunluk_hesap_bordrolar g
        LEFT JOIN {schema}.bordroalanlari b ON b.id = g.bordroid
        WHERE g.gunlukhesapid = %s
        AND b.bordrotipi IN (1, 5)
        AND g.basla < %s
        ORDER BY g.basla
    """
    db_cursor.execute(sorgu2, (vardiya_id, en_erken_giris_str))
    rows2 = db_cursor.fetchall()
    
    for row in rows2:
        basla, bitis, min_val, max_val, ekle, bordro_tipi = row
        
        bordro_basla = time_to_minute(str(basla) if basla else None)
        bordro_bitis = time_to_minute(str(bitis) if bitis else None)
        
        if bordro_basla > bordro_bitis:
            bordro_bitis += 1440
        
        # Ertesi gune ait olarak isaretle
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
    
    return bordrolar


def molalari_al(db_cursor, schema, vardiya):
    """Orijinal: function molalari_al
    
    Vardiya icin mola tanimlarini alir
    """
    molalar = []
    
    vardiya_id = vardiya.get("vardiya_id") or vardiya.get("gunlukhesapid")
    en_erken_giris = vardiya.get("en_erken_giris", 0)
    
    sorgu = f"""
        SELECT basla, bitis, sure
        FROM {schema}.gunluk_mola
        WHERE gunlukhesapid = %s
        ORDER BY basla
    """
    try:
        db_cursor.execute(sorgu, (vardiya_id,))
        rows = db_cursor.fetchall()
        
        for row in rows:
            basla, bitis, sure = row
            
            mola_basla = time_to_minute(str(basla) if basla else None)
            mola_bitis = time_to_minute(str(bitis) if bitis else None)
            mola_sure = time_to_minute(str(sure) if sure else None)
            
            if mola_basla > mola_bitis:
                mola_bitis += 1440
            
            if en_erken_giris >= 1440:
                mola_basla += 1440
                mola_bitis += 1440
            
            molalar.append({
                "mola_basla": mola_basla,
                "mola_bitis": mola_bitis,
                "mola_sure": mola_sure
            })
    except:
        pass  # Tablo yoksa bos liste don
    
    return molalar


def ara_eksikleri_hesapla(vardiya, molalar, hareketler):
    """Orijinal: function ara_eksikleri_hesapla
    
    Mola araliklarindaki eksikleri hesaplar
    """
    ara_eksik_toplam = 0
    
    if not molalar or not hareketler:
        return ara_eksik_toplam
    
    for mola in molalar:
        mola_basla = mola.get("mola_basla", 0)
        mola_bitis = mola.get("mola_bitis", 0)
        mola_sure = mola.get("mola_sure", 0)
        
        for hareket in hareketler:
            giris = hareket.get("islem_giris", 0)
            cikis = hareket.get("islem_cikis", 0)
            
            # Mola araligi ile hareket kesisimi
            kesisim = saat_hesapla(giris, cikis, mola_basla, mola_bitis)
            
            if kesisim > 0 and mola_sure > 0:
                eksik = mola_sure - kesisim
                if eksik > 0:
                    ara_eksik_toplam += eksik
    
    return ara_eksik_toplam


def vardiyalari_al(db_cursor, schema, gunluk_plan_id, ilk_vardiya_dunmu=0, ilk_vardiya_id=0):
    """Orijinal: function vardiyalari_al
    
    Gunluk plan icin vardiya tanimlarini alir
    """
    vardiyalar = []
    
    sorgu = f"""
        SELECT v.id, v.basla, v.bitis, v.gunlukhesapid, v.tatildurumu,
               g.girissaati, g.cikissaati, g.gecgelme, g.erkencikma,
               g.enerkengiris, g.engeccikis, g.hesaptipi
        FROM {schema}.vardiyalar v
        LEFT JOIN {schema}.gunluk_hesap g ON v.gunlukhesapid = g.id
        WHERE v.vardiyaid = %s
        ORDER BY v.basla
    """
    db_cursor.execute(sorgu, (gunluk_plan_id,))
    rows = db_cursor.fetchall()
    
    for vs, row in enumerate(rows):
        (v_id, basla, bitis, gunlukhesapid, tatildurumu,
         giris_saati, cikis_saati, gec_gelme, erken_cikma,
         en_erken_giris, en_gec_cikis, hesap_tipi) = row
        
        vardiya = {
            "vardiya_id": gunlukhesapid,
            "tatil_id": tatildurumu or 0,
            "hesap_tipi": hesap_tipi or 0,
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


def vardiya_bul(vardiyalar, en_kucuk_giris):
    """Orijinal: function vardiya_bul
    
    Giris saatine gore uygun vardiyayi bulur
    """
    if not vardiyalar:
        return None
    
    for vardiya in vardiyalar:
        en_erken = vardiya.get("en_erken_giris", 0)
        en_gec = vardiya.get("en_gec_cikis", 0)
        
        if en_kucuk_giris >= en_erken and en_kucuk_giris <= en_gec:
            return vardiya
    
    # Bulamazsa ilk vardiyayi don
    return vardiyalar[0] if vardiyalar else None


def gunluk_plan_al(db_cursor, schema, tarih, personel_id, hesap_kodu):
    """Orijinal: function gunluk_plan_al
    
    Personel icin gunluk plan (vardiya grubu) alir
    Oncelik: Personel Ozel Plan > Grup Ozel Plan > Haftalik Plan
    """
    gunler = ['Pazar', 'Pazartesi', 'Sali', 'Carsamba', 'Persembe', 'Cuma', 'Cumartesi']
    
    # 1. Personel Ozel Plani kontrol et
    sorgu1 = f"""
        SELECT vardiyaid FROM {schema}.personel_ozel_planlari
        WHERE vardiyaid > 0 AND personelid = %s AND tarih = %s
    """
    try:
        db_cursor.execute(sorgu1, (personel_id, tarih))
        row = db_cursor.fetchone()
        if row:
            return row[0]
    except:
        pass
    
    # 2. Grup Ozel Plani kontrol et
    sorgu2 = f"""
        SELECT vardiyaid FROM {schema}.grupozelplanlari
        WHERE vardiyaid > 0 AND grupid = %s AND tarih = %s
    """
    try:
        db_cursor.execute(sorgu2, (hesap_kodu, tarih))
        row = db_cursor.fetchone()
        if row:
            return row[0]
    except:
        pass
    
    # 3. Haftalik Plan
    try:
        tarih_obj = datetime.strptime(tarih, '%Y-%m-%d')
        haftanin_gunu = gunler[tarih_obj.weekday() + 1 if tarih_obj.weekday() < 6 else 0]
        
        sorgu3 = f"""
            SELECT {haftanin_gunu.lower()} FROM {schema}.planlar
            WHERE grupid = %s AND tarih <= %s
            ORDER BY tarih DESC LIMIT 1
        """
        db_cursor.execute(sorgu3, (hesap_kodu, tarih))
        row = db_cursor.fetchone()
        if row:
            return row[0]
    except:
        pass
    
    return -1


def gunluk_izin_al(db_cursor, schema, per_id, aktif_tarih, vardiya):
    """Orijinal: function gunluk_izin_al
    
    Personelin gunluk izin durumunu kontrol eder
    """
    gunluk_izin = {}
    
    sorgu = f"""
        SELECT p.aciklama, t.id, t.tatiladi, t.ucrettipi
        FROM {schema}.personelizin p
        LEFT JOIN {schema}.tatiller t ON t.id = p.tatilid
        WHERE p.personelid = %s AND p.tarih = %s AND (p.guniciizin = 0 OR p.guniciizin IS NULL)
        ORDER BY p.id DESC
    """
    try:
        db_cursor.execute(sorgu, (per_id, aktif_tarih))
        row = db_cursor.fetchone()
        
        if row:
            aciklama, tatil_id, tatil_adi, ucret_tipi = row
            gunluk_izin["tatil_id"] = tatil_id
            gunluk_izin["tatil_adi"] = tatil_adi
            gunluk_izin["aciklama"] = aciklama
            gunluk_izin["ucret_tipi"] = ucret_tipi
            gunluk_izin["plan_tatil"] = 0
        elif vardiya and vardiya.get("tatil_id", 0) > 0:
            # Vardiyadan tatil al
            sorgu2 = f"SELECT tatiladi, ucrettipi FROM {schema}.tatiller WHERE id = %s"
            db_cursor.execute(sorgu2, (vardiya["tatil_id"],))
            row2 = db_cursor.fetchone()
            if row2:
                gunluk_izin["tatil_id"] = vardiya["tatil_id"]
                gunluk_izin["tatil_adi"] = row2[0]
                gunluk_izin["ucret_tipi"] = row2[1]
                gunluk_izin["plan_tatil"] = 1
    except:
        pass
    
    return gunluk_izin


def saatlik_izinleri_al(db_cursor, schema, per_id, tarih, vardiya):
    """Orijinal: function saatlik_izinleri_al
    
    Personelin saatlik izinlerini alir (gun ici izinler)
    """
    izinler = []
    
    sorgu = f"""
        SELECT p.basla, p.bitis, p.aciklama, t.tatiladi
        FROM {schema}.personelizin p
        LEFT JOIN {schema}.tatiller t ON t.id = p.tatilid
        WHERE p.personelid = %s AND p.tarih = %s AND p.guniciizin = 1
        ORDER BY p.basla
    """
    try:
        db_cursor.execute(sorgu, (per_id, tarih))
        rows = db_cursor.fetchall()
        
        for row in rows:
            basla, bitis, aciklama, tatil_adi = row
            izinler.append({
                "basla": time_to_minute(str(basla) if basla else None),
                "bitis": time_to_minute(str(bitis) if bitis else None),
                "aciklama": aciklama,
                "tatil_adi": tatil_adi
            })
    except:
        pass
    
    return izinler


def gunluk_izinleri_al(db_cursor, schema, per_id, tarih):
    """Orijinal: function gunluk_izinleri_al
    
    Personelin gunluk izin bilgisini string olarak dondurur
    """
    sorgu = f"""
        SELECT t.tatiladi, p.aciklama
        FROM {schema}.personelizin p
        INNER JOIN {schema}.tatiller t ON p.tatilid = t.id
        WHERE p.personelid = %s AND p.tarih = %s AND (p.guniciizin != 1 OR p.guniciizin IS NULL)
    """
    try:
        db_cursor.execute(sorgu, (per_id, tarih))
        row = db_cursor.fetchone()
        
        if row:
            tatil_adi, aciklama = row
            if aciklama:
                return f"{tatil_adi} ({aciklama})"
            return tatil_adi
    except:
        pass
    
    return ""


def calisma_suresi_hesapla(giris, cikis):
    """Giris-cikis arasi sure (dakika)"""
    giris_dk = time_to_minute(giris)
    cikis_dk = time_to_minute(cikis)
    if giris_dk < 0 or cikis_dk < 0:
        return 0
    return max(0, cikis_dk - giris_dk)


def fazla_mesai_hesapla(db_cursor, schema, hareket, vardiya):
    """Fazla mesai hesaplama - Orijinal PHP mantigina gore
    
    1. Bordrolari al (bordrotipi=5 -> fazla mesai)
    2. Her bordro icin saat_hesapla() ile kesisim bul
    3. Min/max kontrolleri yap
    4. Toplam fazla mesaiyi don
    """
    toplam_fm = 0
    
    if not hareket or not vardiya:
        return toplam_fm
    
    giris_int = hareket.get("giris_int", -1)
    cikis_int = hareket.get("cikis_int", -1)
    
    if giris_int < 0 or cikis_int < 0:
        return toplam_fm
    
    # Bordrolari al
    bordrolar = bordrolari_al(db_cursor, schema, vardiya)
    
    for bordro in bordrolar:
        if bordro.get("bordro_tipi") != 5:  # Sadece fazla mesai
            continue
        
        bordro_basla = bordro.get("bordro_basla", 0)
        bordro_bitis = bordro.get("bordro_bitis", 0)
        min_dk = bordro.get("min", 0)
        max_dk = bordro.get("max", 0)
        ekle_dk = bordro.get("ekle", 0)
        
        # Kesisim hesapla
        kesisim = saat_hesapla(giris_int, cikis_int, bordro_basla, bordro_bitis)
        
        # Min kontrolu
        if min_dk > 0 and kesisim < min_dk:
            kesisim = 0
        
        # Max kontrolu
        if max_dk > 0 and kesisim > max_dk:
            kesisim = max_dk
        
        # Ekle
        if kesisim > 0 and ekle_dk > 0:
            kesisim += ekle_dk
        
        toplam_fm += kesisim
    
    return toplam_fm
