"""
Time Revival - AI Photo Video Generation System
Video Generator Module

This module provides advanced video generation capabilities using image processing
techniques. It can generate dynamic videos from static images without requiring
external AI services.
"""

import os
import uuid
import math
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
import cv2


class MotionMode(Enum):
    """Supported motion modes for video generation."""
    BREATHING = "breathing"           # Gentle scale oscillation (breathing effect)
    SWING = "swing"                   # Left-right swinging motion
    PAN = "pan"                       # Smooth panning/zooming
    ZOOM = "zoom"                     # Zoom in/out effect
    SHAKE = "shake"                   # Subtle shaking effect
    WAVE = "wave"                     # Wave-like distortion
    PULSE = "pulse"                   # Heartbeat-like pulse effect
    FLOAT = "float"                   # Gentle floating motion
    ROTATION = "rotation"             # Slow rotation
    KEN_BURNS = "ken_burns"           # Classic Ken Burns effect (pan + zoom)


class VideoStyle(Enum):
    """Supported video styles."""
    ORIGINAL = "original"              # Original colors
    WARM_MEMORIES = "warm_memories"   # Warm, nostalgic tone
    COOL_VINTAGE = "cool_vintage"     # Cool vintage look
    BLACK_WHITE = "black_white"       # Black and white
    SEPIA = "sepia"                   # Sepia tone
    CINEMATIC = "cinematic"           # Cinematic color grading
    DREAMY = "dreamy"                 # Soft, dreamy effect
    VIVID = "vivid"                   # Enhanced colors
    DRAMATIC = "dramatic"             # High contrast dramatic look
    SOFT_FOCUS = "soft_focus"         # Soft focus effect


@dataclass
class VideoConfig:
    """Configuration for video generation."""
    motion_mode: MotionMode = MotionMode.BREATHING
    style: VideoStyle = VideoStyle.WARM_MEMORIES
    duration: int = 5  # seconds
    fps: int = 30
    resolution: Tuple[int, int] = (1280, 720)
    intensity: float = 0.5  # Effect intensity (0.0 to 1.0)


class VideoGenerator:
    """
    Advanced video generator that creates dynamic videos from static images.
    Supports multiple motion modes and styles without requiring external AI services.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the video generator.

        Args:
            output_dir: Directory to save generated videos. If None, uses system temp directory.
        """
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir()) / "time_revival"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._temp_frames_dir = self.output_dir / "frames"
        self._temp_frames_dir.mkdir(exist_ok=True)

    def generate_video(
        self,
        image_path: str,
        motion_mode: str = "breathing",
        style: str = "warm_memories",
        duration: int = 5,
        fps: int = 30,
        resolution: Tuple[int, int] = (1280, 720),
        intensity: float = 0.5,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a dynamic video from a static image.

        Args:
            image_path: Path to the input image
            motion_mode: Motion mode to apply
            style: Visual style to apply
            duration: Video duration in seconds
            fps: Frames per second
            resolution: Output video resolution (width, height)
            intensity: Effect intensity (0.0 to 1.0)
            task_id: Optional task ID for tracking

        Returns:
            Dictionary containing generation results and metadata
        """
        task_id = task_id or str(uuid.uuid4())

        try:
            # Load and validate image
            image = self._load_image(image_path)
            if image is None:
                return {
                    "success": False,
                    "task_id": task_id,
                    "error": "Failed to load image. Please ensure the image file is valid."
                }

            # Apply style to the image
            styled_image = self._apply_style(image, style)

            # Get motion mode enum
            motion = self._parse_motion_mode(motion_mode)

            # Generate frames
            frames = self._generate_frames(
                styled_image,
                motion,
                duration,
                fps,
                resolution,
                intensity
            )

            # Create video from frames
            output_path = self.output_dir / f"{task_id}.mp4"
            self._create_video(frames, output_path, fps)

            # Calculate video metadata
            file_size = output_path.stat().st_size if output_path.exists() else 0

            return {
                "success": True,
                "task_id": task_id,
                "video_url": f"/api/video/{task_id}",
                "video_path": str(output_path),
                "duration": duration,
                "fps": fps,
                "resolution": resolution,
                "motion_mode": motion_mode,
                "style": style,
                "file_size": file_size,
                "message": "Video generated successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "task_id": task_id,
                "error": f"Video generation failed: {str(e)}"
            }

    def _load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load and validate an image file."""
        try:
            img = Image.open(image_path)
            img = img.convert("RGB")
            return img
        except Exception:
            return None

    def _parse_motion_mode(self, mode: str) -> MotionMode:
        """Parse motion mode string to enum."""
        mode = mode.lower().strip()
        for motion in MotionMode:
            if motion.value == mode:
                return motion
        return MotionMode.BREATHING  # Default

    def _apply_style(self, image: Image.Image, style: str) -> Image.Image:
        """
        Apply visual style to the image.

        Args:
            image: Input PIL Image
            style: Style name

        Returns:
            Styled PIL Image
        """
        style = style.lower().strip()

        # Map style names to style enums
        style_map = {
            "original": VideoStyle.ORIGINAL,
            "warm_memories": VideoStyle.WARM_MEMORIES,
            "warm": VideoStyle.WARM_MEMORIES,
            "cool_vintage": VideoStyle.COOL_VINTAGE,
            "vintage": VideoStyle.COOL_VINTAGE,
            "black_white": VideoStyle.BLACK_WHITE,
            "bw": VideoStyle.BLACK_WHITE,
            "grayscale": VideoStyle.BLACK_WHITE,
            "sepia": VideoStyle.SEPIA,
            "cinematic": VideoStyle.CINEMATIC,
            "dreamy": VideoStyle.DREAMY,
            "vivid": VideoStyle.VIVID,
            "dramatic": VideoStyle.DRAMATIC,
            "soft_focus": VideoStyle.SOFT_FOCUS,
            "soft": VideoStyle.SOFT_FOCUS,
        }

        style_enum = style_map.get(style, VideoStyle.WARM_MEMORIES)

        # Apply style transformations
        if style_enum == VideoStyle.ORIGINAL:
            return image

        elif style_enum == VideoStyle.WARM_MEMORIES:
            # Warm, nostalgic tone with slight desaturation
            enhancer = ImageEnhance.Color(image)
            img = enhancer.enhance(0.8)
            # Warm color shift
            r, g, b = img.split()
            r = ImageEnhance.Brightness(r).enhance(1.1)
            b = ImageEnhance.Brightness(b).enhance(0.9)
            img = Image.merge("RGB", (r, g, b))
            # Add slight vignette
            img = self._add_vignette(img, intensity=0.3)
            return img

        elif style_enum == VideoStyle.COOL_VINTAGE:
            # Cool vintage look with fade
            enhancer = ImageEnhance.Color(image)
            img = enhancer.enhance(0.6)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(0.9)
            # Cool color shift
            r, g, b = img.split()
            r = ImageEnhance.Brightness(r).enhance(0.95)
            b = ImageEnhance.Brightness(b).enhance(1.1)
            img = Image.merge("RGB", (r, g, b))
            return img

        elif style_enum == VideoStyle.BLACK_WHITE:
            # Classic black and white
            img = ImageOps.grayscale(image)
            img = img.convert("RGB")
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
            return img

        elif style_enum == VideoStyle.SEPIA:
            # Sepia tone
            img = ImageOps.grayscale(image)
            img = img.convert("RGB")
            # Apply sepia matrix
            pixels = img.load()
            width, height = img.size
            for py in range(height):
                for px in range(width):
                    r, g, b = pixels[px, py]
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[px, py] = (min(255, tr), min(255, tg), min(255, tb))
            return img

        elif style_enum == VideoStyle.CINEMATIC:
            # Cinematic color grading
            enhancer = ImageEnhance.Color(image)
            img = enhancer.enhance(0.85)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.15)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.95)
            # Teal and orange color grading simulation
            r, g, b = img.split()
            r = ImageEnhance.Brightness(r).enhance(1.05)
            b = ImageEnhance.Brightness(b).enhance(1.02)
            img = Image.merge("RGB", (r, g, b))
            img = self._add_vignette(img, intensity=0.4)
            return img

        elif style_enum == VideoStyle.DREAMY:
            # Soft, dreamy effect with blur
            img = image.filter(ImageFilter.GaussianBlur(radius=2))
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.1)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(0.8)  # Reduce sharpness for softness
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.05)
            return img

        elif style_enum == VideoStyle.VIVID:
            # Enhanced, vibrant colors
            enhancer = ImageEnhance.Color(image)
            img = enhancer.enhance(1.4)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.2)
            return img

        elif style_enum == VideoStyle.DRAMATIC:
            # High contrast dramatic look
            enhancer = ImageEnhance.Contrast(image)
            img = enhancer.enhance(1.5)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.8)
            img = self._add_vignette(img, intensity=0.5)
            return img

        elif style_enum == VideoStyle.SOFT_FOCUS:
            # Soft focus effect
            img = image.filter(ImageFilter.GaussianBlur(radius=1))
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(0.7)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.02)
            return img

        return image

    def _add_vignette(self, image: Image.Image, intensity: float = 0.5) -> Image.Image:
        """Add a vignette effect to the image."""
        width, height = image.size
        x = width // 2
        y = height // 2

        # Create radial gradient mask
        mask = Image.new("L", (width, height), 255)
        draw = ImageDraw.Draw(mask)

        max_dist = math.sqrt(x**2 + y**2)

        for i in range(int(max_dist * (1 - intensity * 0.5))):
            shade = int(255 * (1 - (i / max_dist) * intensity * 1.5))
            draw.ellipse(
                [x - i, y - i, x + i, y + i],
                fill=max(0, shade)
            )

        # Apply vignette
        result = image.copy()
        result.putalpha(mask)
        result = result.convert("RGB")
        return result

    def _generate_frames(
        self,
        image: Image.Image,
        motion_mode: MotionMode,
        duration: int,
        fps: int,
        resolution: Tuple[int, int],
        intensity: float
    ) -> List[Image.Image]:
        """
        Generate a sequence of frames with motion effects.

        Args:
            image: Base image to animate
            motion_mode: Motion mode to apply
            duration: Duration in seconds
            fps: Frames per second
            resolution: Output resolution
            intensity: Effect intensity

        Returns:
            List of PIL Image frames
        """
        total_frames = duration * fps
        frames = []

        # Resize image to resolution first
        image = image.resize(resolution, Image.Resampling.LANCZOS)

        for frame_idx in range(total_frames):
            frame = self._apply_motion(
                image.copy(),
                motion_mode,
                frame_idx,
                total_frames,
                intensity
            )
            frames.append(frame)

        return frames

    def _apply_motion(
        self,
        image: Image.Image,
        motion_mode: MotionMode,
        frame_idx: int,
        total_frames: int,
        intensity: float
    ) -> Image.Image:
        """
        Apply motion effect to a single frame.

        Args:
            image: Input image
            motion_mode: Motion mode to apply
            frame_idx: Current frame index
            total_frames: Total number of frames
            intensity: Effect intensity

        Returns:
            Processed frame
        """
        progress = frame_idx / total_frames  # 0 to 1

        if motion_mode == MotionMode.BREATHING:
            # Gentle scale oscillation
            scale = 1.0 + 0.02 * intensity * math.sin(progress * 2 * math.pi * 3)
            return self._scale_image(image, scale)

        elif motion_mode == MotionMode.SWING:
            # Left-right swinging
            max_angle = 5 * intensity
            angle = max_angle * math.sin(progress * 2 * math.pi * 2)
            return self._rotate_image(image, angle)

        elif motion_mode == MotionMode.PAN:
            # Smooth panning
            max_offset = 30 * intensity
            offset_x = max_offset * math.sin(progress * 2 * math.pi)
            offset_y = max_offset * 0.5 * math.sin(progress * 2 * math.pi * 0.5)
            return self._translate_image(image, offset_x, offset_y)

        elif motion_mode == MotionMode.ZOOM:
            # Zoom in/out effect
            scale = 1.0 + 0.15 * intensity * math.sin(progress * 2 * math.pi * 2)
            return self._scale_image(image, scale)

        elif motion_mode == MotionMode.SHAKE:
            # Subtle shaking
            max_shake = 3 * intensity
            shake_x = max_shake * (math.random() - 0.5) * 2
            shake_y = max_shake * (math.random() - 0.5) * 2
            return self._translate_image(image, shake_x, shake_y)

        elif motion_mode == MotionMode.WAVE:
            # Wave-like distortion
            return self._wave_transform(image, progress, intensity)

        elif motion_mode == MotionMode.PULSE:
            # Heartbeat-like pulse
            pulse_freq = 1.5  # Heartbeats per cycle
            pulse = math.sin(progress * 2 * math.pi * pulse_freq)
            scale = 1.0 + 0.03 * intensity * (pulse if pulse > 0 else 0)
            return self._scale_image(image, scale)

        elif motion_mode == MotionMode.FLOAT:
            # Gentle floating motion
            offset_y = 10 * intensity * math.sin(progress * 2 * math.pi * 1.5)
            offset_x = 5 * intensity * math.cos(progress * 2 * math.pi)
            return self._translate_image(image, offset_x, offset_y)

        elif motion_mode == MotionMode.ROTATION:
            # Slow rotation
            max_angle = 10 * intensity
            angle = max_angle * math.sin(progress * 2 * math.pi)
            return self._rotate_image(image, angle)

        elif motion_mode == MotionMode.KEN_BURNS:
            # Classic Ken Burns effect (slow zoom with pan)
            scale = 1.0 + 0.2 * intensity * progress
            offset_x = 20 * intensity * math.sin(progress * math.pi)
            offset_y = 10 * intensity * math.cos(progress * math.pi)
            frame = self._scale_image(image, scale)
            return self._translate_image(frame, offset_x, offset_y)

        return image

    def _scale_image(self, image: Image.Image, scale: float) -> Image.Image:
        """Scale image around center."""
        if abs(scale - 1.0) < 0.001:
            return image

        width, height = image.size
        new_width = int(width * scale)
        new_height = int(height * scale)

        # Resize with high quality
        scaled = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Crop center
        left = (new_width - width) // 2
        top = (new_height - height) // 2
        right = left + width
        bottom = top + height

        if left < 0:
            # Image is smaller, need to pad
            padded = Image.new("RGB", (width, height), (0, 0, 0))
            paste_x = (width - new_width) // 2
            paste_y = (height - new_height) // 2
            padded.paste(scaled, (paste_x, paste_y))
            return padded

        return scaled.crop((left, top, right, bottom))

    def _rotate_image(self, image: Image.Image, angle: float) -> Image.Image:
        """Rotate image around center."""
        if abs(angle) < 0.1:
            return image

        width, height = image.size
        # Rotate with expand to avoid cropping
        rotated = image.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)

        # Crop back to original size
        rot_width, rot_height = rotated.size
        left = (rot_width - width) // 2
        top = (rot_height - height) // 2
        right = left + width
        bottom = top + height

        if left < 0:
            # Pad instead of crop
            padded = Image.new("RGB", (width, height), (0, 0, 0))
            paste_x = (width - rot_width) // 2 if rot_width < width else 0
            paste_y = (height - rot_height) // 2 if rot_height < height else 0
            padded.paste(rotated, (paste_x, paste_y))
            return padded

        return rotated.crop((left, top, right, bottom))

    def _translate_image(self, image: Image.Image, offset_x: float, offset_y: float) -> Image.Image:
        """Translate image by offset."""
        if abs(offset_x) < 0.5 and abs(offset_y) < 0.5:
            return image

        width, height = image.size

        # Create translation matrix
        matrix = [
            1, 0, -offset_x,
            0, 1, -offset_y
        ]

        translated = image.transform(
            (width, height),
            Image.Transform.AFFINE,
            matrix,
            resample=Image.Resampling.BICUBIC
        )

        return translated

    def _wave_transform(self, image: Image.Image, progress: float, intensity: float) -> Image.Image:
        """Apply wave-like distortion effect."""
        width, height = image.size
        frequency = 3
        amplitude = 5 * intensity

        # Create wave distortion
        pixels = image.load()
        output = Image.new("RGB", (width, height))
        out_pixels = output.load()

        for y in range(height):
            offset_x = int(amplitude * math.sin(2 * math.pi * frequency * y / height + progress * 2 * math.pi))
            for x in range(width):
                src_x = (x - offset_x) % width
                src_y = y
                out_pixels[x, y] = pixels[src_x, src_y]

        return output

    def _create_video(
        self,
        frames: List[Image.Image],
        output_path: Path,
        fps: int
    ) -> None:
        """
        Create video file from frames using OpenCV.

        Args:
            frames: List of PIL Image frames
            output_path: Path to save the video
            fps: Frames per second
        """
        if not frames:
            raise ValueError("No frames to create video")

        # Get frame dimensions
        frame = frames[0]
        height, width = np.array(frame).shape[:2]

        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(
            str(output_path),
            fourcc,
            fps,
            (width, height)
        )

        if not writer.isOpened():
            raise RuntimeError("Failed to initialize video writer")

        try:
            for pil_frame in frames:
                # Convert PIL to OpenCV format (RGB to BGR)
                cv_frame = np.array(pil_frame)
                cv_frame = cv2.cvtColor(cv_frame, cv2.COLOR_RGB2BGR)
                writer.write(cv_frame)
        finally:
            writer.release()

        # Verify file was created
        if not output_path.exists():
            raise RuntimeError("Video file was not created")

    def get_available_motions(self) -> List[Dict[str, str]]:
        """Get list of available motion modes."""
        return [
            {"id": m.value, "name": self._humanize_name(m.value), "description": self._get_motion_description(m)}
            for m in MotionMode
        ]

    def get_available_styles(self) -> List[Dict[str, str]]:
        """Get list of available styles."""
        return [
            {"id": s.value, "name": self._humanize_name(s.value), "description": self._get_style_description(s)}
            for s in VideoStyle
        ]

    def _humanize_name(self, name: str) -> str:
        """Convert snake_case to Title Case."""
        return " ".join(word.capitalize() for word in name.split("_"))

    def _get_motion_description(self, motion: MotionMode) -> str:
        """Get description for motion mode."""
        descriptions = {
            MotionMode.BREATHING: "Gentle breathing motion with subtle scaling",
            MotionMode.SWING: "Left-right swinging pendulum effect",
            MotionMode.PAN: "Smooth diagonal panning motion",
            MotionMode.ZOOM: "Rhythmic zoom in and out",
            MotionMode.SHAKE: "Subtle camera shake",
            MotionMode.WAVE: "Wave-like distortion effect",
            MotionMode.PULSE: "Heartbeat-like pulse effect",
            MotionMode.FLOAT: "Gentle floating movement",
            MotionMode.ROTATION: "Slow rotation effect",
            MotionMode.KEN_BURNS: "Classic Ken Burns pan and zoom"
        }
        return descriptions.get(motion, "")

    def _get_style_description(self, style: VideoStyle) -> str:
        """Get description for style."""
        descriptions = {
            VideoStyle.ORIGINAL: "Keep original image colors",
            VideoStyle.WARM_MEMORIES: "Warm, nostalgic tone with vignette",
            VideoStyle.COOL_VINTAGE: "Cool vintage faded look",
            VideoStyle.BLACK_WHITE: "Classic black and white",
            VideoStyle.SEPIA: "Vintage sepia tone",
            VideoStyle.CINEMATIC: "Cinematic color grading with teal/orange",
            VideoStyle.DREAMY: "Soft and dreamy atmosphere",
            VideoStyle.VIVID: "Enhanced vibrant colors",
            VideoStyle.DRAMATIC: "High contrast dramatic look",
            VideoStyle.SOFT_FOCUS: "Soft focus blur effect"
        }
        return descriptions.get(style, "")


def generate_video_sync(
    image_path: str,
    motion_mode: str = "breathing",
    style: str = "warm_memories",
    duration: int = 5,
    fps: int = 30,
    resolution: Tuple[int, int] = (1280, 720),
    intensity: float = 0.5
) -> Dict[str, Any]:
    """
    Synchronous video generation function for backward compatibility.

    Args:
        image_path: Path to input image
        motion_mode: Motion mode to apply
        style: Visual style to apply
        duration: Video duration in seconds
        fps: Frames per second
        resolution: Output resolution
        intensity: Effect intensity

    Returns:
        Generation result dictionary
    """
    generator = VideoGenerator()
    return generator.generate_video(
        image_path=image_path,
        motion_mode=motion_mode,
        style=style,
        duration=duration,
        fps=fps,
        resolution=resolution,
        intensity=intensity
    )


# Example usage and testing
if __name__ == "__main__":
    import sys

    print("Time Revival - Video Generator Module")
    print("=" * 50)
    print("\nAvailable Motion Modes:")
    generator = VideoGenerator()
    for motion in generator.get_available_motions():
        print(f"  - {motion['id']}: {motion['description']}")

    print("\nAvailable Styles:")
    for style in generator.get_available_styles():
        print(f"  - {style['id']}: {style['description']}")

    print("\nModule loaded successfully!")
