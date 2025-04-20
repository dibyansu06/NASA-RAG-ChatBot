from celery import shared_task
import os
import shutil
from .models import UploadedDocument

@shared_task
def delete_uploaded_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    
    try:
        doc = UploadedDocument.objects.get(file=file_path.replace("media/", ""))

        user_id = doc.user.id
        file_name = os.path.splitext(os.path_basename(file_path))[0]
        index_path = f"vectorestores/user_{user_id}/{file_name}_index"
        if os.path.exists(index_path):
            shutil.rmtree(index_path)

        doc.delete()
    except UploadedDocument.DoesNotExist:
        pass