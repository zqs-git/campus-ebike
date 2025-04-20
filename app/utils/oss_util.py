import oss2
import uuid
from flask import current_app

def upload_to_oss(file):
    config = current_app.config
    auth = oss2.Auth(config['OSS_ACCESS_KEY_ID'], config['OSS_ACCESS_KEY_SECRET'])
    bucket = oss2.Bucket(auth, config['OSS_ENDPOINT'], config['OSS_BUCKET_NAME'])

    ext = file.filename.rsplit('.', 1)[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    object_name = config['OSS_IMAGE_FOLDER'] + filename

    print("🚀 开始上传到 OSS")
    bucket.put_object(object_name, file.stream)  
    print("✅ 上传完成:", object_name)

    return f"https://{config['OSS_BUCKET_NAME']}.{config['OSS_ENDPOINT']}/{object_name}"
