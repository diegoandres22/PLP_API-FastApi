from google.cloud import storage
import uuid

BUCKET_NAME = "patelalaperola_imagenes"

def upload_file_to_gcs(file_bytes: bytes, filename: str) -> str:
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    unique_filename = f"{uuid.uuid4()}_{filename}"

    blob = bucket.blob(unique_filename)
    blob.upload_from_string(file_bytes)

    # NO usar blob.make_public()

    # Retorna URL pública (asumiendo permisos públicos en bucket)
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{unique_filename}"
