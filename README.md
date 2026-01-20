# PDKS WE WEB

**WE Teknoloji - Personel Devam Kontrol Sistemi**

Yeni müşteri kurulumları için hazır PDKS iskeleti. MikroPer ve Perkotek sistemleri için ortak API altyapısı.

## 📁 Dosya Yapısı

```
PDKS_WE_WEB/
├── app.py                  # Ana Flask uygulaması
├── hesap_fonksiyonlar.py   # Hesaplama fonksiyonları (PHP birebir)
├── routes_hareketler.py    # Hareket raporları
├── routes_mesai.py         # Mesai raporları
├── routes_vardiya.py       # Vardiya CRUD
├── schema.sql              # PostgreSQL tablo yapısı
├── requirements.txt        # Python bağımlılıkları
├── passenger_wsgi.py       # cPanel WSGI entry
├── setup.sh                # Kurulum scripti
├── .env.example            # Ortam değişkenleri örneği
└── public/
    └── index.html          # Dashboard
```

## 🚀 Hızlı Kurulum

### 1. Klasörü Kopyala
```bash
cp -r mikroper-template /path/to/musteri-pdks
cd /path/to/musteri-pdks
```

### 2. Ortam Değişkenlerini Ayarla
```bash
cp .env.example .env
# .env dosyasını düzenle
```

### 3. Veritabanını Oluştur
```bash
PGPASSWORD='password' psql -h HOST -U USER -d DATABASE -f schema.sql
```

### 4. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 5. Çalıştır
```bash
python app.py
# http://localhost:5000 adresinde çalışır
```

## 🔌 API Endpoint'leri

| Endpoint | Metod | Açıklama |
|----------|-------|----------|
| `/api/test` | GET | Bağlantı testi |
| `/api/stats` | GET | Dashboard istatistikleri |
| `/api/personel` | GET | Personel listesi |
| `/api/hareketler` | GET | Giriş-çıkış hareketleri |
| `/api/gec-gelenler` | GET | Geç gelen personel |
| `/api/erken-cikanlar` | GET | Erken çıkan personel |
| `/api/devamsizlik` | GET | Devamsızlık raporu |
| `/api/icerdekiler` | GET | Şu an içeridekiler |
| `/api/fazla-mesai` | GET | Fazla mesai raporu |
| `/api/gec-erken` | GET | Geç gelme/erken çıkma |
| `/api/vardiyalar` | GET | Vardiya listesi |
| `/api/vardiya/ekle` | POST | Yeni vardiya |
| `/api/vardiya/guncelle/{id}` | PUT | Vardiya güncelle |
| `/api/vardiya/sil/{id}` | DELETE | Vardiya sil |

### Parametreler
```
?start=2026-01-15&end=2026-01-20
```

## 📊 Veritabanı Tabloları

| Tablo | Açıklama |
|-------|----------|
| `personel` | Personel bilgileri |
| `hareketler` | Giriş-çıkış kayıtları |
| `vardiyalar` | Vardiya tanımları |
| `vardiyagruplari` | Vardiya grupları |
| `gunluk_hesap` | Günlük hesap tanımları |
| `gunluk_hesap_bordrolar` | Bordro saatleri |
| `bordroalanlari` | Bordro tipleri (1=Normal, 5=FM) |
| `gunluk_mola` | Mola tanımları |
| `planlar` | Haftalık planlar |
| `personelizin` | İzin kayıtları |
| `tatiller` | Tatil tanımları |

## 🔧 cPanel Deployment

### 1. Dosyaları Yükle
```bash
scp -r . user@server:/home/user/mikroper-api/
```

### 2. Python App Oluştur
- cPanel → Setup Python App
- Python 3.11
- App Root: mikroper-api
- Application URL: /pdks veya subdomain

### 3. Restart
```bash
cloudlinux-selector restart --json --interpreter python \
    --domain domain.com --app-root mikroper-api
```

## ⚠️ Önemli Notlar

1. **VARSAYIM YOK** - Tüm hesaplamalar orijinal PHP formüllerine göre
2. **Gece Vardiyası** - +1440 dk (24 saat) eklenerek hesaplanır
3. **Bordro Tipi 5** - Fazla mesai hesaplaması için kullanılır
4. **Schema Değiştirilebilir** - .env'de SCHEMA değişkeni ile

## 📝 Veri Import

Müşteriden alınan veriler için:

```sql
-- Personel import
COPY mikroper.personel(sicilno, adi, soyadi, departman) 
FROM '/path/to/personel.csv' DELIMITER ',' CSV HEADER;

-- Hareket import
COPY mikroper.hareketler(personelid, tarih, girissaat, cikissaat) 
FROM '/path/to/hareketler.csv' DELIMITER ',' CSV HEADER;
```

## 🏢 Mevcut Müşteriler

| Müşteri | URL | Schema | Durum |
|---------|-----|--------|-------|
| **24Yemek (Perkotek)** | https://pdks.24yemek.com.tr/ | perkotek | ✅ Aktif |
| **Besice (MikroPer)** | https://besice.weteknoloji.tr/pdks/ | mikroper | ✅ Aktif |

## 🔗 Repository

```bash
git clone https://github.com/AcunSoftware/PDKS_WE_WEB.git
```

---
*PDKS WE WEB - WE Teknoloji*
