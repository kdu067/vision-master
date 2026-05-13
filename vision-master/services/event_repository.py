import sqlite3
from typing import List, Dict
from datetime import datetime
from services.config import DATABASE_PATH

class EventRepository:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_db()
    
    def init_db(self):
        """Criar tabela de eventos se não existir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_time TEXT NOT NULL,
                label TEXT NOT NULL,
                confidence REAL NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def save_event(self, label: str, confidence: float, image_path: str = None) -> int:
        """Salvar evento de detecção"""
        event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO events (event_time, label, confidence, image_path)
            VALUES (?, ?, ?, ?)
        """, (event_time, label, confidence, image_path))
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return event_id
    
    def get_recent_events(self, limit: int = 12) -> List[Dict]:
        """Obter eventos recentes"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, event_time, label, confidence, image_path
            FROM events
            ORDER BY event_time DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def count_events(self) -> int:
        """Contar total de eventos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        conn.close()
        return count
