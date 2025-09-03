
from google.cloud import storage
from google.oauth2 import service_account
import uuid
import os
import json

BUCKET_NAME = "patelalaperola_imagenes"

def upload_file_to_gcs(file_bytes: bytes, filename: str) -> str:
    try:
        # Leer credenciales desde variable de entorno
        credentials_info = json.loads(os.environ["google_application_credentials_json"])
        credentials = service_account.Credentials.from_service_account_info(credentials_info)

        # Crear cliente de GCS con credenciales explícitas
        client = storage.Client(credentials=credentials, project=credentials_info["project_id"])
        bucket = client.bucket(BUCKET_NAME)

        # Generar nombre único para el archivo
        unique_filename = f"{uuid.uuid4()}_{filename}"

        # Subir archivo
        blob = bucket.blob(unique_filename)
        blob.upload_from_string(file_bytes)

        # Retornar URL pública (asumiendo permisos públicos en el bucket)
        return f"https://storage.googleapis.com/{BUCKET_NAME}/{unique_filename}"

    except Exception as e:
        # Manejo de error bonito
        print(f"Error subiendo archivo a GCS: {e}")
        raise RuntimeError("No se pudo subir la imagen. Revisa la configuración del bucket y las credenciales.")


