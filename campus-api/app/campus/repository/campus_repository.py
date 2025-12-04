# ==================== REPOSITORY KATMANI (Veri Erişimi) ====================

class CampusRepository:
    def __init__(self, conn):
        self.conn = conn
    
    def create(self, campus_data: dict) -> dict:
        cur = self.conn.cursor()
        try:
            query = """
            INSERT INTO campuses (name, city, address, established_year, total_area, student_capacity)
            VALUES (%(name)s, %(city)s, %(address)s, %(established_year)s, %(total_area)s, %(student_capacity)s)
            RETURNING *;
            """
            cur.execute(query, campus_data)
            campus = cur.fetchone()
            self.conn.commit()
            return dict(campus)
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Veritabanı oluşturma hatası: {str(e)}")
        finally:
            cur.close()
    
    def find_all(self, city: Optional[str] = None) -> List[dict]:
        cur = self.conn.cursor()
        try:
            if city:
                query = 'SELECT * FROM campuses WHERE city ILIKE %s ORDER BY id'
                cur.execute(query, (f'%{city}%',))
            else:
                cur.execute('SELECT * FROM campuses ORDER BY id')
            
            campuses = cur.fetchall()
            return [dict(campus) for campus in campuses]
        except Exception as e:
            raise Exception(f"Veritabanı listeleme hatası: {str(e)}")
        finally:
            cur.close()
    
    def find_by_id(self, campus_id: int) -> Optional[dict]:
        cur = self.conn.cursor()
        try:
            cur.execute('SELECT * FROM campuses WHERE id = %s', (campus_id,))
            campus = cur.fetchone()
            return dict(campus) if campus else None
        except Exception as e:
            raise Exception(f"Veritabanı getirme hatası: {str(e)}")
        finally:
            cur.close()
    
    def update(self, campus_id: int, campus_data: dict) -> Optional[dict]:
        cur = self.conn.cursor()
        try:
            set_clause = ", ".join([f"{key} = %({key})s" for key in campus_data.keys()])
            query = f"""
            UPDATE campuses 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %(id)s
            RETURNING *;
            """
            campus_data['id'] = campus_id
            cur.execute(query, campus_data)
            campus = cur.fetchone()
            self.conn.commit()
            return dict(campus) if campus else None
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Veritabanı güncelleme hatası: {str(e)}")
        finally:
            cur.close()
    
    def delete(self, campus_id: int) -> Optional[dict]:
        cur = self.conn.cursor()
        try:
            cur.execute('DELETE FROM campuses WHERE id = %s RETURNING *', (campus_id,))
            campus = cur.fetchone()
            self.conn.commit()
            return dict(campus) if campus else None
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Veritabanı silme hatası: {str(e)}")
        finally:
            cur.close()
