"""
Time Revival - AI Photo Video Generation System
Main Flask Application

A complete backend service for generating dynamic videos from static images.
Provides REST API endpoints for frontend integration.
"""

import os
import uuid
import json
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS

from config import Config, get_config
from video_generator import VideoGenerator, MotionMode, VideoStyle


# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = get_config()

# Configure Flask
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

# Enable CORS if configured
if config.CORS_ENABLED:
    CORS(app, origins=config.CORS_ORIGINS.split(","))

# Initialize video generator
video_generator = VideoGenerator(output_dir=str(config.OUTPUT_DIR))

# Task storage (in-memory for demo, use Redis in production)
tasks: Dict[str, Dict[str, Any]] = {}
tasks_lock = threading.Lock()


def json_response(data: Dict[str, Any], status: int = 200) -> Response:
    """Create a JSON response."""
    return jsonify(data), status


def error_response(message: str, status: int = 400, details: Optional[str] = None) -> Response:
    """Create an error response."""
    response = {"success": False, "error": message}
    if details:
        response["details"] = details
    return jsonify(response), status


def validate_image_file(file) -> Optional[str]:
    """Validate uploaded image file."""
    if not file:
        return "No file provided"
    if file.filename == "":
        return "No file selected"
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in config.SUPPORTED_IMAGE_FORMATS:
        return f"Unsupported file format. Supported: {', '.join(config.SUPPORTED_IMAGE_FORMATS)}"
    return None


def validate_video_params(params: Dict[str, Any]) -> Optional[str]:
    """Validate video generation parameters."""
    # Duration
    duration = params.get("duration", config.DEFAULT_DURATION)
    try:
        duration = int(duration)
        if duration < config.MIN_DURATION or duration > config.MAX_DURATION:
            return f"Duration must be between {config.MIN_DURATION} and {config.MAX_DURATION} seconds"
    except (ValueError, TypeError):
        return "Duration must be a valid integer"

    # FPS
    fps = params.get("fps", config.DEFAULT_FPS)
    try:
        fps = int(fps)
        if fps < config.MIN_FPS or fps > config.MAX_FPS:
            return f"FPS must be between {config.MIN_FPS} and {config.MAX_FPS}"
    except (ValueError, TypeError):
        return "FPS must be a valid integer"

    # Resolution
    resolution = params.get("resolution", config.DEFAULT_RESOLUTION)
    if isinstance(resolution, str):
        try:
            res_parts = resolution.split("x")
            resolution = (int(res_parts[0]), int(res_parts[1]))
        except (ValueError, IndexError):
            return "Resolution must be in format WIDTHxHEIGHT (e.g., 1280x720)"

    if resolution[0] < config.MIN_RESOLUTION[0] or resolution[0] > config.MAX_RESOLUTION[0]:
        return f"Width must be between {config.MIN_RESOLUTION[0]} and {config.MAX_RESOLUTION[0]}"
    if resolution[1] < config.MIN_RESOLUTION[1] or resolution[1] > config.MAX_RESOLUTION[1]:
        return f"Height must be between {config.MIN_RESOLUTION[1]} and {config.MAX_RESOLUTION[1]}"

    # Motion mode
    motion_mode = params.get("motion_mode", config.DEFAULT_MOTION_MODE)
    valid_motions = [m.value for m in MotionMode]
    if motion_mode not in valid_motions:
        return f"Invalid motion mode. Valid options: {', '.join(valid_motions)}"

    # Style
    style = params.get("style", config.DEFAULT_STYLE)
    valid_styles = [s.value for s in VideoStyle]
    if style not in valid_styles:
        return f"Invalid style. Valid options: {', '.join(valid_styles)}"

    # Intensity
    intensity = params.get("intensity", config.DEFAULT_INTENSITY)
    try:
        intensity = float(intensity)
        if intensity < 0.0 or intensity > 1.0:
            return "Intensity must be between 0.0 and 1.0"
    except (ValueError, TypeError):
        return "Intensity must be a valid number"

    return None


def background_video_generation(
    task_id: str,
    image_path: str,
    motion_mode: str,
    style: str,
    duration: int,
    fps: int,
    resolution: tuple,
    intensity: float
) -> None:
    """
    Background task for video generation.

    Args:
        task_id: Unique task identifier
        image_path: Path to source image
        motion_mode: Motion effect to apply
        style: Visual style to apply
        duration: Video duration in seconds
        fps: Frames per second
        resolution: Output resolution
        intensity: Effect intensity
    """
    try:
        # Update task status
        with tasks_lock:
            tasks[task_id]["status"] = "processing"
            tasks[task_id]["progress"] = 10

        # Generate video
        result = video_generator.generate_video(
            image_path=image_path,
            motion_mode=motion_mode,
            style=style,
            duration=duration,
            fps=fps,
            resolution=resolution,
            intensity=intensity,
            task_id=task_id
        )

        # Update task with result
        with tasks_lock:
            tasks[task_id]["status"] = "completed" if result["success"] else "failed"
            tasks[task_id]["progress"] = 100
            tasks[task_id]["result"] = result
            tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()

            if result["success"]:
                tasks[task_id]["video_url"] = result["video_url"]
                tasks[task_id]["video_path"] = result["video_path"]

    except Exception as e:
        with tasks_lock:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = str(e)
            tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()


# ==================== API Endpoints ====================

@app.route(f"{config.API_PREFIX}/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.

    Returns service status and available options.
    """
    return json_response({
        "success": True,
        "status": "healthy",
        "service": "time-revival-backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "capabilities": {
            "motion_modes": video_generator.get_available_motions(),
            "styles": video_generator.get_available_styles(),
            "defaults": {
                "duration": config.DEFAULT_DURATION,
                "fps": config.DEFAULT_FPS,
                "resolution": f"{config.DEFAULT_RESOLUTION[0]}x{config.DEFAULT_RESOLUTION[1]}",
                "motion_mode": config.DEFAULT_MOTION_MODE,
                "style": config.DEFAULT_STYLE,
                "intensity": config.DEFAULT_INTENSITY
            },
            "limits": {
                "max_duration": config.MAX_DURATION,
                "max_resolution": f"{config.MAX_RESOLUTION[0]}x{config.MAX_RESOLUTION[1]}",
                "max_fps": config.MAX_FPS,
                "max_upload_size": f"{config.MAX_CONTENT_LENGTH // (1024*1024)}MB"
            }
        }
    })


@app.route(f"{config.API_PREFIX}/generate", methods=["POST"])
def generate_video():
    """
    Generate a dynamic video from an uploaded image.

    Accepts:
        - POST multipart/form-data with image file
        - OR POST JSON with image_url

    Parameters (form/JSON):
        - motion_mode: Motion effect (default: breathing)
        - style: Visual style (default: warm_memories)
        - duration: Video duration in seconds (default: 5)
        - fps: Frames per second (default: 30)
        - resolution: Resolution WIDTHxHEIGHT (default: 1280x720)
        - intensity: Effect intensity 0.0-1.0 (default: 0.5)

    Returns:
        Task ID for tracking generation progress
    """
    # Handle both JSON and form data
    image_path = None
    task_id = str(uuid.uuid4())

    if request.is_json:
        data = request.get_json()
        image_url = data.get("image_url")

        if image_url:
            # Download image from URL
            import urllib.request
            import tempfile

            temp_path = Path(tempfile.gettempdir()) / f"{task_id}_input"

            try:
                urllib.request.urlretrieve(image_url, str(temp_path))
                image_path = str(temp_path)
            except Exception as e:
                return error_response(f"Failed to download image: {str(e)}")
        else:
            return error_response("No image provided. Send image_url in JSON or upload file.")

        params = data

    else:
        # Handle file upload
        if "image" not in request.files:
            return error_response("No image file provided")

        file = request.files["image"]
        error = validate_image_file(file)
        if error:
            return error_response(error)

        # Save uploaded file
        ext = file.filename.rsplit(".", 1)[-1].lower()
        filename = f"{task_id}.{ext}"
        image_path = str(config.UPLOAD_DIR / filename)
        file.save(image_path)

        params = request.form.to_dict()

    # Parse resolution
    resolution_str = params.get("resolution", f"{config.DEFAULT_RESOLUTION[0]}x{config.DEFAULT_RESOLUTION[1]}")
    try:
        res_parts = resolution_str.split("x")
        resolution = (int(res_parts[0]), int(res_parts[1]))
    except (ValueError, IndexError):
        resolution = config.DEFAULT_RESOLUTION

    # Validate parameters
    error = validate_video_params(params)
    if error:
        # Cleanup uploaded file if validation fails
        if image_path and Path(image_path).exists():
            Path(image_path).unlink()
        return error_response(error)

    # Extract validated parameters
    motion_mode = params.get("motion_mode", config.DEFAULT_MOTION_MODE)
    style = params.get("style", config.DEFAULT_STYLE)
    duration = int(params.get("duration", config.DEFAULT_DURATION))
    fps = int(params.get("fps", config.DEFAULT_FPS))
    intensity = float(params.get("intensity", config.DEFAULT_INTENSITY))

    task_data = {
        "task_id": task_id,
        "status": "queued",
        "progress": 0,
        "created_at": datetime.utcnow().isoformat(),
        "params": {
            "motion_mode": motion_mode,
            "style": style,
            "duration": duration,
            "fps": fps,
            "resolution": resolution,
            "intensity": intensity
        },
        "result": None
    }

    with tasks_lock:
        tasks[task_id] = task_data

    # Start background generation
    thread = threading.Thread(
        target=background_video_generation,
        args=(task_id, image_path, motion_mode, style, duration, fps, resolution, intensity)
    )
    thread.daemon = True
    thread.start()

    return json_response({
        "success": True,
        "task_id": task_id,
        "status": "queued",
        "message": "Video generation started",
        "status_url": f"{config.API_PREFIX}/status/{task_id}",
        "params": task_data["params"]
    })


@app.route(f"{config.API_PREFIX}/status/<task_id>", methods=["GET"])
def get_task_status(task_id: str):
    """
    Get the status of a video generation task.

    Args:
        task_id: The task identifier returned from /api/generate

    Returns:
        Task status and result (if completed)
    """
    with tasks_lock:
        task = tasks.get(task_id)

    if not task:
        return error_response("Task not found", status=404)

    response = {
        "success": True,
        "task_id": task_id,
        "status": task["status"],
        "progress": task.get("progress", 0),
        "created_at": task.get("created_at"),
        "completed_at": task.get("completed_at")
    }

    if task["status"] == "completed" and task.get("result"):
        response["result"] = {
            "video_url": task.get("video_url"),
            "video_path": task.get("video_path"),
            "duration": task["result"].get("duration"),
            "fps": task["result"].get("fps"),
            "resolution": task["result"].get("resolution"),
            "file_size": task["result"].get("file_size"),
            "message": task["result"].get("message")
        }

    elif task["status"] == "failed":
        response["error"] = task.get("error") or task.get("result", {}).get("error", "Unknown error")

    return json_response(response)


@app.route(f"{config.API_PREFIX}/video/<task_id>", methods=["GET"])
def get_video(task_id: str):
    """
    Download the generated video.

    Args:
        task_id: The task identifier

    Returns:
        Video file
    """
    with tasks_lock:
        task = tasks.get(task_id)

    if not task:
        return error_response("Task not found", status=404)

    if task["status"] != "completed":
        return error_response(f"Video not ready. Current status: {task['status']}")

    video_path = task.get("video_path")
    if not video_path or not Path(video_path).exists():
        return error_response("Video file not found", status=404)

    return send_file(
        video_path,
        mimetype="video/mp4",
        as_attachment=False,
        download_name=f"{task_id}.mp4"
    )


@app.route(f"{config.API_PREFIX}/motions", methods=["GET"])
def get_motion_modes():
    """
    Get available motion modes.

    Returns:
        List of motion modes with descriptions
    """
    return json_response({
        "success": True,
        "motion_modes": video_generator.get_available_motions()
    })


@app.route(f"{config.API_PREFIX}/styles", methods=["GET"])
def get_styles():
    """
    Get available video styles.

    Returns:
        List of styles with descriptions
    """
    return json_response({
        "success": True,
        "styles": video_generator.get_available_styles()
    })


@app.route(f"{config.API_PREFIX}/preview", methods=["POST"])
def generate_preview():
    """
    Generate a short preview video (3 seconds) for quick testing.

    Same as /generate but with limited duration.
    """
    # Force short duration for preview
    if request.is_json:
        data = request.get_json()
        data["duration"] = 3
        request._cached_json = data
        request.get_json = lambda: data
    else:
        # Modify form data
        params = request.form.to_dict()
        params["duration"] = "3"
        request.form = params

    return generate_video()


@app.route(f"{config.API_PREFIX}/batch", methods=["POST"])
def batch_generate():
    """
    Generate multiple videos with different settings from one image.

    Accepts JSON with single image_url and array of generation configs.
    """
    if not request.is_json:
        return error_response("This endpoint only accepts JSON")

    data = request.get_json()
    image_url = data.get("image_url")

    if not image_url:
        return error_response("image_url is required")

    configs = data.get("configs", [])
    if not configs:
        return error_response("configs array is required with at least one configuration")

    if len(configs) > 5:
        return error_response("Maximum 5 configurations allowed per batch")

    # Download image
    import urllib.request
    import tempfile

    batch_id = str(uuid.uuid4())
    temp_path = Path(tempfile.gettempdir()) / f"{batch_id}_input"

    try:
        urllib.request.urlretrieve(image_url, str(temp_path))
    except Exception as e:
        return error_response(f"Failed to download image: {str(e)}")

    # Create tasks for each config
    task_ids = []
    with tasks_lock:
        for idx, config_params in enumerate(configs):
            task_id = str(uuid.uuid4())
            task_ids.append(task_id)

            # Apply defaults and merge with provided params
            motion_mode = config_params.get("motion_mode", config.DEFAULT_MOTION_MODE)
            style = config_params.get("style", config.DEFAULT_STYLE)
            duration = min(int(config_params.get("duration", 3)), 5)  # Cap at 5 for batch
            fps = int(config_params.get("fps", config.DEFAULT_FPS))
            intensity = float(config_params.get("intensity", config.DEFAULT_INTENSITY))

            task_data = {
                "task_id": task_id,
                "batch_id": batch_id,
                "status": "queued",
                "progress": 0,
                "created_at": datetime.utcnow().isoformat(),
                "params": {
                    "motion_mode": motion_mode,
                    "style": style,
                    "duration": duration,
                    "fps": fps,
                    "intensity": intensity
                }
            }
            tasks[task_id] = task_data

            # Start generation thread
            thread = threading.Thread(
                target=background_video_generation,
                args=(task_id, str(temp_path), motion_mode, style, duration, fps, (1280, 720), intensity)
            )
            thread.daemon = True
            thread.start()

    return json_response({
        "success": True,
        "batch_id": batch_id,
        "task_ids": task_ids,
        "message": f"Started generation of {len(task_ids)} videos",
        "status_url": f"{config.API_PREFIX}/batch/{batch_id}"
    })


@app.route(f"{config.API_PREFIX}/batch/<batch_id>", methods=["GET"])
def get_batch_status(batch_id: str):
    """Get status of all tasks in a batch."""
    with tasks_lock:
        batch_tasks = {
            task_id: task
            for task_id, task in tasks.items()
            if task.get("batch_id") == batch_id
        }

    if not batch_tasks:
        return error_response("Batch not found", status=404)

    tasks_summary = []
    completed = 0
    failed = 0

    for task_id, task in batch_tasks.items():
        task_info = {
            "task_id": task_id,
            "status": task["status"],
            "progress": task.get("progress", 0)
        }
        if task["status"] == "completed":
            task_info["video_url"] = task.get("video_url")
            completed += 1
        elif task["status"] == "failed":
            task_info["error"] = task.get("error")
            failed += 1

        tasks_summary.append(task_info)

    return json_response({
        "success": True,
        "batch_id": batch_id,
        "total": len(batch_tasks),
        "completed": completed,
        "failed": failed,
        "pending": len(batch_tasks) - completed - failed,
        "tasks": tasks_summary
    })


# ==================== Error Handlers ====================

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return error_response(
        f"File too large. Maximum size is {config.MAX_CONTENT_LENGTH // (1024*1024)}MB",
        status=413
    )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return error_response("Endpoint not found", status=404)


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    return error_response("Internal server error", status=500)


# ==================== Main Entry Point ====================

def create_app() -> Flask:
    """Create and configure the Flask application."""
    return app


if __name__ == "__main__":
    print("=" * 60)
    print("Time Revival - AI Photo Video Generation System")
    print("=" * 60)
    print(f"\nBackend starting on {config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"API Prefix: {config.API_PREFIX}")
    print(f"\nEndpoints:")
    print(f"  GET  {config.API_PREFIX}/health           - Health check")
    print(f"  POST {config.API_PREFIX}/generate          - Generate video")
    print(f"  GET  {config.API_PREFIX}/status/<task_id> - Check task status")
    print(f"  GET  {config.API_PREFIX}/video/<task_id>  - Download video")
    print(f"  GET  {config.API_PREFIX}/motions          - List motion modes")
    print(f"  GET  {config.API_PREFIX}/styles            - List styles")
    print(f"  POST {config.API_PREFIX}/preview           - Quick preview")
    print(f"  POST {config.API_PREFIX}/batch             - Batch generation")
    print(f"\nPress Ctrl+C to stop the server")
    print("=" * 60)

    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
        threaded=config.FLASK_THREADED
    )
