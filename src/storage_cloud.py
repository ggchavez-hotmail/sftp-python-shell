import os
import tempfile
from google.cloud import storage

SERVICE_ACCOUNT = os.getenv('SERVICE_ACCOUNT')
    
def download(file_path_local, file_path_cloud, bucket_name):
    try:
        ABSOLUTE_PATH = os.path.abspath(SERVICE_ACCOUNT)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ABSOLUTE_PATH #SERVICE_ACCOUNT
        print("INFO", f"file_path_local... {file_path_local}")
        print("INFO", f"file_path_cloud... {file_path_cloud}")
        print("INFO", f"bucket_name... {bucket_name}")
        
        storage_client = storage.Client()

        # Obtiene el bucket
        bucket = storage_client.bucket(bucket_name)

        # Sube el archivo al bucket
        blob = bucket.blob(file_path_cloud)
        blob.download_to_filename(file_path_local)
        
        print("INFO", f"Archivo {file_path_cloud} descargado de {blob.public_url}")
        return True
    except Exception as e:
        print("GCLOUD - ERROR", e)
        return False

# upload_bucket("prueba", os.path.join(file_path, "vida.docx"), "vida-devolucion")
def upload(file_path_local, file_path_cloud, bucket_name):
    try:
        
        ABSOLUTE_PATH = os.path.abspath(SERVICE_ACCOUNT)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ABSOLUTE_PATH #SERVICE_ACCOUNT
        print("INFO", f"file_path_local... {file_path_local}")
        print("INFO", f"file_path_cloud... {file_path_cloud}")
        print("INFO", f"bucket_name... {bucket_name}")
        
        storage_client = storage.Client()

        # Obtiene el bucket
        bucket = storage_client.bucket(bucket_name)

        # Sube el archivo al bucket
        blob = bucket.blob(file_path_cloud)
        blob.upload_from_filename(file_path_local)
        
        print("INFO", f"Archivo {file_path_local} subido a {blob.public_url}")
        return True

    except Exception as e:
        print("GCLOUD - ERROR", f"Error en la carga a Cloud Storage: {e}")
        return False