-- MikroPer PDKS - PostgreSQL Schema Template
-- Yeni müşteri kurulumu için boş tablo yapısı
-- Kullanım: psql -h HOST -U USER -d DATABASE -f schema.sql

-- Schema oluştur (müşteri adına göre değiştir)
CREATE SCHEMA IF NOT EXISTS mikroper;

-- =====================================================
-- ANA TABLOLAR
-- =====================================================

-- Personel bilgileri
CREATE TABLE IF NOT EXISTS mikroper.personel (
    id SERIAL PRIMARY KEY,
    sicilno VARCHAR(50),
    adi VARCHAR(100),
    soyadi VARCHAR(100),
    hesapgrupkodu INTEGER DEFAULT 1,
    departman VARCHAR(100),
    bolum VARCHAR(100),
    gorev VARCHAR(100),
    isegiristarihi DATE,
    isecikistarihi DATE,
    aktif INTEGER DEFAULT 1,
    kartno VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Giriş-çıkış hareketleri
CREATE TABLE IF NOT EXISTS mikroper.hareketler (
    id SERIAL PRIMARY KEY,
    personelid INTEGER REFERENCES mikroper.personel(id),
    tarih DATE NOT NULL,
    girissaat TIME,
    cikissaat TIME,
    tarihcikis DATE,
    giriscihazid INTEGER DEFAULT 0,
    cikiscihazid INTEGER DEFAULT 0,
    girismudahale INTEGER DEFAULT 0,
    cikismudahale INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- VARDİYA YÖNETİMİ
-- =====================================================

-- Vardiya grupları
CREATE TABLE IF NOT EXISTS mikroper.vardiyagruplari (
    id SERIAL PRIMARY KEY,
    aciklama VARCHAR(200),
    aktif INTEGER DEFAULT 1
);

-- Günlük hesap tanımları
CREATE TABLE IF NOT EXISTS mikroper.gunluk_hesap (
    id SERIAL PRIMARY KEY,
    aciklama VARCHAR(200),
    girissaati TIME,
    cikissaati TIME,
    gecgelme TIME,
    erkencikma TIME,
    enerkengiris TIME,
    engeccikis TIME,
    hesaptipi INTEGER DEFAULT 0,
    vardiyagun INTEGER DEFAULT 0,
    gecerkenhesaplama INTEGER DEFAULT 0
);

-- Vardiya tanımları
CREATE TABLE IF NOT EXISTS mikroper.vardiyalar (
    id SERIAL PRIMARY KEY,
    vardiyaid INTEGER REFERENCES mikroper.vardiyagruplari(id),
    basla TIME,
    bitis TIME,
    gunlukhesapid INTEGER REFERENCES mikroper.gunluk_hesap(id),
    tatildurumu INTEGER DEFAULT 0
);

-- =====================================================
-- BORDRO VE MESAİ
-- =====================================================

-- Bordro alanları (bordrotipi: 1=Normal, 5=Fazla Mesai)
CREATE TABLE IF NOT EXISTS mikroper.bordroalanlari (
    id SERIAL PRIMARY KEY,
    aciklama VARCHAR(200),
    bordrotipi INTEGER DEFAULT 1,
    aktif INTEGER DEFAULT 1
);

-- Günlük hesap bordroları
CREATE TABLE IF NOT EXISTS mikroper.gunluk_hesap_bordrolar (
    id SERIAL PRIMARY KEY,
    gunlukhesapid INTEGER REFERENCES mikroper.gunluk_hesap(id),
    bordroid INTEGER REFERENCES mikroper.bordroalanlari(id),
    basla TIME,
    bitis TIME,
    min TIME,
    max TIME,
    ekle TIME
);

-- Mola tanımları
CREATE TABLE IF NOT EXISTS mikroper.gunluk_mola (
    id SERIAL PRIMARY KEY,
    gunlukhesapid INTEGER REFERENCES mikroper.gunluk_hesap(id),
    basla TIME,
    bitis TIME,
    sure TIME
);

-- =====================================================
-- PLAN YÖNETİMİ
-- =====================================================

-- Haftalık planlar
CREATE TABLE IF NOT EXISTS mikroper.planlar (
    id SERIAL PRIMARY KEY,
    grupid INTEGER REFERENCES mikroper.vardiyagruplari(id),
    tarih DATE,
    pazartesi INTEGER DEFAULT 0,
    sali INTEGER DEFAULT 0,
    carsamba INTEGER DEFAULT 0,
    persembe INTEGER DEFAULT 0,
    cuma INTEGER DEFAULT 0,
    cumartesi INTEGER DEFAULT 0,
    pazar INTEGER DEFAULT 0
);

-- Grup özel planları
CREATE TABLE IF NOT EXISTS mikroper.grupozelplanlari (
    id SERIAL PRIMARY KEY,
    grupid INTEGER,
    tarih DATE,
    vardiyaid INTEGER
);

-- Personel özel planları
CREATE TABLE IF NOT EXISTS mikroper.personel_ozel_planlari (
    id SERIAL PRIMARY KEY,
    personelid INTEGER REFERENCES mikroper.personel(id),
    tarih DATE,
    vardiyaid INTEGER
);

-- =====================================================
-- İZİN VE TATİL
-- =====================================================

-- Tatil tanımları
CREATE TABLE IF NOT EXISTS mikroper.tatiller (
    id SERIAL PRIMARY KEY,
    tatiladi VARCHAR(200),
    ucrettipi INTEGER DEFAULT 0,
    aktif INTEGER DEFAULT 1
);

-- Personel izinleri
CREATE TABLE IF NOT EXISTS mikroper.personelizin (
    id SERIAL PRIMARY KEY,
    personelid INTEGER REFERENCES mikroper.personel(id),
    tarih DATE,
    tatilid INTEGER REFERENCES mikroper.tatiller(id),
    basla TIME,
    bitis TIME,
    aciklama VARCHAR(500),
    guniciizin INTEGER DEFAULT 0
);

-- =====================================================
-- INDEXLER (Performans için)
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_hareketler_tarih ON mikroper.hareketler(tarih);
CREATE INDEX IF NOT EXISTS idx_hareketler_personel ON mikroper.hareketler(personelid);
CREATE INDEX IF NOT EXISTS idx_hareketler_tarih_personel ON mikroper.hareketler(tarih, personelid);
CREATE INDEX IF NOT EXISTS idx_personel_hesapgrup ON mikroper.personel(hesapgrupkodu);
CREATE INDEX IF NOT EXISTS idx_personelizin_tarih ON mikroper.personelizin(tarih);

-- =====================================================
-- ÖRNEK VERİLER (İsteğe bağlı)
-- =====================================================

-- Varsayılan bordro tipleri
INSERT INTO mikroper.bordroalanlari (aciklama, bordrotipi) VALUES 
    ('Normal Mesai', 1),
    ('Fazla Mesai', 5)
ON CONFLICT DO NOTHING;

-- Varsayılan tatil türleri
INSERT INTO mikroper.tatiller (tatiladi, ucrettipi) VALUES 
    ('Yıllık İzin', 1),
    ('Mazeret İzni', 0),
    ('Hastalık İzni', 0),
    ('Resmi Tatil', 1)
ON CONFLICT DO NOTHING;

-- Varsayılan vardiya grubu
INSERT INTO mikroper.vardiyagruplari (aciklama) VALUES 
    ('Genel Vardiya')
ON CONFLICT DO NOTHING;

-- =====================================================
-- TAMAMLANDI
-- =====================================================
-- Schema kurulumu tamamlandı
-- Sonraki adım: Personel ve vardiya verilerini import edin
