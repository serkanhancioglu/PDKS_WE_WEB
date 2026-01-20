"""
Hesap.inc - Temel Hesaplama Fonksiyonları
PHP birebir karşılıkları - Veritabanı bağımsız
"""
from datetime import datetime, timedelta
import math


def durum_hesapla(pay, payda, alt_pay, alt_payda, carpan, ekle):
    """Progress bar hesaplama"""
    return math.floor(carpan * ((pay + (alt_pay / alt_payda)) / payda)) + ekle


def tarih_gun_farki(tarihinden, tarihine):
    """Tarih farkı (gün)"""
    try:
        d1 = datetime.strptime(str(tarihinden), '%Y-%m-%d')
        d2 = datetime.strptime(str(tarihine), '%Y-%m-%d')
        return (d2 - d1).days
    except:
        return 0


def time_to_minute(saat):
    """Saat -> dakika dönüşümü (HH:MM -> int)"""
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


def dakika_to_saat(dakika):
    """Dakika -> saat dönüşümü (int -> HH:MM)"""
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
    """Bordro saat kesişim hesaplama - PHP birebir
    
    Giriş/çıkış ile bordro başlangıç/bitiş arasındaki kesişimi hesaplar
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
    """Birden fazla hareket varsa ilk giriş ve son çıkışı hesaplar"""
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
            
            if hareket_sonuc.get("cikis_int", -1) < 0:
                hareket_sonuc["en_buyuk_cikis"] = hareket_sonuc.get("giris_int", -1)
                hareket_sonuc["cikis_int"] = hareket_sonuc.get("giris_int", -1)
                hareket_sonuc["cikis_saat"] = hareket_sonuc.get("giris_saat", "")
        else:
            if hareket.get("giris_int", -1) > -1 and hareket.get("giris_int", 99999) < hareket_sonuc.get("giris_int", 99999):
                hareket_sonuc["giris_int"] = hareket["giris_int"]
                hareket_sonuc["giris_saat"] = hareket.get("giris_saat", "")
                hareket_sonuc["en_kucuk_giris"] = hareket["giris_int"]
            
            if hareket.get("cikis_int", -1) > -1 and hareket.get("cikis_int", -1) > hareket_sonuc.get("cikis_int", -1):
                hareket_sonuc["cikis_int"] = hareket["cikis_int"]
                hareket_sonuc["cikis_saat"] = hareket.get("cikis_saat", "")
                hareket_sonuc["en_buyuk_cikis"] = hareket["cikis_int"]
    
    return [hareket_sonuc]


def ara_eksikleri_hesapla(vardiya, molalar, hareketler):
    """Mola aralıklarındaki eksikleri hesaplar"""
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
            
            kesisim = saat_hesapla(giris, cikis, mola_basla, mola_bitis)
            
            if kesisim > 0 and mola_sure > 0:
                eksik = mola_sure - kesisim
                if eksik > 0:
                    ara_eksik_toplam += eksik
    
    return ara_eksik_toplam


def calisma_suresi_hesapla(giris, cikis):
    """Giriş-çıkış arası süre (dakika)"""
    giris_dk = time_to_minute(giris)
    cikis_dk = time_to_minute(cikis)
    if giris_dk < 0 or cikis_dk < 0:
        return 0
    return max(0, cikis_dk - giris_dk)


def vardiya_bul(vardiyalar, en_kucuk_giris):
    """Giriş saatine göre uygun vardiyayı bulur"""
    if not vardiyalar:
        return None
    
    for vardiya in vardiyalar:
        en_erken = vardiya.get("en_erken_giris", 0)
        en_gec = vardiya.get("en_gec_cikis", 0)
        
        if en_kucuk_giris >= en_erken and en_kucuk_giris <= en_gec:
            return vardiya
    
    return vardiyalar[0] if vardiyalar else None
