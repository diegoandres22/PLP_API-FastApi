
import logging
from google.cloud import storage
from google.oauth2 import service_account
import uuid
import os
import json

logger = logging.getLogger("patealaperola")

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

    except Exception:
        # Antes: print() en vez del logger del proyecto — no queda en el
        # mismo lugar que el resto de los logs de errores no controlados
        # (main.py usa logger.exception). Sigue subiendo como RuntimeError:
        # lo captura catch_unhandled_exceptions_middleware y responde 500
        # genérico, sin filtrar detalles de credenciales/bucket al cliente.
        logger.exception("Error subiendo archivo a GCS")
        raise RuntimeError("No se pudo subir la imagen. Revisa la configuración del bucket y las credenciales.")


