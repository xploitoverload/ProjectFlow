# app/routes/face_recognition_routes.py
"""
Face Recognition API Routes
Endpoints for face detection, recognition, liveness, and clustering.
"""

from flask import Blueprint, request, jsonify, send_file
from functools import wraps
from werkzeug.utils import secure_filename
import os
import logging

from app.ml.face_recognition import face_recognition_engine

logger = logging.getLogger(__name__)

# Create blueprint
face_bp = Blueprint('face_recognition', __name__, url_prefix='/api/v1/face')

UPLOAD_FOLDER = 'uploads/faces'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}


def require_auth(f):
    """Require authentication for endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================================
# FACE DETECTION ROUTES
# ============================================================================

@face_bp.route('/detect', methods=['POST'])
@require_auth
def detect_faces():
    """Detect faces in uploaded image."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Save file
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Detect faces
    faces = face_recognition_engine.detect_faces(filepath)
    
    return jsonify({
        'status': 'success',
        'faces': [f.to_dict() for f in faces],
        'face_count': len(faces)
    }), 201


@face_bp.route('/detect/batch', methods=['POST'])
@require_auth
def detect_batch():
    """Detect faces in multiple images."""
    if 'images' not in request.files:
        return jsonify({'error': 'No images provided'}), 400
    
    files = request.files.getlist('images')
    all_faces = []
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    for file in files:
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            faces = face_recognition_engine.detect_faces(filepath)
            all_faces.extend(faces)
    
    return jsonify({
        'status': 'success',
        'total_faces': len(all_faces),
        'faces': [f.to_dict() for f in all_faces]
    }), 201


# ============================================================================
# FACE RECOGNITION/IDENTIFICATION ROUTES
# ============================================================================

@face_bp.route('/<face_id>/recognize', methods=['POST'])
@require_auth
def recognize_face(face_id):
    """Recognize and assign face to user."""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    result = face_recognition_engine.recognize_face(face_id, user_id)
    
    if result.get('status') == 'error':
        return jsonify(result), 404
    
    return jsonify(result), 200


@face_bp.route('/user/<user_id>', methods=['GET'])
@require_auth
def get_user_faces(user_id):
    """Get all recognized faces for user."""
    faces = face_recognition_engine.get_user_faces(user_id)
    
    return jsonify({
        'user_id': user_id,
        'face_count': len(faces),
        'faces': faces
    })


@face_bp.route('/<face_id>', methods=['GET'])
@require_auth
def get_face_info(face_id):
    """Get face information."""
    info = face_recognition_engine.get_face_info(face_id)
    
    if 'error' in info:
        return jsonify(info), 404
    
    return jsonify(info)


# ============================================================================
# LIVENESS DETECTION ROUTES
# ============================================================================

@face_bp.route('/<face_id>/liveness', methods=['POST'])
@require_auth
def detect_liveness(face_id):
    """Detect liveness (real vs fake face)."""
    result = face_recognition_engine.detect_liveness(face_id)
    
    if result.get('status') == 'error':
        return jsonify(result), 404
    
    return jsonify(result)


@face_bp.route('/liveness/batch', methods=['POST'])
@require_auth
def liveness_batch():
    """Detect liveness for multiple faces."""
    data = request.get_json()
    face_ids = data.get('face_ids', [])
    
    results = []
    for face_id in face_ids:
        result = face_recognition_engine.detect_liveness(face_id)
        if result.get('status') == 'success':
            results.append(result)
    
    return jsonify({
        'status': 'success',
        'processed': len(results),
        'results': results
    })


# ============================================================================
# FACE EMBEDDING & COMPARISON ROUTES
# ============================================================================

@face_bp.route('/<face_id>/embedding', methods=['POST'])
@require_auth
def generate_embedding(face_id):
    """Generate face embedding."""
    data = request.get_json()
    model = data.get('model', 'deepface')
    
    result = face_recognition_engine.generate_embedding(face_id, model)
    
    if result.get('status') == 'error':
        return jsonify(result), 404
    
    return jsonify(result)


@face_bp.route('/compare', methods=['POST'])
@require_auth
def compare_faces():
    """Compare two faces."""
    data = request.get_json()
    face_id_1 = data.get('face_id_1')
    face_id_2 = data.get('face_id_2')
    threshold = data.get('threshold', 0.6)
    
    if not face_id_1 or not face_id_2:
        return jsonify({'error': 'face_id_1 and face_id_2 required'}), 400
    
    result = face_recognition_engine.compare_faces(face_id_1, face_id_2, threshold)
    
    if result.get('status') == 'error':
        return jsonify(result), 404
    
    return jsonify(result)


@face_bp.route('/compare/batch', methods=['POST'])
@require_auth
def compare_batch():
    """Compare multiple face pairs."""
    data = request.get_json()
    pairs = data.get('pairs', [])
    threshold = data.get('threshold', 0.6)
    
    results = []
    for pair in pairs:
        result = face_recognition_engine.compare_faces(
            pair.get('face_id_1'),
            pair.get('face_id_2'),
            threshold
        )
        if result.get('status') == 'success':
            results.append(result)
    
    return jsonify({
        'status': 'success',
        'comparisons': len(results),
        'results': results
    })


# ============================================================================
# CLUSTERING ROUTES
# ============================================================================

@face_bp.route('/cluster', methods=['POST'])
@require_auth
def cluster_faces():
    """Cluster faces into groups."""
    data = request.get_json()
    threshold = data.get('threshold', 0.6)
    
    result = face_recognition_engine.cluster_faces(threshold)
    
    return jsonify(result)


@face_bp.route('/cluster/<cluster_id>', methods=['GET'])
@require_auth
def get_cluster(cluster_id):
    """Get cluster information."""
    info = face_recognition_engine.get_cluster_info(cluster_id)
    
    if 'error' in info:
        return jsonify(info), 404
    
    return jsonify(info)


@face_bp.route('/cluster/<cluster_id>/label', methods=['POST'])
@require_auth
def label_cluster(cluster_id):
    """Label cluster (assign identity)."""
    data = request.get_json()
    label = data.get('label')
    
    if not label:
        return jsonify({'error': 'label required'}), 400
    
    result = face_recognition_engine.label_cluster(cluster_id, label)
    
    if result.get('status') == 'error':
        return jsonify(result), 404
    
    return jsonify(result)


# ============================================================================
# ANALYTICS & EXPORT ROUTES
# ============================================================================

@face_bp.route('/stats', methods=['GET'])
@require_auth
def stats():
    """Get face recognition statistics."""
    stats_data = face_recognition_engine.get_stats()
    return jsonify(stats_data)


@face_bp.route('/export', methods=['GET'])
@require_auth
def export_dataset():
    """Export face dataset."""
    verified_only = request.args.get('verified_only', 'true').lower() == 'true'
    
    data = face_recognition_engine.export_dataset(verified_only)
    
    return jsonify(data)


@face_bp.route('/export/csv', methods=['GET'])
@require_auth
def export_csv():
    """Export face dataset as CSV."""
    import csv
    import io
    
    verified_only = request.args.get('verified_only', 'true').lower() == 'true'
    data = face_recognition_engine.export_dataset(verified_only)
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Face ID', 'User ID', 'Age', 'Gender', 'Emotion', 'Liveness', 'Cluster ID'])
    
    for face in data['faces']:
        writer.writerow([
            face['face_id'],
            face.get('user_id', ''),
            face['attributes']['age'],
            face['attributes']['gender'],
            face['attributes']['emotion'],
            face['liveness'],
            face.get('cluster_id', '')
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='faces_export.csv'
    )


# ============================================================================
# HEALTH CHECK
# ============================================================================

@face_bp.route('/health', methods=['GET'])
def health():
    """Health check for face recognition."""
    stats = face_recognition_engine.get_stats()
    return jsonify({
        'status': 'healthy',
        'detection_model': face_recognition_engine.detection_model.value,
        'stats': stats
    })
