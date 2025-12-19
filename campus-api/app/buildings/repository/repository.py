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
