# ==================== CONFIGURATION ====================
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 5432)),
    'database': os.getenv('DATABASE_NAME', 'university_db'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', '12345'),
}

# ==================== DATABASE İŞLEMLERİ ====================
def initialize_db_pool():
    """Veritabanı bağlantı havuzunu başlatır."""
    global pool
    try:
        # minconn=1, maxconn=10: 1'den 10'a kadar bağlantı yönetimi yapar.
        pool = SimpleConnectionPool(minconn=1, maxconn=10, **DB_CONFIG)
        print('✅ Veritabanı Bağlantı Havuzu Başarıyla Başlatıldı.')
    except Exception as e:
        print(f'❌ Bağlantı Havuzu Başlatma Hatası: {e}')
        raise

def close_db_pool():
    """Veritabanı bağlantı havuzunu kapatır."""
    global pool
    if pool:
        pool.closeall()
        print('✅ Veritabanı Bağlantı Havuzu Kapatıldı.')

def get_db_connection():
    """Bağımlılık Enjeksiyonu için: Havuzdan bir bağlantı alır ve iş bitince havuza iade eder."""
    if not pool:
        raise Exception("Veritabanı bağlantı havuzu başlatılmamış.")
        
    conn = pool.getconn()
    try:
        # Bağlantıyı isteği işleyen fonksiyona yolla (yield)
        yield conn
    finally:
        # İstek tamamlanınca bağlantıyı havuza geri bırak
        pool.putconn(conn)

def create_tables():
    """Veritabanı tablolarını oluştur/güncelle."""
    # Tablo oluşturma işlemi için havuzdan geçici bir bağlantı al
    conn = next(get_db_connection())
    cur = conn.cursor()
    try:
        # 1. Kampüsler Tablosu
        cur.execute("""
        CREATE TABLE IF NOT EXISTS campuses (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            city VARCHAR(100) NOT NULL,
            address TEXT,
            established_year INTEGER,
            total_area DECIMAL(10, 2),
            student_capacity INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 2. Binalar Tablosu (campus_id, campuses tablosuna dış anahtar (Foreign Key) ile bağlanır)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS buildings (
            id SERIAL PRIMARY KEY,
            campus_id INTEGER NOT NULL REFERENCES campuses(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            type VARCHAR(50), -- Derslik, Laboratuvar, Kütüphane vb.
            floor_count INTEGER,
            construction_year INTEGER,
            gross_area DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        print('✅ Kampüs ve Bina tabloları başarıyla oluşturuldu/güncellendi.')
    except Exception as e:
        print(f'❌ Tablo oluşturma hatası: {e}')
    finally:
        cur.close()
