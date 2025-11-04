"""
Service for managing OpenAI Vector Store operations
"""
import json
import tempfile
import os
import hashlib
from typing import List, Dict, Any, Set
from openai import OpenAI
from aws_lambda_powertools import Logger

from src.util.secrets_manager import get_openai_api_key

logger = Logger(child=True)


class VectorStoreService:
    """Service for uploading and managing data in OpenAI Vector Stores"""
    
    def __init__(self, vector_store_id: str | None = None):
        """
        Initialize the Vector Store Service
        
        Args:
            vector_store_id: Optional existing vector store ID. If not provided,
                           will look for OPENAI_VECTOR_STORE_ID environment variable
        """
        api_key = get_openai_api_key()
        self.client = OpenAI(api_key=api_key)
        
        # Get vector store ID from parameter or environment variable
        self.vector_store_id = vector_store_id or os.environ.get('OPENAI_VECTOR_STORE_ID')
        
        if not self.vector_store_id:
            logger.warning("No vector store ID provided. Will need to create or specify one.")
    
    def create_vector_store(self, name: str) -> str:
        """
        Create a new vector store
        
        Args:
            name: Name for the vector store
            
        Returns:
            The ID of the created vector store
        """
        logger.info(f"Creating new vector store: {name}")
        vector_store = self.client.vector_stores.create(name=name)
        self.vector_store_id = vector_store.id
        logger.info(f"Created vector store with ID: {self.vector_store_id}")
        return self.vector_store_id
    
    def _hash_degree_name(self, degree_name: str) -> str:
        """
        Create a hash from a degree name for consistent file naming
        
        Args:
            degree_name: The name of the degree
            
        Returns:
            A hash string to use as filename identifier
        """
        # Normalize the degree name (lowercase, strip whitespace)
        normalized_name = degree_name.strip().lower()
        # Create SHA256 hash and take first 16 characters for readability
        hash_object = hashlib.sha256(normalized_name.encode('utf-8'))
        return hash_object.hexdigest()[:16]
    
    def _get_existing_files_map(self) -> Dict[str, str]:
        """
        Get a mapping of degree name hashes to file IDs for existing files in the vector store
        
        Returns:
            Dictionary mapping degree name hashes to OpenAI file IDs
        """
        if not self.vector_store_id:
            raise ValueError("No vector store ID configured.")
        
        logger.info(f"Fetching existing files from vector store {self.vector_store_id}")
        existing_files = {}
        
        try:
            # List all files in the vector store
            files = self.client.vector_stores.files.list(
                vector_store_id=self.vector_store_id,
                limit=100  # Adjust as needed
            )
            
            # Build a map of filename hash to file_id
            for file in files.data:
                # Get the actual file object to access its filename
                try:
                    file_obj = self.client.files.retrieve(file.id)
                    filename = file_obj.filename
                    # Extract hash from filename (format: degree_<hash>.txt)
                    if filename.startswith('degree_') and filename.endswith('.txt'):
                        file_hash = filename[7:-4]  # Remove 'degree_' prefix and '.txt' suffix
                        existing_files[file_hash] = file.id
                except Exception as e:
                    logger.warning(f"Could not retrieve file info for {file.id}: {e}")
            
            logger.info(f"Found {len(existing_files)} existing files in vector store")
            return existing_files
            
        except Exception as e:
            logger.error(f"Error fetching existing files: {e}")
            return {}
    
    def upload_degree_data(self, degree_data: List[Dict[str, Any]], batch_size: int = 500) -> Dict[str, Any]:
        """
        Upload scraped degree data to the OpenAI vector store.
        Uses hashed degree names as filenames to enable update detection.
        If a file with the same hash exists, it will be deleted and replaced with new content.
        
        Args:
            degree_data: List of degree information dictionaries
            batch_size: Maximum number of files to upload per batch
            
        Returns:
            Dictionary with upload statistics
        """
        if not self.vector_store_id:
            raise ValueError("No vector store ID configured. Call create_vector_store() first.")
        
        logger.info(f"Uploading {len(degree_data)} degree records to vector store {self.vector_store_id}")
        
        # Get existing files to check for updates
        existing_files = self._get_existing_files_map()
        
        uploaded_files = []
        updated_files = []
        failed_uploads = []
        temp_files = []
        files_to_delete = []  # Track files that need to be deleted before re-upload
        
        try:
            # Create temporary files for each degree's data
            for idx, degree in enumerate(degree_data):
                try:
                    degree_name = degree.get('name', degree.get('scraped_degree_name', 'Unknown'))
                    degree_hash = self._hash_degree_name(degree_name)
                    
                    # Check if this degree already exists in the vector store
                    is_update = degree_hash in existing_files
                    if is_update:
                        logger.info(f"Degree '{degree_name}' already exists (hash: {degree_hash}), will update")
                        files_to_delete.append({
                            'file_id': existing_files[degree_hash],
                            'degree_name': degree_name,
                            'hash': degree_hash
                        })
                    
                    # Create a structured text document for each degree
                    content = self._format_degree_content(degree)
                    
                    # Create a temporary file with hash-based naming
                    temp_file = tempfile.NamedTemporaryFile(
                        mode='w',
                        suffix='.txt',
                        prefix=f"degree_{degree_hash}_",
                        delete=False,
                        encoding='utf-8'
                    )
                    temp_file.write(content)
                    temp_file.close()
                    temp_files.append({
                        'path': temp_file.name,
                        'degree_name': degree_name,
                        'degree_hash': degree_hash,
                        'is_update': is_update,
                        'degree': degree
                    })
                    
                except Exception as e:
                    logger.error(f"Error creating temp file for {degree.get('name', 'Unknown')}: {e}")
                    failed_uploads.append({
                        'degree': degree.get('name', 'Unknown'),
                        'error': str(e)
                    })
            
            # Delete old versions of files that need to be updated
            if files_to_delete:
                logger.info(f"Deleting {len(files_to_delete)} existing files before re-upload")
                for file_info in files_to_delete:
                    try:
                        self.client.vector_stores.files.delete(
                            vector_store_id=self.vector_store_id,
                            file_id=file_info['file_id']
                        )
                        logger.info(f"Deleted old version of {file_info['degree_name']} (file_id: {file_info['file_id']})")
                    except Exception as e:
                        logger.error(f"Error deleting file {file_info['file_id']}: {e}")
            
            # Upload files in batches
            for i in range(0, len(temp_files), batch_size):
                batch = temp_files[i:i + batch_size]
                logger.info(f"Uploading batch {i // batch_size + 1} ({len(batch)} files)")
                
                try:
                    # First, upload files to OpenAI's files API with proper filenames
                    file_ids = []
                    for temp_file_info in batch:
                        try:
                            # Create the filename with hash for identification
                            # Format: degree_<hash>.txt
                            filename = f"degree_{temp_file_info['degree_hash']}.txt"
                            
                            with open(temp_file_info['path'], 'rb') as file_stream:
                                # Upload with hash-based filename
                                # OpenAI expects a tuple of (filename, file_content, content_type)
                                file_obj = self.client.files.create(
                                    file=(filename, file_stream, 'text/plain'),
                                    purpose='assistants'
                                )
                                file_ids.append({
                                    'file_id': file_obj.id,
                                    'degree_name': temp_file_info['degree_name'],
                                    'is_update': temp_file_info['is_update']
                                })
                                logger.info(f"Uploaded file {file_obj.id} with filename {filename} for degree '{temp_file_info['degree_name']}'")
                        except Exception as e:
                            logger.error(f"Error uploading file {temp_file_info['degree_name']}: {e}")
                            failed_uploads.append({
                                'degree': temp_file_info['degree_name'],
                                'error': str(e)
                            })
                    
                    # Then add the uploaded files to the vector store
                    if file_ids:
                        for file_info in file_ids:
                            try:
                                self.client.vector_stores.files.create(
                                    vector_store_id=self.vector_store_id,
                                    file_id=file_info['file_id']
                                )
                                # Track successful uploads
                                if file_info['is_update']:
                                    updated_files.append(file_info['degree_name'])
                                else:
                                    uploaded_files.append(file_info['degree_name'])
                            except Exception as e:
                                logger.error(f"Error adding file {file_info['file_id']} to vector store: {e}")
                                failed_uploads.append({
                                    'degree': file_info['degree_name'],
                                    'error': str(e)
                                })
                    
                except Exception as e:
                    logger.error(f"Error processing batch: {e}")
                    for temp_file_info in batch:
                        if temp_file_info['degree_name'] not in [f['degree'] for f in failed_uploads]:
                            failed_uploads.append({
                                'degree': temp_file_info['degree_name'],
                                'error': str(e)
                            })
            
        finally:
            # Clean up temporary files
            for temp_file_info in temp_files:
                try:
                    os.unlink(temp_file_info['path'])
                except Exception as e:
                    logger.warning(f"Error deleting temp file {temp_file_info['path']}: {e}")
        
        result = {
            'vector_store_id': self.vector_store_id,
            'total_degrees': len(degree_data),
            'new_uploads': len(uploaded_files),
            'updated_files': len(updated_files),
            'successful_operations': len(uploaded_files) + len(updated_files),
            'failed_uploads': len(failed_uploads),
            'uploaded_files': uploaded_files,
            'updated_files_list': updated_files,
            'failures': failed_uploads
        }
        
        logger.info(f"Upload complete: {result['new_uploads']} new, {result['updated_files']} updated, {result['failed_uploads']} failed out of {result['total_degrees']} total")
        return result
    
    def _format_degree_content(self, degree: Dict[str, Any]) -> str:
        """
        Format degree information into a structured text document
        
        Args:
            degree: Dictionary containing degree information
            
        Returns:
            Formatted text content
        """
        lines = []
        
        # Add title/header
        degree_name = degree.get('name', degree.get('scraped_degree_name', 'Unknown Degree'))
        lines.append(f"# {degree_name}\n")
        
        # Add URL
        if 'url' in degree:
            lines.append(f"Source URL: {degree['url']}\n")
        elif 'scraped_url' in degree:
            lines.append(f"Source URL: {degree['scraped_url']}\n")
        
        lines.append("\n")
        
        # Add main content
        if 'content' in degree:
            lines.append("## Program Information\n")
            lines.append(f"{degree['content']}\n\n")
        
        # Add structured metadata
        lines.append("## Metadata\n")
        
        # Add all other fields as metadata
        metadata_fields = ['title', 'description', 'keywords', 'author', 
                          'language', 'sitename', 'date', 'categories', 
                          'tags', 'scraped_degree_name', 'scraped_url']
        
        for field in metadata_fields:
            if field in degree and degree[field]:
                value = degree[field]
                # Handle lists
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                lines.append(f"**{field.replace('_', ' ').title()}**: {value}\n")
        
        return '\n'.join(lines)
    
    def delete_all_files(self) -> Dict[str, Any]:
        """
        Delete all files from the vector store with pagination support
        
        Returns:
            Dictionary with deletion statistics
        """
        if not self.vector_store_id:
            raise ValueError("No vector store ID configured.")
        
        logger.info(f"Deleting all files from vector store {self.vector_store_id}")
        
        try:
            deleted_count = 0
            failed_count = 0
            after = None
            
            # Paginate through all files
            while True:
                # List files with pagination
                if after:
                    files = self.client.vector_stores.files.list(
                        vector_store_id=self.vector_store_id,
                        limit=100,
                        after=after
                    )
                else:
                    files = self.client.vector_stores.files.list(
                        vector_store_id=self.vector_store_id,
                        limit=100
                    )
                
                # Delete each file in the current page
                for file in files.data:
                    try:
                        self.client.vector_stores.files.delete(
                            vector_store_id=self.vector_store_id,
                            file_id=file.id
                        )
                        deleted_count += 1
                        logger.info(f"Deleted file: {file.id}")
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Error deleting file {file.id}: {e}")
                
                # Check if there are more pages
                if not files.has_more:
                    break
                    
                # Get the ID of the last file for pagination
                if files.data:
                    after = files.data[-1].id
                else:
                    break
            
            logger.info(f"Deleted {deleted_count} files from vector store (failed: {failed_count})")
            return {
                'vector_store_id': self.vector_store_id,
                'deleted_count': deleted_count,
                'failed_count': failed_count
            }
            
        except Exception as e:
            logger.error(f"Error deleting files: {e}")
            raise
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """
        Get information about the current vector store
        
        Returns:
            Dictionary with vector store information
        """
        if not self.vector_store_id:
            raise ValueError("No vector store ID configured.")
        
        try:
            vector_store = self.client.vector_stores.retrieve(self.vector_store_id)
            
            return {
                'id': vector_store.id,
                'name': vector_store.name,
                'file_counts': vector_store.file_counts.dict() if vector_store.file_counts else {},
                'status': vector_store.status,
                'created_at': vector_store.created_at
            }
        except Exception as e:
            logger.error(f"Error retrieving vector store info: {e}")
            raise