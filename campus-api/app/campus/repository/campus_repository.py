# repository.py
from typing import Optional, List
from sqlmodel import Session, select
from models import Campus  # ← models.py'den import ediyoruz

class CampusRepository:
    def __init__(self, session: Session):  # ← conn yerine session
        self.session = session
    
    def create(self, campus_data: dict) -> Campus:
        try:
            campus = Campus(**campus_data)
            self.session.add(campus)
            self.session.commit()
            self.session.refresh(campus)
            return campus
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Veritabanı oluşturma hatası: {str(e)}")
    
    def find_all(self, city: Optional[str] = None) -> List[Campus]:
        try:
            statement = select(Campus).order_by(Campus.id)
            if city:
                statement = statement.where(Campus.city.ilike(f"%{city}%"))
            campuses = self.session.exec(statement).all()
            return list(campuses)
        except Exception as e:
            raise Exception(f"Veritabanı listeleme hatası: {str(e)}")
    
    def find_by_id(self, campus_id: int) -> Optional[Campus]:
        try:
            return self.session.get(Campus, campus_id)
        except Exception as e:
            raise Exception(f"Veritabanı getirme hatası: {str(e)}")
    
    def update(self, campus_id: int, campus_data: dict) -> Optional[Campus]:
        try:
            campus = self.session.get(Campus, campus_id)
            if not campus:
                return None
            for key, value in campus_data.items():
                setattr(campus, key, value)
            self.session.add(campus)
            self.session.commit()
            self.session.refresh(campus)
            return campus
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Veritabanı güncelleme hatası: {str(e)}")
    
    def delete(self, campus_id: int) -> Optional[Campus]:
        try:
            campus = self.session.get(Campus, campus_id)
            if not campus:
                return None
            self.session.delete(campus)
            self.session.commit()
            return campus
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Veritabanı silme hatası: {str(e)}")
