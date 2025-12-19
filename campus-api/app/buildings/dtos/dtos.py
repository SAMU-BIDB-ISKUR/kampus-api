# --- Bina Modelleri ---
class BuildingCreateDTO(BaseModel):
    campus_id: int = Field(..., description="Binanın ait olduğu kampüs ID'si")
    name: str = Field(..., min_length=1, max_length=255, description="Bina Adı")
    type: Optional[str] = Field(None, max_length=50, description="Bina Tipi (Derslik, Kütüphane vb.)")
    floor_count: Optional[int] = Field(None, ge=1, description="Kat Sayısı")
    construction_year: Optional[int] = Field(None, ge=1000, le=2100, description="İnşaat Yılı")
    gross_area: Optional[float] = Field(None, ge=0, description="Brüt Alan (m²)")

class BuildingUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    floor_count: Optional[int] = Field(None, ge=1)
    construction_year: Optional[int] = Field(None, ge=1000, le=2100)
    gross_area: Optional[float] = Field(None, ge=0)

class BuildingResponseDTO(BaseModel):
    id: int
    campus_id: int
    name: str
    type: Optional[str]
    floor_count: Optional[int]
    construction_year: Optional[int]
    gross_area: Optional[float]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
