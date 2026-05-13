import cv2
import threading
from ultralytics import YOLO
from services.config import CAMERA_SOURCE, CAMERA_RECONNECT_SECONDS, TARGET_CLASSES, CAPTURES_DIR
from services.event_repository import EventRepository
import os
from datetime import datetime

class VideoMonitor:
    def __init__(self):
        self.camera_source = CAMERA_SOURCE
        self.model = YOLO("yolo11n.pt")
        self.repository = EventRepository()
        self.current_frame = None
        self.is_running = False
        self.is_connected = False
        self.thread = None
    
    def start(self):
        """Iniciar monitoramento de vídeo"""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Parar monitoramento"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.is_running:
            try:
                cap = cv2.VideoCapture(self.camera_source)
                if not cap.isOpened():
                    self.is_connected = False
                    self._sleep(CAMERA_RECONNECT_SECONDS)
                    continue
                
                self.is_connected = True
                
                while self.is_running and cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    
                    self.current_frame = frame
                    self._process_frame(frame)
                
                cap.release()
                self.is_connected = False
                self._sleep(CAMERA_RECONNECT_SECONDS)
            
            except Exception as e:
                print(f"Erro no monitor: {e}")
                self.is_connected = False
                self._sleep(CAMERA_RECONNECT_SECONDS)
    
    def _process_frame(self, frame):
        """Processar frame com YOLO"""
        try:
            results = self.model(frame, verbose=False)
            
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    label = result.names[cls_id]
                    confidence = float(box.conf[0])
                    
                    # Filtrar por classes alvo
                    if label in TARGET_CLASSES and confidence > 0.5:
                        self._save_detection(frame, label, confidence)
        
        except Exception as e:
            print(f"Erro ao processar frame: {e}")
    
    def _save_detection(self, frame, label: str, confidence: float):
        """Salvar evento de detecção"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"capture_{timestamp}_{label}_{int(confidence*100)}.jpg"
            filepath = os.path.join(CAPTURES_DIR, filename)
            
            cv2.imwrite(filepath, frame)
            
            relative_path = f"/static/captures/{filename}"
            self.repository.save_event(label, confidence, relative_path)
        
        except Exception as e:
            print(f"Erro ao salvar detecção: {e}")
    
    def get_frame(self):
        """Obter frame atual"""
        return self.current_frame
    
    def get_status(self) -> dict:
        """Obter status do monitor"""
        return {
            "online": self.is_connected,
            "connected": self.is_connected,
            "has_live_frame": self.current_frame is not None,
            "source_type": "stream" if "://" in self.camera_source else "local"
        }
    
    @staticmethod
    def _sleep(seconds: int):
        """Dormir por N segundos"""
        import time
        time.sleep(seconds)
