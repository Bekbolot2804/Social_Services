from minio import Minio
from django.conf import settings

def upload_image(help_obj, image):
    client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_USE_SSL
    )
    
    bucket_name = "help-images"
    object_name = f"{help_obj.id}/{image.name}"
    
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    
    client.put_object(
        bucket_name,
        object_name,
        image,
        image.size,
        content_type=image.content_type
    )
    
    return f"{settings.MINIO_PUBLIC_URL}/{bucket_name}/{object_name}"