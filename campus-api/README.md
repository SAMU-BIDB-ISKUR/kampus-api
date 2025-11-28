# Üniversite Kampüs API

## Kurulum

1. Sanal ortam oluştur:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

2. Paketleri yükle:
```bash
pip install -r requirements.txt
```

3. .env dosyasını düzenle ve PostgreSQL şifrenizi girin

4. Uygulamayı çalıştır:
```bash
uvicorn main:app --reload
```

5. API dokümantasyonu:
http://localhost:8000/docs
