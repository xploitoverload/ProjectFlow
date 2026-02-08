# app/ml/face_recognition.py
"""
Advanced Face Recognition System
Detects, recognizes, and analyzes faces with liveness detection and clustering.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
import uuid
import numpy as np


class FaceDetectionModel(Enum):
    """Face detection models available."""
    MEDIAPIPE = "mediapipe"  # Fast, lightweight
    DEEPFACE = "deepface"    # Accurate, comprehensive
    DLIB = "dlib"            # Traditional, reliable


class LivenessStatus(Enum):
    """Liveness detection status."""
    ALIVE = "alive"
    FAKE = "fake"
    UNCERTAIN = "uncertain"


@dataclass
class FaceEmbedding:
    """Face embedding vector representation."""
    embedding_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    face_id: str = ""
    vector: List[float] = field(default_factory=list)
    model: str = "deepface"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'embedding_id': self.embedding_id,
            'face_id': self.face_id,
            'vector_size': len(self.vector),
            'model': self.model,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class Face:
    """Detected face with attributes and metadata."""
    face_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    image_path: str = ""
    
    # Face geometry
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    
    # Face attributes
    age: Optional[int] = None
    gender: Optional[str] = None  # male, female, other
    emotion: Optional[str] = None  # happy, sad, angry, etc
    confidence: float = 0.0
    
    # Liveness
    liveness: LivenessStatus = LivenessStatus.UNCERTAIN
    liveness_score: float = 0.0
    
    # Embeddings
    embeddings: List[FaceEmbedding] = field(default_factory=list)
    cluster_id: Optional[str] = None
    
    # Metadata
    detected_at: datetime = field(default_factory=datetime.utcnow)
    verified: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'face_id': self.face_id,
            'user_id': self.user_id,
            'bbox': {'x': self.x, 'y': self.y, 'width': self.width, 'height': self.height},
            'attributes': {
                'age': self.age,
                'gender': self.gender,
                'emotion': self.emotion,
                'confidence': round(self.confidence, 3)
            },
            'liveness': {
                'status': self.liveness.value,
                'score': round(self.liveness_score, 3)
            },
            'cluster_id': self.cluster_id,
            'verified': self.verified,
            'detected_at': self.detected_at.isoformat()
        }


@dataclass
class FaceCluster:
    """Cluster of similar faces (likely same person)."""
    cluster_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    faces: Set[str] = field(default_factory=set)  # face_ids
    centroid: List[float] = field(default_factory=list)
    confidence: float = 0.0
    label: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'cluster_id': self.cluster_id,
            'face_count': len(self.faces),
            'confidence': round(self.confidence, 3),
            'label': self.label
        }


class FaceRecognitionEngine:
    """
    Advanced face recognition with detection, recognition, liveness, and clustering.
    """
    
    def __init__(self, detection_model: FaceDetectionModel = FaceDetectionModel.MEDIAPIPE):
        """Initialize face recognition engine."""
        self.detection_model = detection_model
        self.faces: Dict[str, Face] = {}
        self.clusters: Dict[str, FaceCluster] = {}
        self.user_faces: Dict[str, Set[str]] = {}  # user_id -> face_ids
        self.recognized_count = 0
        self.liveness_verified_count = 0
        
    def detect_faces(self, image_path: str) -> List[Face]:
        """Detect faces in image."""
        # Simulate face detection
        detected = []
        
        # In production, use MediaPipe, DeepFace, or DLIB
        face = Face(
            image_path=image_path,
            x=100,
            y=50,
            width=200,
            height=250,
            age=28,
            gender='female',
            emotion='happy',
            confidence=0.95
        )
        
        self.faces[face.face_id] = face
        detected.append(face)
        
        return detected
    
    def recognize_face(self, face_id: str, user_id: str = None) -> Dict:
        """Recognize/identify face or assign to user."""
        if face_id not in self.faces:
            return {'status': 'error', 'message': 'Face not found'}
        
        face = self.faces[face_id]
        
        if user_id:
            face.user_id = user_id
            face.verified = True
            
            if user_id not in self.user_faces:
                self.user_faces[user_id] = set()
            self.user_faces[user_id].add(face_id)
            
            self.recognized_count += 1
        
        return {
            'status': 'success',
            'face_id': face_id,
            'user_id': user_id,
            'confidence': face.confidence
        }
    
    def detect_liveness(self, face_id: str) -> Dict:
        """Detect liveness (real vs fake face)."""
        if face_id not in self.faces:
            return {'status': 'error', 'message': 'Face not found'}
        
        face = self.faces[face_id]
        
        # Simulate liveness detection
        liveness_score = 0.92  # In production: analyze micro-expressions, texture, etc.
        
        if liveness_score > 0.8:
            face.liveness = LivenessStatus.ALIVE
        elif liveness_score < 0.3:
            face.liveness = LivenessStatus.FAKE
        else:
            face.liveness = LivenessStatus.UNCERTAIN
        
        face.liveness_score = liveness_score
        
        if face.liveness == LivenessStatus.ALIVE:
            self.liveness_verified_count += 1
        
        return {
            'status': 'success',
            'face_id': face_id,
            'liveness': face.liveness.value,
            'score': face.liveness_score
        }
    
    def generate_embedding(self, face_id: str, model: str = 'deepface') -> Dict:
        """Generate face embedding vector."""
        if face_id not in self.faces:
            return {'status': 'error', 'message': 'Face not found'}
        
        face = self.faces[face_id]
        
        # Simulate embedding generation (in production: use DeepFace, FaceNet, etc.)
        embedding_vector = np.random.rand(128).tolist()  # 128-dim vector
        
        embedding = FaceEmbedding(
            face_id=face_id,
            vector=embedding_vector,
            model=model
        )
        
        face.embeddings.append(embedding)
        
        return {
            'status': 'success',
            'embedding_id': embedding.embedding_id,
            'vector_size': len(embedding_vector),
            'model': model
        }
    
    def compare_faces(self, face_id_1: str, face_id_2: str, threshold: float = 0.6) -> Dict:
        """Compare two faces and get similarity score."""
        if face_id_1 not in self.faces or face_id_2 not in self.faces:
            return {'status': 'error', 'message': 'One or both faces not found'}
        
        face1 = self.faces[face_id_1]
        face2 = self.faces[face_id_2]
        
        if not face1.embeddings or not face2.embeddings:
            return {'status': 'error', 'message': 'Missing embeddings for comparison'}
        
        # Simulate cosine similarity
        v1 = np.array(face1.embeddings[0].vector)
        v2 = np.array(face2.embeddings[0].vector)
        similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        
        # Normalize to 0-1
        similarity = (similarity + 1) / 2
        
        return {
            'status': 'success',
            'face_id_1': face_id_1,
            'face_id_2': face_id_2,
            'similarity': round(similarity, 3),
            'match': similarity > threshold
        }
    
    def cluster_faces(self, distance_threshold: float = 0.6) -> Dict:
        """Cluster faces into groups (likely same person)."""
        clusters = {}
        unassigned = set(self.faces.keys())
        
        while unassigned:
            face_id = unassigned.pop()
            face = self.faces[face_id]
            
            cluster_id = str(uuid.uuid4())[:8]
            cluster = FaceCluster(cluster_id=cluster_id)
            cluster.faces.add(face_id)
            face.cluster_id = cluster_id
            
            # Find similar faces
            for other_id in list(unassigned):
                result = self.compare_faces(face_id, other_id, distance_threshold)
                if result.get('match'):
                    cluster.faces.add(other_id)
                    self.faces[other_id].cluster_id = cluster_id
                    unassigned.remove(other_id)
            
            cluster.confidence = sum(self.faces[f].confidence for f in cluster.faces) / len(cluster.faces)
            clusters[cluster_id] = cluster
            self.clusters[cluster_id] = cluster
        
        return {
            'status': 'success',
            'clusters_created': len(clusters),
            'face_count': len(self.faces)
        }
    
    def label_cluster(self, cluster_id: str, label: str) -> Dict:
        """Label a cluster (assign to person/identity)."""
        if cluster_id not in self.clusters:
            return {'status': 'error', 'message': 'Cluster not found'}
        
        cluster = self.clusters[cluster_id]
        cluster.label = label
        
        return {
            'status': 'success',
            'cluster_id': cluster_id,
            'label': label,
            'face_count': len(cluster.faces)
        }
    
    def get_user_faces(self, user_id: str) -> List[Dict]:
        """Get all recognized faces for user."""
        if user_id not in self.user_faces:
            return []
        
        return [self.faces[fid].to_dict() for fid in self.user_faces[user_id]]
    
    def get_face_info(self, face_id: str) -> Dict:
        """Get detailed face information."""
        if face_id not in self.faces:
            return {'error': 'Face not found'}
        
        return self.faces[face_id].to_dict()
    
    def get_cluster_info(self, cluster_id: str) -> Dict:
        """Get cluster information."""
        if cluster_id not in self.clusters:
            return {'error': 'Cluster not found'}
        
        cluster = self.clusters[cluster_id]
        faces = [self.faces[fid].to_dict() for fid in cluster.faces]
        
        return {
            'cluster': cluster.to_dict(),
            'faces': faces
        }
    
    def export_dataset(self, filter_verified: bool = True) -> Dict:
        """Export face dataset for model training."""
        faces = []
        
        for face in self.faces.values():
            if filter_verified and not face.verified:
                continue
            
            faces.append({
                'face_id': face.face_id,
                'user_id': face.user_id,
                'image_path': face.image_path,
                'attributes': {
                    'age': face.age,
                    'gender': face.gender,
                    'emotion': face.emotion
                },
                'liveness': face.liveness.value,
                'cluster_id': face.cluster_id
            })
        
        return {
            'total_faces': len(faces),
            'verified_faces': sum(1 for f in self.faces.values() if f.verified),
            'clusters': len(self.clusters),
            'faces': faces
        }
    
    def get_stats(self) -> Dict:
        """Get face recognition statistics."""
        verified_faces = sum(1 for f in self.faces.values() if f.verified)
        alive_faces = sum(1 for f in self.faces.values() if f.liveness == LivenessStatus.ALIVE)
        
        return {
            'total_faces': len(self.faces),
            'verified_faces': verified_faces,
            'recognition_rate': round(self.recognized_count / max(len(self.faces), 1), 3) if self.faces else 0,
            'clusters': len(self.clusters),
            'liveness_verified': alive_faces,
            'liveness_verification_rate': round(self.liveness_verified_count / max(len(self.faces), 1), 3) if self.faces else 0,
            'tracked_users': len(self.user_faces),
            'average_confidence': round(sum(f.confidence for f in self.faces.values()) / max(len(self.faces), 1), 3) if self.faces else 0
        }


# Global face recognition engine
face_recognition_engine = FaceRecognitionEngine()
