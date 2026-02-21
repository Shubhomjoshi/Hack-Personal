"""
Azure Storage Service - Handle file uploads to Azure Blob Storage
"""
import os
from azure.storage.blob import BlobServiceClient, ContentSettings
from typing import Optional
import uuid
class AzureStorageService:
    def __init__(self, connection_string: str, container_name: str):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = None
        if connection_string:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                # Create container if it doesn't exist
                try:
                    self.blob_service_client.create_container(container_name)
                except Exception:
                    pass  # Container already exists
            except Exception as e:
                print(f""Warning: Could not initialize Azure Storage: {e}"")
    def upload_file(self, file_path: str, blob_name: Optional[str] = None) -> Optional[str]:
        """"""Upload file to Azure Blob Storage""""""
        if not self.blob_service_client:
            return None
        try:
            if not blob_name:
                file_ext = os.path.splitext(file_path)[1]
                blob_name = f""{uuid.uuid4()}{file_ext}""
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            # Set content type
            content_type = self._get_content_type(file_path)
            content_settings = ContentSettings(content_type=content_type)
            # Upload file
            with open(file_path, ""rb"") as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    content_settings=content_settings
                )
            # Return blob URL
            return blob_client.url
        except Exception as e:
            print(f""Error uploading to Azure Storage: {e}"")
            return None
    def download_file(self, blob_name: str, download_path: str) -> bool:
        """"""Download file from Azure Blob Storage""""""
        if not self.blob_service_client:
            return False
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            with open(download_path, ""wb"") as file:
                blob_data = blob_client.download_blob()
                file.write(blob_data.readall())
            return True
        except Exception as e:
            print(f""Error downloading from Azure Storage: {e}"")
            return False
    def delete_file(self, blob_name: str) -> bool:
        """"""Delete file from Azure Blob Storage""""""
        if not self.blob_service_client:
            return False
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            return True
        except Exception as e:
            print(f""Error deleting from Azure Storage: {e}"")
            return False
    def _get_content_type(self, file_path: str) -> str:
        """"""Get MIME type for file""""""
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.tiff': 'image/tiff',
        }
        return content_types.get(ext, 'application/octet-stream')
# Singleton instance
_azure_storage_service: Optional[AzureStorageService] = None
def get_azure_storage_service() -> Optional[AzureStorageService]:
    """"""Get or create Azure Storage Service instance""""""
    global _azure_storage_service
    if _azure_storage_service is None:
        from azure_config import azure_config
        if azure_config.use_azure_storage():
            _azure_storage_service = AzureStorageService(
                azure_config.AZURE_STORAGE_CONNECTION_STRING,
                azure_config.AZURE_STORAGE_CONTAINER_NAME
            )
    return _azure_storage_service
