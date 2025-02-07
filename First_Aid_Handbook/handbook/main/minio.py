from minio import Minio
from django.conf import settings
from rest_framework.response import Response
from django.core.files.uploadedfile import InMemoryUploadedFile
from.models import Help




def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('miniolab1', image_name, file_object, file_object.size)
        return f"http://localhost:9000/minilab1/image/{image_name}"
    except Exception as e:
        return {"error": str(e)}
def add_pic(new_help, pic):
    client = Minio(
        enpoint=settings.AWS_S3_ENDPOINT_URL,
        acess=settings.AWS_S3_ACCESS_KEY_ID,
        secret=settings.AWS_S3_SECRET_ACCESS_KEY,
        secure=settings.AWS_S3_USE_SSL
    )
    i=new_help.id
    img_obj_name = f"{i}.png"
    if not pic:
        return Response({"errors": "Нет файла для изображения"})
    result = process_file_upload(pic, client, img_obf_name)
    if "error" in result:
        return Response({"errors": result["error"]})
    new_help.image = result["url"]
    new_help.save()
    return Response({"success": "Изображение загружено"})