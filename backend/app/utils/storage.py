import boto3
from botocore.client import Config
import os
import uuid
from typing import Optional
from datetime import datetime

# MinIO/S3 Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "ai-hr-interview")
MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", "false").lower() == "true"

# Initialize MinIO client
s3_client = boto3.client(
    's3',
    endpoint_url=f"{'https' if MINIO_USE_SSL else 'http'}://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

def ensure_bucket_exists():
    """Create bucket if it doesn't exist"""
    try:
        s3_client.head_bucket(Bucket=MINIO_BUCKET)
    except:
        try:
            s3_client.create_bucket(Bucket=MINIO_BUCKET)
            print(f"Created MinIO bucket: {MINIO_BUCKET}")
        except Exception as e:
            print(f"Error creating bucket: {e}")

async def save_file_to_storage(
    file_content: bytes,
    original_filename: str,
    file_type: str,
    session_id: Optional[str] = None
) -> str:
    """
    Save file to MinIO storage
    
    Args:
        file_content: Raw file bytes
        original_filename: Original filename
        file_type: Type category (jd, resume, audio, video)
        session_id: Optional session ID for organization
    
    Returns:
        Storage path/key for the saved file
    """
    
    ensure_bucket_exists()
    
    # Generate unique filename
    file_extension = os.path.splitext(original_filename)[1]
    unique_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    if session_id:
        storage_key = f"{file_type}/{session_id}/{timestamp}_{unique_id}{file_extension}"
    else:
        storage_key = f"{file_type}/{timestamp}_{unique_id}{file_extension}"
    
    try:
        # Upload to MinIO
        s3_client.put_object(
            Bucket=MINIO_BUCKET,
            Key=storage_key,
            Body=file_content,
            ContentType=get_content_type(file_extension),
            Metadata={
                'original_filename': original_filename,
                'file_type': file_type,
                'upload_timestamp': timestamp
            }
        )
        
        return storage_key
        
    except Exception as e:
        raise Exception(f"Failed to save file to storage: {str(e)}")

async def get_file_from_storage(storage_key: str) -> bytes:
    """Retrieve file content from MinIO storage"""
    
    try:
        response = s3_client.get_object(Bucket=MINIO_BUCKET, Key=storage_key)
        return response['Body'].read()
        
    except Exception as e:
        raise Exception(f"Failed to retrieve file from storage: {str(e)}")

async def get_file_url(storage_key: str, expires_in: int = 3600) -> str:
    """Generate presigned URL for file access"""
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': MINIO_BUCKET, 'Key': storage_key},
            ExpiresIn=expires_in
        )
        return url
        
    except Exception as e:
        raise Exception(f"Failed to generate file URL: {str(e)}")

async def delete_file_from_storage(storage_key: str) -> bool:
    """Delete file from MinIO storage"""
    
    try:
        s3_client.delete_object(Bucket=MINIO_BUCKET, Key=storage_key)
        return True
        
    except Exception as e:
        print(f"Error deleting file {storage_key}: {e}")
        return False

def get_content_type(file_extension: str) -> str:
    """Get MIME type for file extension"""
    
    content_types = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc': 'application/msword',
        '.txt': 'text/plain',
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.m4a': 'audio/mp4',
        '.webm': 'audio/webm',
        '.ogg': 'audio/ogg',
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo'
    }
    
    return content_types.get(file_extension.lower(), 'application/octet-stream')

def list_files_by_session(session_id: str, file_type: Optional[str] = None) -> list:
    """List all files for a session"""
    
    try:
        prefix = f"{file_type}/{session_id}/" if file_type else f"session_{session_id}/"
        
        response = s3_client.list_objects_v2(
            Bucket=MINIO_BUCKET,
            Prefix=prefix
        )
        
        files = []
        for obj in response.get('Contents', []):
            files.append({
                'key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat(),
                'metadata': get_file_metadata(obj['Key'])
            })
        
        return files
        
    except Exception as e:
        print(f"Error listing files for session {session_id}: {e}")
        return []

def get_file_metadata(storage_key: str) -> dict:
    """Get file metadata from MinIO"""
    
    try:
        response = s3_client.head_object(Bucket=MINIO_BUCKET, Key=storage_key)
        return response.get('Metadata', {})
        
    except Exception as e:
        print(f"Error getting metadata for {storage_key}: {e}")
        return {}

# Initialize bucket on module import
try:
    ensure_bucket_exists()
except Exception as e:
    print(f"Warning: Could not initialize MinIO bucket: {e}")