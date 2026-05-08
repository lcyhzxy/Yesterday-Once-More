"""
时光重现 - AI照片视频生成后端服务 (独立打包版本)
可直接部署到 Railway、Render、Vercel Serverless Functions 等平台
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import base64
from io import BytesIO
from PIL import Image
import requests
import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_FOLDER = '/tmp/outputs'
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
EXECUTOR = ThreadPoolExecutor(max_workers=2)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 获取环境变量
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')

def process_image(image_path, motion_mode='breathing', duration=5, style='natural'):
    """
    图像预处理和增强
    """
    try:
        img = Image.open(image_path)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 调整尺寸以适合AI模型
        max_size = 1024
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # 保存处理后的图片
        enhanced_path = image_path.replace('.', '_enhanced.')
        img.save(enhanced_path, quality=95)

        return enhanced_path
    except Exception as e:
        print(f"Image processing error: {e}")
        return image_path

def generate_video_with_ai(image_path, motion_mode='breathing', duration=5):
    """
    使用AI模型生成视频
    支持多个AI服务提供商
    """
    if not REPLICATE_API_TOKEN:
        return {
            'status': 'error',
            'message': 'AI服务未配置。请设置 REPLICATE_API_TOKEN 环境变量'
        }

    try:
        # 预处理图片
        enhanced_image = process_image(image_path, motion_mode, duration)

        # 根据运动模式设置提示词
        prompts = {
            'breathing': 'gentle breathing motion, subtle zoom in and out, natural, cinematic, smooth, realistic',
            'gentle-sway': 'gentle swaying motion, left to right, natural movement, cinematic, realistic',
            'smile': 'warm smile appearing, gentle brightness changes, emotional, nostalgic, realistic',
            'memory-flow': 'slow zoom in, fading to warm tones, nostalgic, emotional, cinematic, realistic'
        }

        prompt = prompts.get(motion_mode, prompts['breathing'])

        # 使用Replicate API
        import replicate
        os.environ['REPLICATE_API_TOKEN'] = REPLICATE_API_TOKEN

        # Zeroscope v2 模型 - 高质量视频生成
        output = replicate.run(
            "anotherjesse/zeroscope-v2-xl:71996d331e84d5991e7e2f8ec34c220b892a51139c5b1c3b8e4b8e3a8f6e8d3c",
            input={
                "prompt": prompt,
                "negative_prompt": "blur, low quality, distorted, ugly, artificial, cartoon",
                "duration": duration,
                "fps": 30,
                "guidance_scale": 7.5,
                "image": open(enhanced_image, 'rb')
            }
        )

        return {
            'status': 'success',
            'video_url': output,
            'model': 'Zeroscope v2'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def generate_simple_video(image_path, motion_mode='breathing', duration=5, style='natural'):
    """
    简单视频生成（无需AI服务）
    使用基础图像动画
    """
    try:
        from PIL import Image, ImageDraw, ImageFilter
        import math

        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 调整尺寸
        max_size = 720
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        frames = []
        total_frames = duration * 30  # 30fps

        for i in range(total_frames):
            progress = i / total_frames

            if motion_mode == 'breathing':
                scale = 1 + math.sin(progress * math.pi * 4) * 0.025
                brightness = 1 + math.sin(progress * math.pi * 2) * 0.06
            elif motion_mode == 'gentle-sway':
                offset_x = math.sin(progress * math.pi * 3) * 15
                scale = 1 + math.sin(progress * math.pi * 2) * 0.015
            elif motion_mode == 'smile':
                scale = 1 + math.sin(progress * math.pi * 2) * 0.02
                brightness = 1 + math.sin(progress * math.pi * 4) * 0.1
            else:  # memory-flow
                scale = 1 + progress * 0.15
                brightness = 1 - progress * 0.2

            # 应用效果
            if style == 'warm-memory':
                img_copy = img.copy()
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Brightness(img_copy)
                img_copy = enhancer.enhance(brightness if brightness else 1.05)
            elif style == 'black-white':
                img_copy = img.copy().convert('L').convert('RGB')
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Brightness(img_copy)
                img_copy = enhancer.enhance(brightness if brightness else 1)
            else:
                img_copy = img.copy()

            # 保存帧
            from io import BytesIO
            buffer = BytesIO()
            img_copy.save(buffer, format='JPEG', quality=90)
            buffer.seek(0)
            frames.append(buffer.read())

        return {
            'status': 'success',
            'frames': frames,
            'total_frames': total_frames
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

@app.route('/')
def home():
    """首页"""
    return jsonify({
        'service': '时光重现 - AI视频生成服务',
        'version': '2.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'generate': '/api/generate',
            'status': '/api/status/<task_id>'
        }
    })

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': '时光重现 AI视频生成服务',
        'version': '2.0.0',
        'ai_configured': bool(REPLICATE_API_TOKEN),
        'features': {
            'ai_generation': bool(REPLICATE_API_TOKEN),
            'simple_generation': True
        }
    })

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """生成视频"""
    try:
        # 验证请求
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '没有上传图片'}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400

        # 验证文件类型
        allowed_types = {'image/jpeg', 'image/png', 'image/webp'}
        if file.content_type not in allowed_types:
            return jsonify({'success': False, 'error': '不支持的图片格式'}), 400

        # 检查文件大小
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)

        if size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': '文件大小超过20MB'}), 400

        # 保存上传的图片
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{file_ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # 获取参数
        motion_mode = request.form.get('motion_mode', 'breathing')
        duration = min(int(request.form.get('duration', 5)), 10)
        style = request.form.get('style', 'natural')

        # 生成视频
        if REPLICATE_API_TOKEN:
            # 使用AI生成
            result = generate_video_with_ai(filepath, motion_mode, duration)

            if result['status'] == 'success':
                return jsonify({
                    'success': True,
                    'video_url': result['video_url'],
                    'model': result['model'],
                    'generation_mode': 'ai'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('message', 'AI生成失败')
                }), 500
        else:
            # 使用简单生成
            result = generate_simple_video(filepath, motion_mode, duration, style)

            if result['status'] == 'success':
                # 保存为GIF（简单模式）
                task_id = uuid.uuid4()
                gif_path = os.path.join(OUTPUT_FOLDER, f"{task_id}.gif")

                frames = []
                for frame_data in result['frames'][::3]:  # 每3帧取1帧
                    from io import BytesIO
                    buffer = BytesIO(frame_data)
                    frames.append(Image.open(buffer))

                if frames:
                    frames[0].save(
                        gif_path,
                        save_all=True,
                        append_images=frames[1:],
                        duration=int(1000/30*3),
                        loop=0
                    )

                return jsonify({
                    'success': True,
                    'video_url': f"/api/download/{task_id}.gif",
                    'generation_mode': 'simple',
                    'format': 'gif'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('message', '生成失败')
                }), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_video(filename):
    """下载生成的视频"""
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': '文件不存在'}), 404

@app.route('/api/models')
def list_models():
    """可用的AI模型"""
    models = [
        {
            'id': 'zeroscope-v2',
            'name': 'Zeroscope v2',
            'description': '高质量视频生成模型，支持多种运动模式',
            'requires_gpu': True,
            'cost': 'medium'
        },
        {
            'id': 'animatediff',
            'name': 'AnimateDiff',
            'description': '专业的图像动画化模型',
            'requires_gpu': True,
            'cost': 'medium'
        }
    ]

    return jsonify({
        'models': models,
        'ai_configured': bool(REPLICATE_API_TOKEN)
    })

# 如果是主程序，运行服务器
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
