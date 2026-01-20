# PDKS WE WEB - MikroPer Template

**WE Teknoloji - Personel Devam Kontrol Sistemi**

Yeni MikroPer müşteri kurulumları için hazır PDKS template'i. Orijinal PHP `Hesap.inc` fonksiyonları birebir Python'a çevrilmiştir.

## Hızlı Kurulum

```bash
# 1. Klonla
git clone https://github.com/serkanhancioglu/PDKS_WE_WEB.git
cd PDKS_WE_WEB

# 2. .env oluştur
cp .env.example .env
# .env dosyasını düzenle

# 3. Bağımlılıkları kur
pip install -r requirements.txt

# 4. Veritabanı şemasını oluştur
psql -h HOST -U USER -d DATABASE -f schema.sql

# 5. Çalıştır
python app.py
```

## Proje Yapısı

| Özellik | Değer |
|---------|-------|
| **Framework** | Flask + PostgreSQL |
| **Hesap.inc** | ✅ Birebir çevrildi (761 satır) |
| **Tablolar** | 95 (MySQL yapısı korundu) |

## Modüler Yapı (200-600 satır kuralı)

```
PDKS_WE_WEB/
├── app.py                  (106 satır) - Ana Flask uygulaması
├── hesap_inc_complete.py   (761 satır) - Hesap.inc birebir çeviri
├── hesap_sorgular.py       (414 satır) - Veritabanı sorguları
├── routes_hareketler.py    (155 satır) - Hareket endpoint'leri
├── routes_mesai.py         (166 satır) - Mesai endpoint'leri
├── routes_vardiya.py       (92 satır)  - Vardiya CRUD
├── schema.sql              (168 satır) - PostgreSQL şema
├── .env.example                        - Ortam değişkenleri
└── public/index.html                   - Dashboard
```

## PHP Hesap.inc → Python Eşleştirmesi

### hesap_fonksiyonlar.py (Veritabanı Bağımsız)

| PHP Fonksiyonu | Python Karşılığı | Açıklama |
|----------------|------------------|----------|
| `saat_hesapla()` | ✅ Birebir | Bordro kesişim hesaplama |
| `time_to_minute()` | ✅ Birebir | Saat → dakika dönüşümü |
| `dakika_to_saat()` | ✅ Birebir | Dakika → saat dönüşümü |
| `ilkgiris_soncikis_hesapla()` | ✅ Birebir | İlk giriş/son çıkış |
| `ara_eksikleri_hesapla()` | ✅ Birebir | Mola eksik hesaplama |
| `vardiya_bul()` | ✅ Birebir | Vardiya eşleştirme |
| `durum_hesapla()` | ✅ Birebir | Progress bar |
| `tarih_gun_farki()` | ✅ Birebir | Tarih farkı |

### hesap_sorgular.py (Veritabanı Bağımlı)

| PHP Fonksiyonu | Python Karşılığı | Açıklama |
|----------------|------------------|----------|
| `hareketleri_al()` | ✅ Birebir | Personel hareketleri |
| `bordrolari_al()` | ✅ Birebir | Bordro tanımları |
| `molalari_al()` | ✅ Birebir | Mola tanımları |
| `vardiyalari_al()` | ✅ Birebir | Vardiya sorgusu |
| `gunluk_plan_al()` | ✅ Birebir | Günlük plan |
| `gunluk_izin_al()` | ✅ Birebir | İzin kontrolü |
| `saatlik_izinleri_al()` | ✅ Birebir | Saatlik izin |
| `fazla_mesai_hesapla()` | ✅ Birebir | Fazla mesai |

## API Endpoint'leri

### Raporlar

| Endpoint | PHP Rapor | Açıklama |
|----------|-----------|----------|
| `GET /api/hareketler` | 01-Genel Bazda Hareket.php | Tüm giriş-çıkış |
| `GET /api/fazla-mesai` | 04-Fazla Mesai.php | Fazla mesai hesaplama |
| `GET /api/gec-gelenler` | 05-Gec Gelenler.php | Geç gelen personel |
| `GET /api/erken-cikanlar` | 06-Erken Cikanlar.php | Erken çıkan personel |
| `GET /api/devamsizlik` | 03-Devamsizlik.php | Devamsızlık raporu |
| `GET /api/icerdekiler` | 14-Iceridekiler.php | Şu an içeridekiler |
| `GET /api/personel` | - | Personel listesi |

### Vardiya Yönetimi

| Endpoint | Metod | Açıklama |
|----------|-------|----------|
| `/api/vardiyalar` | GET | Vardiya listesi |
| `/api/vardiya/ekle` | POST | Yeni vardiya |
| `/api/vardiya/guncelle/{id}` | PUT | Vardiya güncelle |
| `/api/vardiya/sil/{id}` | DELETE | Vardiya sil |

### Parametreler

```
?start=2026-01-15&end=2026-01-20
```

## Kritik Tablolar

| Tablo | Açıklama | Kayıt |
|-------|----------|-------|
| `hareketler` | Giriş-çıkış verileri | 65,453 |
| `personel` | Personel bilgileri | 130 |
| `vardiyalar` | Vardiya tanımları | 26 |
| `vardiyagruplari` | Vardiya grupları | 18 |
| `gunluk_hesap` | Günlük hesap tanımları | 11 |
| `gunluk_hesap_bordrolar` | Bordro saatleri | 15 |
| `bordroalanlari` | Bordro tipleri (5=Fazla Mesai) | 26 |

## Hesaplama Mantığı

### Fazla Mesai Hesaplama

```python
# 1. Personelin vardiya grubunu bul
hesapgrupkodu = personel.hesapgrupkodu

# 2. Vardiya tanımını al
vardiyalar = vardiyalari_al(hesapgrupkodu)

# 3. Bordroları al (bordrotipi=5 -> Fazla Mesai)
bordrolar = bordrolari_al(vardiya)

# 4. Her bordro için kesişim hesapla
for bordro in bordrolar:
    if bordro.bordro_tipi == 5:
        kesisim = saat_hesapla(giris, cikis, bordro_basla, bordro_bitis)
        toplam_fm += kesisim
```

### saat_hesapla() Formülü

```python
def saat_hesapla(giris, cikis, basla, bitis):
    """Bordro kesişim hesaplama - PHP birebir"""
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
```

## Yönetim Komutları

```bash
# SSH Bağlantı
ssh linux01

# API Restart
cloudlinux-selector restart --json --interpreter python \
    --domain besice.weteknoloji.tr --app-root mikroper-api

# Veritabanı
PGPASSWORD='dxCQK{xY7W9j' psql -h 127.0.0.1 -U apibscusr_selamnaber \
    -d apibscusr_test123 -c "SELECT COUNT(*) FROM mikroper.hareketler;"
```

## Test

```bash
# Hareketler
curl "https://besice.weteknoloji.tr/pdks/api/hareketler?start=2026-01-15&end=2026-01-20"

# Fazla Mesai
curl "https://besice.weteknoloji.tr/pdks/api/fazla-mesai?start=2026-01-15&end=2026-01-19"

# Bağlantı Testi
curl "https://besice.weteknoloji.tr/pdks/api/test"
```

## Notlar

- **VARSAYIM YOK** - Tüm hesaplamalar orijinal PHP formüllerine göre
- **Modüler Yapı** - Her dosya 200-600 satır
- **MySQL → PostgreSQL** - 95 tablo birebir aktarıldı
- **Gece Vardiyası** - +1440 dk (24 saat) eklenerek hesaplanır

---
*Son Güncelleme: 20 Ocak 2026*
