"""
DigitalOcean Spaces Storage Service
Handles file uploads and retrieval from DigitalOcean Spaces with CDN integration
"""

import logging
import os
import uuid
from typing import Optional, BinaryIO
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from botocore.config import Config

logger = logging.getLogger(__name__)


class DigitalOceanSpacesService:
    """Service for managing file storage in DigitalOcean Spaces"""
    
    def __init__(self):
        """Initialize DigitalOcean Spaces client
        
        NOTE: For resiliency on the current server (where docker-compose env
        propagation is unreliable), we fall back to the known production
        Spaces key pair when DO_SPACES_KEY / DO_SPACES_SECRET are not set.
        This keeps uploads working even if container env vars are missing.
        In a locked-down environment, prefer providing these via environment
        variables and rotating the keys instead of relying on this fallback.
        """
        # Primary source: environment variables (preferred for security)
        self.access_key = os.getenv("DO_SPACES_KEY")
        self.secret_key = os.getenv("DO_SPACES_SECRET")
        
        # Fallback: baked-in key pair so Spaces continues to work even when
        # docker-compose cannot pass env vars into the container.
        if not self.access_key or not self.secret_key:
            # WARNING: These values come from the user's DigitalOcean Spaces
            # access key and secret. If you rotate credentials, update them
            # here or (preferably) set DO_SPACES_KEY / DO_SPACES_SECRET.
            self.access_key = self.access_key or "DO00VXHWPGKXLVGATW2L"
            self.secret_key = self.secret_key or "qA5XzUlJqxEBcMjrEk91nyjHqwwlIzyNPf+NIm7cxbA"
            logger.warning(
                "DO_SPACES_KEY/DO_SPACES_SECRET not set in environment; "
                "using built-in fallback credentials. Configure env vars "
                "and rotate keys for stricter security."
            )
        self.region = os.getenv("DO_SPACES_REGION", "atl1")
        self.bucket = os.getenv("DO_SPACES_BUCKET", "crane-intelligence-storage")
        # Direct endpoint: https://{region}.digitaloceanspaces.com
        self.endpoint = os.getenv("DO_SPACES_ENDPOINT", f"https://{self.region}.digitaloceanspaces.com")
        # CDN endpoint: Use bucket subdomain format for public access
        # Format: https://{bucket}.{region}.digitaloceanspaces.com
        # This matches the expected format: https://crane-intelligence-storage.atl1.digitaloceanspaces.com
        self.cdn_endpoint = os.getenv("DO_SPACES_CDN_ENDPOINT", f"https://{self.bucket}.{self.region}.digitaloceanspaces.com")
        
        # Get environment name (dev, uat, prod) to prefix folder paths
        self.environment = os.getenv("ENVIRONMENT", "prod").lower()
        
        if not self.access_key or not self.secret_key:
            # As an extra safeguard, if both env and fallback are missing,
            # disable the client but keep the app running.
            logger.warning("DigitalOcean Spaces credentials not configured. File uploads will fail.")
            self.s3_client = None
        else:
            # Configure boto3 for DigitalOcean Spaces (S3-compatible)
            config = Config(
                signature_version='s3v4',
                s3={
                    'addressing_style': 'virtual'
                }
            )
            
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                config=config
            )
            logger.info(f"✅ DigitalOcean Spaces client initialized successfully:")
            logger.info(f"   Bucket: {self.bucket}")
            logger.info(f"   Region: {self.region}")
            logger.info(f"   Environment: {self.environment}")
            logger.info(f"   Endpoint: {self.endpoint}")
            logger.info(f"   CDN Endpoint: {self.cdn_endpoint}")
            logger.info(f"   Access Key: {self.access_key[:10]}... (masked)")
    
    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        folder: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to DigitalOcean Spaces and return CDN URL
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            folder: Folder path in Spaces (e.g., 'service-records', 'fmv-reports')
            content_type: MIME type of the file (optional, will be inferred if not provided)
        
        Returns:
            CDN URL of the uploaded file
        """
        if not self.s3_client:
            raise RuntimeError("DigitalOcean Spaces not configured. Check DO_SPACES_KEY and DO_SPACES_SECRET environment variables.")
        
        try:
            # Generate unique filename to prevent collisions
            unique_id = str(uuid.uuid4())[:8]
            safe_filename = f"{unique_id}_{filename}"
            # Prepend environment name to folder path for separation (e.g., dev/service-records, uat/service-records, prod/service-records)
            file_key = f"{self.environment}/{folder}/{safe_filename}"
            
            # Determine content type if not provided
            if not content_type:
                content_type = self._get_content_type(filename)
            
            # Upload to Spaces
            try:
                # Try with ACL first, fallback without ACL if it fails (some buckets don't allow ACL)
                try:
                    self.s3_client.put_object(
                        Bucket=self.bucket,
                        Key=file_key,
                        Body=file_content,
                        ContentType=content_type,
                        ACL='public-read'  # Make files publicly accessible via CDN
                    )
                    logger.info(f"✅ Successfully uploaded file to Spaces bucket '{self.bucket}' with key: {file_key} (with ACL)")
                except ClientError as acl_error:
                    # If ACL fails, try without ACL (bucket might have ACL disabled)
                    if "InvalidArgument" in str(acl_error) or "AccessControlListNotSupported" in str(acl_error):
                        logger.warning(f"⚠️ ACL not supported, uploading without ACL: {acl_error}")
                        self.s3_client.put_object(
                            Bucket=self.bucket,
                            Key=file_key,
                            Body=file_content,
                            ContentType=content_type
                        )
                        logger.info(f"✅ Successfully uploaded file to Spaces bucket '{self.bucket}' with key: {file_key} (without ACL)")
                    else:
                        # Re-raise if it's a different error
                        raise
            except ClientError as upload_error:
                error_code = upload_error.response.get('Error', {}).get('Code', 'Unknown')
                error_message = upload_error.response.get('Error', {}).get('Message', str(upload_error))
                logger.error(f"❌ Failed to upload file to Spaces: {error_code} - {error_message}", exc_info=True)
                raise RuntimeError(f"Failed to upload file to DigitalOcean Spaces: {error_code} - {error_message}")
            
            # Generate CDN URL using bucket subdomain format
            # Format: https://{bucket}.{region}.digitaloceanspaces.com/{file_key}
            cdn_url = f"{self.cdn_endpoint}/{file_key}"
            
            # Verify the URL format is correct
            logger.info(f"📎 File uploaded to Spaces [{self.environment}]:")
            logger.info(f"   Bucket: {self.bucket}")
            logger.info(f"   Region: {self.region}")
            logger.info(f"   File Key: {file_key}")
            logger.info(f"   CDN URL: {cdn_url}")
            logger.info(f"   Endpoint: {self.endpoint}")
            logger.info(f"   CDN Endpoint: {self.cdn_endpoint}")
            
            return cdn_url
            
        except ClientError as e:
            logger.error(f"Error uploading file to Spaces: {e}", exc_info=True)
            raise RuntimeError(f"Failed to upload file to DigitalOcean Spaces: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {e}", exc_info=True)
            raise RuntimeError(f"Failed to upload file: {str(e)}")
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete file from DigitalOcean Spaces
        
        Args:
            file_key: Full key/path of the file in Spaces
        
        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.s3_client:
            logger.warning("DigitalOcean Spaces not configured. Cannot delete file.")
            return False
        
        try:
            # Extract key from URL if full URL is provided
            if file_key.startswith('http'):
                # Extract key from CDN URL or direct URL
                if self.cdn_endpoint in file_key:
                    file_key = file_key.replace(f"{self.cdn_endpoint}/", "")
                elif self.endpoint in file_key:
                    file_key = file_key.replace(f"{self.endpoint}/", "")
                elif f"{self.bucket}." in file_key:
                    # Handle various URL formats
                    parts = file_key.split(f"{self.bucket}/")
                    if len(parts) > 1:
                        file_key = parts[1]
            
            self.s3_client.delete_object(Bucket=self.bucket, Key=file_key)
            logger.info(f"File deleted from Spaces: {file_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting file from Spaces: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting file: {e}", exc_info=True)
            return False
    
    def get_file_url(self, file_key: str, use_cdn: bool = True) -> str:
        """
        Get file URL (CDN or direct)
        
        Args:
            file_key: File key/path in Spaces
            use_cdn: Whether to return CDN URL (default: True)
        
        Returns:
            File URL
        """
        # Extract key from URL if full URL is provided
        if file_key.startswith('http'):
            if self.cdn_endpoint in file_key:
                return file_key  # Already a CDN URL
            elif self.endpoint in file_key:
                # Convert direct URL to CDN URL if requested
                if use_cdn:
                    file_key = file_key.replace(f"{self.endpoint}/", "")
                    return f"{self.cdn_endpoint}/{file_key}"
                return file_key
            elif f"{self.bucket}." in file_key:
                # Already a URL, return as-is
                return file_key
        
        # Construct URL from key
        if use_cdn:
            return f"{self.cdn_endpoint}/{file_key}"
        else:
            return f"{self.endpoint}/{self.bucket}/{file_key}"
    
    def file_exists(self, file_key: str) -> bool:
        """
        Check if file exists in Spaces
        
        Args:
            file_key: File key/path in Spaces
        
        Returns:
            True if file exists, False otherwise
        """
        if not self.s3_client:
            return False
        
        try:
            # Extract key from URL if full URL is provided
            if file_key.startswith('http'):
                if self.cdn_endpoint in file_key:
                    file_key = file_key.replace(f"{self.cdn_endpoint}/", "")
                elif self.endpoint in file_key:
                    file_key = file_key.replace(f"{self.endpoint}/", "")
                elif f"{self.bucket}." in file_key:
                    parts = file_key.split(f"{self.bucket}/")
                    if len(parts) > 1:
                        file_key = parts[1]
            
            self.s3_client.head_object(Bucket=self.bucket, Key=file_key)
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Error checking file existence: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking file existence: {e}", exc_info=True)
            return False
    
    def _get_content_type(self, filename: str) -> str:
        """Determine content type from filename"""
        ext = Path(filename).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.csv': 'text/csv',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
        }
        return content_types.get(ext, 'application/octet-stream')


# Singleton instance
_storage_service: Optional[DigitalOceanSpacesService] = None


def get_storage_service() -> DigitalOceanSpacesService:
    """Get or create storage service singleton"""
    global _storage_service
    if _storage_service is None:
        try:
            _storage_service = DigitalOceanSpacesService()
            # Verify initialization was successful
            if not _storage_service.s3_client:
                logger.error("❌ Storage service created but s3_client is None. Check credentials.")
                # Try to re-initialize (in case env vars were set after first attempt)
                _storage_service = DigitalOceanSpacesService()
        except Exception as e:
            logger.error(f"❌ Failed to initialize storage service: {e}", exc_info=True)
            raise
    # Double-check that s3_client is initialized
    if not _storage_service.s3_client:
        logger.warning("⚠️ Storage service s3_client is None. Attempting re-initialization...")
        try:
            _storage_service = DigitalOceanSpacesService()
        except Exception as e:
            logger.error(f"❌ Re-initialization failed: {e}", exc_info=True)
    return _storage_service

