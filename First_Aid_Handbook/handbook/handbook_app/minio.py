from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile

def deleteImg(url):
    client = Minio(
            endpoint = '127.0.0.1:9000',
            access_key = 'minioadmin',
            secret_key = 'minioadmin',
            secure = False
        )
    if url == '':
        return 'success'
    try:
        url_parts = url.split('/')
        bucket_name = url_parts[3]
        img_name = url_parts[4]
    except:
        return 'error'

    try:
        client.remove_object(bucket_name, img_name)
        return 'success'
    except:
        return 'error'
    
def addImg(img):
    client = Minio(
        endpoint = '127.0.0.1:9000',
        access_key = 'minioadmin',
        secret_key = 'minioadmin',
        secure = False
    )

    client.put_object(
        'miniolab1',
        f'{img.name}',
        img,
        img.size
    )
    return f'http://127.0.0.1:9000/miniolab1/{img.name}'