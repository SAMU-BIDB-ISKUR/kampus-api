# ==================== CONFIGURATION ====================
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 5432)),
    'database': os.getenv('DATABASE_NAME', 'university_db'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', '12345'),
}
