import cv2
import json
import time
import threading
import logging
from ultralytics import YOLO
from mediapipe_hand_face_kinematics import MediaPipeHandFaceKinematicsEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SpatialWorldModel")

class SpatialWorldModelEngine:
    def __init__(self):
        self.yolo_model = YOLO("yolov8n.pt")
        self.mp_engine = MediaPipeHandFaceKinematicsEngine()
        self.occupancy_grid = {} # Map of detected objects and their approx 3D spatial coordinates
        self.is_running = False
        
    def start_spatial_mapping(self, camera_index=0):
        self.is_running = True
        self.thread = threading.Thread(target=self._mapping_loop, args=(camera_index,), daemon=True)
        self.thread.start()
        
    def _mapping_loop(self, camera_index):
        cap = cv2.VideoCapture(camera_index)
        logger.info("Initializing Continuous Spatial World Model (Project Astra implementation)...")
        
        while self.is_running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 1. YOLOv8 Semantic Object Detection
            results = self.yolo_model(frame, stream=True, verbose=False)
            current_objects = {}
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    class_name = self.yolo_model.names[cls_id]
                    # Get center coordinates (approximating spatial location)
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    
                    # Store object with basic 2D->3D heuristic
                    current_objects[class_name] = {"x": cx, "y": cy, "last_seen": time.time()}
            
            # 2. MediaPipe Hand/Face Kinematics (Human-Object Interaction)
            # We would run mp_engine here to track if hand is near an object
            
            # 3. Update persistent grid
            for obj_name, coords in current_objects.items():
                if obj_name not in self.occupancy_grid:
                    logger.info(f"New object mapped into Spatial Grid: {obj_name} at ({coords['x']:.1f}, {coords['y']:.1f})")
                self.occupancy_grid[obj_name] = coords
                
            # Write out state to spatial_memory.json
            with open("spatial_memory.json", "w") as f:
                json.dump(self.occupancy_grid, f, indent=2)
                
            time.sleep(1) # Run at 1 Hz for background semantic mapping
            
        cap.release()

    def query_spatial_model(self, object_name):
        obj = self.occupancy_grid.get(object_name)
        if obj:
            return f"{object_name} is currently located at relative coordinates X:{obj['x']:.1f}, Y:{obj['y']:.1f}."
        else:
            return f"I don't see {object_name} in your physical environment."

if __name__ == "__main__":
    print("--- STARTING CONTINUOUS SPATIAL WORLD MODEL ---")
    engine = SpatialWorldModelEngine()
    engine.start_spatial_mapping()
    
    # Simulate queries
    time.sleep(5)
    print(engine.query_spatial_model("cell phone"))
    print(engine.query_spatial_model("person"))
    
    time.sleep(10)
    engine.is_running = False
