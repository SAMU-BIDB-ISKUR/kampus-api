# main.py - Tek Dosyada Kampüs ve Bina Yönetimi API
from fastapi import FastAPI, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select
import os



# Global Bağlantı Havuzu
pool: Optional[SimpleConnectionPool] = None



# ==================== PYDANTIC MODELS (DTO) ====================





class BuildingRepository:
    def __init__(self, conn):
        self.conn = conn
    
    def create(self, building_data: dict) -> dict:
        cur = self.conn.cursor()
        try:
            query = """
            INSERT INTO buildings (campus_id, name, type, floor_count, construction_year, gross_area)
            VALUES (%(campus_id)s, %(name)s, %(type)s, %(floor_count)s, %(construction_year)s, %(gross_area)s)
            RETURNING *;
            """
            cur.execute(query, building_data)
            building = cur.fetchone()
            self.conn.commit()
            return dict(building)
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Veritabanı bina oluşturma hatası: {str(e)}")
        finally:
            cur.close()
            
    def find_all(self, campus_id: Optional[int] = None) -> List[dict]:
        cur = self.conn.cursor()
        try:
            if campus_id is not None:
                cur.execute('SELECT * FROM buildings WHERE campus_id = %s ORDER BY id', (campus_id,))
            else:
                cur.execute('SELECT * FROM buildings ORDER BY id')
            
            buildings = cur.fetchall()
            return [dict(building) for building in buildings]
        except Exception as e:
            raise Exception(f"Veritabanı bina listeleme hatası: {str(e)}")
        finally:
            cur.close()

    def find_by_id(self, building_id: int) -> Optional[dict]:
        cur = self.conn.cursor()
        try:
            cur.execute('SELECT * FROM buildings WHERE id = %s', (building_id,))
            building = cur.fetchone()
            return dict(building) if building else None
        except Exception as e:
            raise Exception(f"Veritabanı bina getirme hatası: {str(e)}")
        finally:
            cur.close()

    def update(self, building_id: int, building_data: dict) -> Optional[dict]:
        cur = self.conn.cursor()
        try:
            set_clause = ", ".join([f"{key} = %({key})s" for key in building_data.keys()])
            query = f"""
            UPDATE buildings 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %(id)s
            RETURNING *;
            """
            building_data['id'] = building_id
            cur.execute(query, building_data)
            building = cur.fetchone()
            self.conn.commit()
            return dict(building) if building else None
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Veritabanı bina güncelleme hatası: {str(e)}")
        finally:
            cur.close()

    def delete(self, building_id: int) -> Optional[dict]:
        cur = self.conn.cursor()
        try:
            cur.execute('DELETE FROM buildings WHERE id = %s RETURNING *', (building_id,))
            building = cur.fetchone()
            self.conn.commit()
            return dict(building) if building else None
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Veritabanı bina silme hatası: {str(e)}")
        finally:
            cur.close()


# ==================== SERVICE KATMANI (İş Mantığı) ====================

class CampusService:
    def __init__(self, repository: CampusRepository):
        self.repository = repository
    
    def create_campus(self, campus_dto: CampusCreateDTO) -> CampusResponseDTO:
        try:
            campus_data = campus_dto.model_dump()
            campus = self.repository.create(campus_data)
            return CampusResponseDTO(**campus)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Kampüs oluşturulurken bir sunucu hatası oluştu.")
    
    def get_campuses(self, city: Optional[str]) -> List[CampusResponseDTO]:
        try:
            campuses = self.repository.find_all(city)
            return [CampusResponseDTO(**campus) for campus in campuses]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Kampüsler listelenirken bir sunucu hatası oluştu.")
    
    def get_campus_by_id(self, campus_id: int) -> CampusResponseDTO:
        try:
            campus = self.repository.find_by_id(campus_id)
            if not campus:
                raise HTTPException(status_code=404, detail=f"ID {campus_id} ile kampüs bulunamadı")
            return CampusResponseDTO(**campus)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Kampüs getirilirken bir sunucu hatası oluştu.")

    def update_campus(self, campus_id: int, campus_dto: CampusUpdateDTO) -> CampusResponseDTO:
        existing = self.repository.find_by_id(campus_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"ID {campus_id} ile kampüs bulunamadı")
        
        update_data = campus_dto.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="Güncellenecek veri gönderilmedi")
        
        try:
            campus = self.repository.update(campus_id, update_data)
            return CampusResponseDTO(**campus)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Kampüs güncellenirken bir sunucu hatası oluştu.")

    def delete_campus(self, campus_id: int) -> CampusResponseDTO:
        try:
            campus = self.repository.delete(campus_id)
            if not campus:
                raise HTTPException(status_code=404, detail=f"ID {campus_id} ile kampüs bulunamadı")
            return CampusResponseDTO(**campus)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Kampüs silinirken bir sunucu hatası oluştu.")


class BuildingService:
    def __init__(self, repository: BuildingRepository, campus_repository: CampusRepository):
        self.repository = repository
        self.campus_repository = campus_repository
    
    def create_building(self, building_dto: BuildingCreateDTO) -> BuildingResponseDTO:
        # Kampüs var mı kontrol et
        if not self.campus_repository.find_by_id(building_dto.campus_id):
            raise HTTPException(status_code=404, detail=f"Kampüs ID {building_dto.campus_id} bulunamadı. Bina oluşturulamaz.")

        try:
            building_data = building_dto.model_dump()
            building = self.repository.create(building_data)
            return BuildingResponseDTO(**building)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bina oluşturulurken bir sunucu hatası oluştu.")
    
    def get_buildings(self, campus_id: Optional[int]) -> List[BuildingResponseDTO]:
        # Eğer campus_id verilmişse, kampüsün varlığını kontrol et
        if campus_id is not None and not self.campus_repository.find_by_id(campus_id):
            raise HTTPException(status_code=404, detail=f"Kampüs ID {campus_id} bulunamadı.")
            
        try:
            buildings = self.repository.find_all(campus_id)
            return [BuildingResponseDTO(**building) for building in buildings]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Binalar listelenirken bir sunucu hatası oluştu.")
    
    def get_building_by_id(self, building_id: int) -> BuildingResponseDTO:
        try:
            building = self.repository.find_by_id(building_id)
            if not building:
                raise HTTPException(status_code=404, detail=f"ID {building_id} ile bina bulunamadı")
            return BuildingResponseDTO(**building)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bina getirilirken bir sunucu hatası oluştu.")

    def update_building(self, building_id: int, building_dto: BuildingUpdateDTO) -> BuildingResponseDTO:
        existing = self.repository.find_by_id(building_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"ID {building_id} ile bina bulunamadı")
        
        update_data = building_dto.model_dump(exclude_unset=True)
        
        # Campus ID'sinin güncellenmesini engelle
        if 'campus_id' in update_data:
             raise HTTPException(status_code=400, detail="Binanın ait olduğu kampüs (campus_id) güncellenemez.")

        if not update_data:
            raise HTTPException(status_code=400, detail="Güncellenecek veri gönderilmedi")
        
        try:
            building = self.repository.update(building_id, update_data)
            return BuildingResponseDTO(**building)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bina güncellenirken bir sunucu hatası oluştu.")
    
    def delete_building(self, building_id: int) -> BuildingResponseDTO:
        try:
            building = self.repository.delete(building_id)
            if not building:
                raise HTTPException(status_code=404, detail=f"ID {building_id} ile bina bulunamadı")
            return BuildingResponseDTO(**building)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bina silinirken bir sunucu hatası oluştu.")

# ==================== FASTAPI APP VE BAĞIMLILIKLAR ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Bağlantı havuzunu başlat ve tabloları oluştur
    initialize_db_pool()
    create_tables()
    yield
    # Shutdown: Bağlantı havuzunu kapat
    close_db_pool()

app = FastAPI(
    title="Üniversite Kampüs ve Bina API",
    description="Üniversite kampüslerini ve bunlara bağlı binaları yönetmek için REST API",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware (Frontend entegrasyonu için) ---
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    # Frontend'inizin çalıştığı adresi buraya ekleyin (örnek: React/Vue portu)
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


# === Bağımlılık Enjeksiyonu (Dependency Injection) Fonksiyonları ===

def get_campus_repository(conn=Depends(get_db_connection)) -> CampusRepository:
    return CampusRepository(conn=conn)

def get_campus_service(repository: CampusRepository = Depends(get_campus_repository)) -> CampusService:
    return CampusService(repository=repository)

def get_building_repository(conn=Depends(get_db_connection)) -> BuildingRepository:
    return BuildingRepository(conn=conn)

def get_building_service(
    repository: BuildingRepository = Depends(get_building_repository),
    campus_repository: CampusRepository = Depends(get_campus_repository) # Kampüs varlığını kontrol etmek için
) -> BuildingService:
    return BuildingService(repository=repository, campus_repository=campus_repository)


# ==================== ENDPOINTS (Kampüs Yönetimi) ====================

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Üniversite Kampüs ve Bina API'ye hoş geldiniz",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.post("/api/campuses", response_model=CampusResponseDTO, status_code=status.HTTP_201_CREATED, tags=["Campuses"])
async def create_campus(
    campus: CampusCreateDTO, 
    service: CampusService = Depends(get_campus_service)
):
    """Yeni kampüs oluştur"""
    return service.create_campus(campus)

@app.get("/api/campuses", response_model=List[CampusResponseDTO], tags=["Campuses"])
async def get_campuses(
    city: Optional[str] = Query(None, description="Şehir adına göre filtrele"), 
    service: CampusService = Depends(get_campus_service)
):
    """Tüm kampüsleri listele veya `city` sorgu parametresi ile filtrele."""
    return service.get_campuses(city)

@app.get("/api/campuses/{campus_id}", response_model=CampusResponseDTO, tags=["Campuses"])
async def get_campus(
    campus_id: int, 
    service: CampusService = Depends(get_campus_service)
):
    """ID'ye göre kampüs getir"""
    return service.get_campus_by_id(campus_id)

@app.put("/api/campuses/{campus_id}", response_model=CampusResponseDTO, tags=["Campuses"])
async def update_campus(
    campus_id: int, 
    campus: CampusUpdateDTO, 
    service: CampusService = Depends(get_campus_service)
):
    """Kampüs güncelle"""
    return service.update_campus(campus_id, campus)

@app.delete("/api/campuses/{campus_id}", response_model=CampusResponseDTO, tags=["Campuses"])
async def delete_campus(
    campus_id: int, 
    service: CampusService = Depends(get_campus_service)
):
    """Kampüs sil (Bağlı binalar da silinir - ON DELETE CASCADE)"""
    return service.delete_campus(campus_id)

# ==================== ENDPOINTS (Bina Yönetimi) ====================

@app.post("/api/buildings", response_model=BuildingResponseDTO, status_code=status.HTTP_201_CREATED, tags=["Buildings"])
async def create_building(
    building: BuildingCreateDTO, 
    service: BuildingService = Depends(get_building_service)
):
    """Yeni bina oluştur (bir kampüse bağlı olmalıdır)"""
    return service.create_building(building)

@app.get("/api/buildings", response_model=List[BuildingResponseDTO], tags=["Buildings"])
async def get_buildings(
    campus_id: Optional[int] = Query(None, description="Kampüs ID'sine göre filtrele"), 
    service: BuildingService = Depends(get_building_service)
):
    """Tüm binaları listele veya Kampüs ID'sine göre filtrele"""
    return service.get_buildings(campus_id)

@app.get("/api/buildings/{building_id}", response_model=BuildingResponseDTO, tags=["Buildings"])
async def get_building(
    building_id: int, 
    service: BuildingService = Depends(get_building_service)
):
    """ID'ye göre bina getir"""
    return service.get_building_by_id(building_id)

@app.put("/api/buildings/{building_id}", response_model=BuildingResponseDTO, tags=["Buildings"])
async def update_building(
    building_id: int, 
    building: BuildingUpdateDTO, 
    service: BuildingService = Depends(get_building_service)
):
    """Bina güncelle"""
    return service.update_building(building_id, building)

@app.delete("/api/buildings/{building_id}", response_model=BuildingResponseDTO, tags=["Buildings"])
async def delete_building(
    building_id: int, 
    service: BuildingService = Depends(get_building_service)
):
    """Bina sil"""
    return service.delete_building(building_id)


# ==================== RUN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
