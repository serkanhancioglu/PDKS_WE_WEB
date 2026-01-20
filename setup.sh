#!/bin/bash
# MikroPer PDKS - Kurulum Scripti
# Kullanım: ./setup.sh <musteri_adi> <schema_adi>

set -e

MUSTERI=${1:-"yeni_musteri"}
SCHEMA=${2:-"mikroper"}

echo "=========================================="
echo "MikroPer PDKS Kurulum"
echo "Müşteri: $MUSTERI"
echo "Schema: $SCHEMA"
echo "=========================================="

# 1. .env dosyasını oluştur
echo "[1/4] .env dosyası oluşturuluyor..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  → .env.example kopyalandı"
    echo "  ⚠️  .env dosyasını düzenleyip DB bilgilerini girin!"
else
    echo "  → .env zaten mevcut"
fi

# 2. Python bağımlılıklarını yükle
echo "[2/4] Python bağımlılıkları yükleniyor..."
pip install -r requirements.txt --quiet

# 3. Schema oluştur (PostgreSQL)
echo "[3/4] Veritabanı schema'sı oluşturuluyor..."
echo "  → schema.sql dosyasını çalıştırın:"
echo "  PGPASSWORD='YOUR_PASSWORD' psql -h HOST -U USER -d DATABASE -f schema.sql"

# 4. Public klasörünü oluştur
echo "[4/4] Public klasörü kontrol ediliyor..."
mkdir -p public

echo ""
echo "=========================================="
echo "✅ Kurulum tamamlandı!"
echo ""
echo "Sonraki adımlar:"
echo "1. .env dosyasını düzenleyin"
echo "2. PostgreSQL'de schema.sql çalıştırın"
echo "3. Personel ve vardiya verilerini import edin"
echo "4. python app.py ile test edin"
echo "=========================================="
