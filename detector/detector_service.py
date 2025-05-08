#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的车牌检测与可视化脚本

功能：
  - Roboflow 云端/本地模型推理
  - EasyOCR 文字识别
  - 阿里云 OSS 图像上传
  - 禁停区判定上报
  - 支持单张图片和视频检测
  - 实时结果可视化

使用说明：
  1. 将待检测的图片和视频文件放在与本脚本相同目录，或通过绝对路径引用。
     推荐目录结构示例：
       detector_service.py
       images/
         └─ test1.jpg
         └─ license_plate.png
       videos/
         └─ video1.mp4
  2. 设置环境变量：
       export MODEL_ID="<namespace/project/version>"
       export ROBOFLOW_API_KEY="<你的API_KEY>"
       export OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, OSS_ENDPOINT, OSS_BUCKET_NAME
  3. 运行：
       python detector_service.py --image images/frame4.jpg
       python detector_service.py --video videos/video1.mp4
"""
import os
import time
import uuid
import queue
import logging
import argparse
from datetime import datetime, timezone

import cv2
import requests
import oss2
import easyocr
from shapely.geometry import Point, Polygon
from inference import get_model

# —— 日志配置 ——
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# —— OSS 配置 ——
OSS_ACCESS_KEY_ID     = os.getenv('OSS_ACCESS_KEY_ID')
OSS_ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET')
OSS_ENDPOINT          = os.getenv('OSS_ENDPOINT')
OSS_BUCKET_NAME       = os.getenv('OSS_BUCKET_NAME')
OSS_IMAGE_FOLDER      = os.getenv('OSS_IMAGE_FOLDER', 'captures/')

auth   = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

def upload_bytes_to_oss(image_bytes: bytes, ext='jpg') -> str:
    """上传字节到 OSS，返回 URL。"""
    object_name = f"{OSS_IMAGE_FOLDER}{uuid.uuid4().hex}.{ext}"
    bucket.put_object(object_name, image_bytes)
    return f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}/{object_name}"

# —— 禁停区读取 ——
ZONES_API = os.getenv('ZONES_API', 'http://localhost:5000/api/zones')
polygons = {}
try:
    zones = requests.get(ZONES_API, timeout=5).json()
    polygons = {z['id']: Polygon(z['path']) for z in zones}
    logger.info(f"Loaded {len(polygons)} zones from {ZONES_API}")
except Exception:
    logger.exception("Failed fetch zones, using empty polygon list")

# —— 模型加载 ——
MODEL_ID = os.getenv('MODEL_ID', 'motorcycle-lp/5')
API_KEY  = os.getenv('ROBOFLOW_API_KEY')
try:
    model = get_model(model_id=MODEL_ID, api_key=API_KEY)
    logger.info("Detection model loaded successfully")
except Exception:
    logger.exception("Model load failed, exiting.")
    raise

# —— OCR 初始化 ——
reader = easyocr.Reader(['en'], gpu=False)
logger.info("OCR engine initialized")

# —— 上报配置 ——
VIOLATION_API = os.getenv('VIOLATION_API', 'http://localhost:5000/api/violations')
CAMERA_ID     = int(os.getenv('CAMERA_ID', '1'))
report_queue = queue.Queue()

def iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

def pixel_to_geo(x: int, y: int):
    return float(x), float(y)

def safe_report(payload: dict):
    try:
        r = requests.post(VIOLATION_API, json=payload, timeout=5)
        r.raise_for_status()
    except Exception:
        report_queue.put((payload, time.time()))

def retry_reports(max_age=60):
    size = report_queue.qsize()
    for _ in range(size):
        payload, t0 = report_queue.get()
        if time.time() - t0 < max_age:
            safe_report(payload)

# —— 单张图片检测 ——
def detect_image(image_path: str,
                 confidence=0.25, iou_threshold=0.4,
                 display=True):
    """对单张图片做检测并可视化。"""
    frame = cv2.imread(image_path)
    if frame is None:
        logger.error(f"Cannot read image: {image_path}")
        return
    res = model.infer(frame, confidence=confidence, iou_threshold=iou_threshold)[0]
    preds = getattr(res, 'predictions', []) or []
    for p in preds:
        x1 = int(p.x - p.width/2)
        y1 = int(p.y - p.height/2)
        x2 = int(p.x + p.width/2)
        y2 = int(p.y + p.height/2)
        label = f"{p.class_name} {p.confidence:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(frame, (x1, y1-th-4), (x1+tw, y1), (255,255,255), -1)
        cv2.putText(frame, label, (x1, y1-4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    if display:
        cv2.imshow("Image Detections", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return preds

# —— 视频检测 ——
def run(video_path: str='video1.mp4', frame_step: int=5,
        confidence: float=0.25, iou_threshold: float=0.4,
        display: bool=True):
    """对视频文件做逐帧检测并可视化。"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        return
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    logger.info(f"Video opened: {fps:.2f} FPS, {total} frames")
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        idx += 1
        if idx % frame_step != 0:
            continue
        res = model.infer(frame, confidence=confidence, iou_threshold=iou_threshold)[0]
        preds = getattr(res, 'predictions', []) or []
        for p in preds:
            x1 = int(p.x - p.width/2)
            y1 = int(p.y - p.height/2)
            x2 = int(p.x + p.width/2)
            y2 = int(p.y + p.height/2)
            label = f"{p.class_name} {p.confidence:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(frame, (x1, y1-th-4), (x1+tw, y1), (255,255,255), -1)
            cv2.putText(frame, label, (x1, y1-4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
        if display:
            cv2.imshow("Video Detections", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        retry_reports()
    cap.release()
    if display:
        cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', help='Path to image for detection')
    parser.add_argument('--video', help='Path to video for detection')
    args = parser.parse_args()
    if args.image:
        detect_image(args.image)
    elif args.video:
        run(video_path=args.video)
    else:
        print("请通过 --image 或 --video 参数指定输入文件。 示例: python detector_service.py --image images/test.jpg")

