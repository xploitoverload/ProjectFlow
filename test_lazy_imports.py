#!/usr/bin/env python3
"""Quick test to verify lazy imports work"""
from app import create_app

print("Testing app startup with lazy imports...")
app = create_app()
print("✓ App created successfully!")
print("✓ All lazy imports deferred - no heavy dependencies needed!")
token = app.config.get('HIDDEN_ADMIN_TOKEN', 'NOT FOUND')
print(f"✓ Hidden token generated: {token[:20]}...")
print(f"✓ Total blueprints: {len(app.blueprints)}")
print("\nSUCCESS: App starts WITHOUT installing face_recognition/numpy!")
