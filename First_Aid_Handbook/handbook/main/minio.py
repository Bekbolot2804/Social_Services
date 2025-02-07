# main/minio.py

from minio import Minio
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import Help


def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('miniolab1', image_name, file_object, file_object.size)
        return f"http://localhost:9000/miniolab1/{image_name}"
    except Exception as e:
        return {"error": str(e)}


def add_pic(new_help, pic):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.EMAIL_USE_SSL
    )
    img_obj_name = f"{new_help.id}.png"

    if not pic:
        return {"error": "Нет файла для изображения"}

    result = process_file_upload(pic, client, img_obj_name)
    if isinstance(result, dict) and "error" in result:
        return result

    # Обновляем поле image объекта Help
    new_help.image = result
    new_help.save()
    return {"success": "Изображение загружено"}