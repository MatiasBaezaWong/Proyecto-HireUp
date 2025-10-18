from supabase import create_client
import os

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def upload_cv(file, filename):
    bucket = os.environ.get("SUPABASE_BUCKET", "cvs")
    
    # Leer contenido del archivo
    file_content = file.read()
    file.seek(0)

    # Subir archivo
    supabase.storage.from_(bucket).upload(filename, file_content, {"upsert": "true"})
    
    # Obtener URL pública
    public_url = supabase.storage.from_(bucket).get_public_url(filename)
    return public_url
