#!/usr/bin/env python3
"""
Time Revival - Backend API Server
Entry point for deployment
"""

import os
import sys

# Add the application directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"

    print("=" * 60)
    print("Time Revival - AI Photo Video Generation System")
    print("=" * 60)
    print(f"\nAPI Server starting on port {port}")
    print(f"Access the API at: http://0.0.0.0:{port}/api/health")
    print("\nAvailable endpoints:")
    print("  GET  /api/health           - Health check")
    print("  POST /api/generate          - Generate video")
    print("  GET  /api/status/<task_id> - Check task status")
    print("  GET  /api/video/<task_id>  - Download video")
    print("  GET  /api/motions          - List motion modes")
    print("  GET  /api/styles            - List styles")
    print("  POST /api/preview           - Quick preview")
    print("  POST /api/batch             - Batch generation")
    print("=" * 60)

    app.run(host=host, port=port, debug=False, threaded=True)
