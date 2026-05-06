"""
时光重现 - 专业AI视频生成后端服务
使用Replicate API进行真实的AI视频生成
"""

import os
import uuid
import base64
from io import BytesIO
from PIL import Image
import requests
import replicate
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Replicate API Token (需要设置环境变量)
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')

def enhance_image_for_animation(image_path):
    """
    预处理图片，增强适合动画化的特征
    """
    try:
        img = Image.open(image_path)

        # 确保RGB模式
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 调整尺寸（Replicate模型通常需要较小尺寸）
        max_size = 1024
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # 保存处理后的图片
        enhanced_path = image_path.replace('.', '_enhanced.')
        img.save(enhanced_path, quality=95)

        return enhanced_path
    except Exception as e:
        print(f"图片预处理失败: {e}")
        return image_path

def generate_video_with_replicate(image_path, motion_mode='breathing', duration=5):
    """
    使用Replicate的AI模型生成视频

    可用的模型：
    1. Zeroscope v2 - 快速生成，适合演示
    2. AnimateDiff - 专业的图像动画化模型
    3. models - 更高质量的生成模型
    """
    try:
        # 预处理图片
        enhanced_image = enhance_image_for_animation(image_path)

        # 根据运动模式设置提示词
        prompts = {
            'breathing': 'gentle breathing motion, subtle zoom in and out, natural, cinematic, smooth',
            'gentle-sway': 'gentle swaying motion, left to right, natural movement, cinematic',
            'smile': 'warm smile appearing, gentle brightness changes, emotional, nostalgic',
            'memory-flow': 'slow zoom in, fading to warm tones, nostalgic, emotional, cinematic'
        }

        prompt = prompts.get(motion_mode, 'gentle breathing motion, natural, cinematic')

        # 使用Zeroscope模型生成视频
        # 注意：这是示例，实际使用时需要有效的API token
        if REPLICATE_API_TOKEN:
            # 初始化Replicate客户端
            os.environ['REPLICATE_API_TOKEN'] = REPLICATE_API_TOKEN

            # 使用Zeroscope模型
            output = replicate.run(
                "anotherjesse/zeroscope-v2-xl:71996d331e84d5991e7e2f8ec34c220b892a51139c5b1c3b8e4b8e3a8f6e8d3c",
                input={
                    "prompt": prompt,
                    "negative_prompt": "blur, low quality, distorted, ugly",
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
        else:
            # 没有API token时返回错误提示
            return {
                'status': 'error',
                'message': '需要配置Replicate API Token。请设置环境变量 REPLICATE_API_TOKEN'
            }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def generate_video_with_alternative_api(image_path, motion_mode='breathing', duration=5):
    """
    使用替代API生成视频（如需要）
    可以集成：阿里云、腾讯云、其他视频生成API
    """
    # 这里可以添加其他API的集成代码
    pass

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """生成视频API"""
    try:
        # 验证请求
        if 'image' not in request.files:
            return jsonify({'error': '没有上传图片'}), 400

        file = request.files['image']

        # 验证文件
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        # 检查文件类型
        allowed_types = {'image/jpeg', 'image/png', 'image/webp'}
        if file.content_type not in allowed_types:
            return jsonify({'error': '不支持的图片格式'}), 400

        # 检查文件大小
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)

        if size > MAX_FILE_SIZE:
            return jsonify({'error': '文件大小超过20MB'}), 400

        # 保存上传的图片
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{file_ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # 获取参数
        motion_mode = request.form.get('motion_mode', 'breathing')
        duration = int(request.form.get('duration', 5))
        style = request.form.get('style', 'natural')

        # 生成视频
        result = generate_video_with_replicate(filepath, motion_mode, duration)

        if result['status'] == 'success':
            return jsonify({
                'success': True,
                'video_url': result['video_url'],
                'model': result.get('model', 'Unknown')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', '生成失败')
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced-generate', methods=['POST'])
def advanced_generate():
    """
    高级视频生成API
    支持更多参数和自定义设置
    """
    try:
        data = request.get_json()

        if not data or 'image_base64' not in data:
            return jsonify({'error': '需要提供base64编码的图片'}), 400

        # 解码图片
        image_data = base64.b64decode(data['image_base64'])
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, 'wb') as f:
            f.write(image_data)

        # 获取参数
        motion_mode = data.get('motion_mode', 'breathing')
        duration = data.get('duration', 5)
        style = data.get('style', 'natural')
        quality = data.get('quality', 'high')
        custom_prompt = data.get('custom_prompt', None)

        # 生成视频
        result = generate_video_with_replicate(filepath, motion_mode, duration)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """查询任务状态"""
    # 实际应用中应该查询数据库或缓存
    return jsonify({
        'task_id': task_id,
        'status': 'completed',
        'progress': 100
    })

@app.route('/api/models', methods=['GET'])
def list_models():
    """列出可用的AI模型"""
    models = [
        {
            'id': 'zeroscope-v2',
            'name': 'Zeroscope v2',
            'description': '高质量视频生成模型，支持多种运动模式',
            'supports_duration': [3, 5, 10],
            'max_resolution': '1024x1024'
        },
        {
            'id': 'animatediff',
            'name': 'AnimateDiff',
            'description': '专业的图像动画化模型，生成自然流畅的动画',
            'supports_duration': [2, 4, 8],
            'max_resolution': '512x512'
        }
    ]

    return jsonify({'models': models})

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': '时光重现 AI视频生成服务',
        'version': '2.0.0',
        'replicate_configured': bool(REPLICATE_API_TOKEN)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
