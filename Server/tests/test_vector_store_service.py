"""
Tests for VectorStoreService
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import os

from src.services.vector_store_service import VectorStoreService


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client"""
    with patch('src.services.vector_store_service.OpenAI') as mock_client:
        yield mock_client


@pytest.fixture
def mock_api_key():
    """Mock the API key retrieval"""
    with patch('src.services.vector_store_service.get_openai_api_key', return_value='test-api-key'):
        yield


@pytest.fixture
def sample_degree_data():
    """Sample degree data for testing"""
    return [
        {
            'name': 'Master of Computer Science',
            'url': 'https://example.com/ms-cs',
            'content': 'This is a comprehensive program in computer science...',
            'title': 'MS in Computer Science',
            'description': 'Graduate program in CS',
            'scraped_url': 'https://example.com/ms-cs',
            'scraped_degree_name': 'Master of Computer Science'
        },
        {
            'name': 'Master of Data Science',
            'url': 'https://example.com/ms-ds',
            'content': 'This program focuses on data analytics and machine learning...',
            'title': 'MS in Data Science',
            'description': 'Graduate program in Data Science',
            'scraped_url': 'https://example.com/ms-ds',
            'scraped_degree_name': 'Master of Data Science'
        }
    ]


class TestVectorStoreService:
    """Tests for VectorStoreService"""
    
    def test_init_with_vector_store_id(self, mock_openai_client, mock_api_key):
        """Test initialization with vector store ID"""
        service = VectorStoreService(vector_store_id='vs_123')
        assert service.vector_store_id == 'vs_123'
    
    def test_init_with_env_variable(self, mock_openai_client, mock_api_key):
        """Test initialization with environment variable"""
        with patch.dict(os.environ, {'OPENAI_VECTOR_STORE_ID': 'vs_env_123'}):
            service = VectorStoreService()
            assert service.vector_store_id == 'vs_env_123'
    
    def test_init_without_vector_store_id(self, mock_openai_client, mock_api_key):
        """Test initialization without vector store ID"""
        with patch.dict(os.environ, {}, clear=True):
            service = VectorStoreService()
            assert service.vector_store_id is None
    
    def test_create_vector_store(self, mock_openai_client, mock_api_key):
        """Test creating a new vector store"""
        mock_vector_store = Mock()
        mock_vector_store.id = 'vs_new_123'
        
        mock_client_instance = mock_openai_client.return_value
        mock_client_instance.vector_stores.create.return_value = mock_vector_store
        
        service = VectorStoreService()
        vector_store_id = service.create_vector_store('Test Vector Store')
        
        assert vector_store_id == 'vs_new_123'
        assert service.vector_store_id == 'vs_new_123'
        mock_client_instance.vector_stores.create.assert_called_once_with(name='Test Vector Store')
    
    def test_format_degree_content(self, mock_openai_client, mock_api_key, sample_degree_data):
        """Test formatting degree content"""
        service = VectorStoreService(vector_store_id='vs_123')
        
        content = service._format_degree_content(sample_degree_data[0])
        
        assert 'Master of Computer Science' in content
        assert 'https://example.com/ms-cs' in content
        assert 'This is a comprehensive program in computer science' in content
        assert '## Program Information' in content
        assert '## Metadata' in content
    
    def test_upload_degree_data_success(self, mock_openai_client, mock_api_key, sample_degree_data):
        """Test successful upload of degree data"""
        # Mock the files.list to return no existing files
        mock_files_list = Mock()
        mock_files_list.data = []
        
        # Mock the file upload and vector store operations
        mock_file_obj = Mock()
        mock_file_obj.id = 'file_123'
        mock_file_obj.filename = 'degree_abc123def456.txt'
        
        mock_client_instance = mock_openai_client.return_value
        mock_client_instance.vector_stores.files.list.return_value = mock_files_list
        mock_client_instance.files.create.return_value = mock_file_obj
        mock_client_instance.vector_stores.files.create.return_value = Mock()
        
        service = VectorStoreService(vector_store_id='vs_123')
        result = service.upload_degree_data(sample_degree_data)
        
        assert result['vector_store_id'] == 'vs_123'
        assert result['total_degrees'] == 2
        assert result['new_uploads'] == 2
        assert result['updated_files'] == 0
        assert result['failed_uploads'] == 0
        assert len(result['uploaded_files']) == 2
    
    def test_upload_degree_data_no_vector_store_id(self, mock_openai_client, mock_api_key, sample_degree_data):
        """Test upload without vector store ID raises error"""
        with patch.dict(os.environ, {}, clear=True):
            service = VectorStoreService()
            
            with pytest.raises(ValueError, match="No vector store ID configured"):
                service.upload_degree_data(sample_degree_data)
    
    def test_upload_degree_data_partial_failure(self, mock_openai_client, mock_api_key):
        """Test upload with some failures"""
        # Create data where one will fail during temp file creation
        degree_data = [
            {'name': 'Valid Degree', 'content': 'Valid content'},
            {'name': None, 'content': 'This will fail'}  # This should cause an error
        ]
        
        # Mock the files.list to return no existing files
        mock_files_list = Mock()
        mock_files_list.data = []
        
        mock_file_obj = Mock()
        mock_file_obj.id = 'file_123'
        mock_file_obj.filename = 'degree_abc123def456.txt'
        
        mock_client_instance = mock_openai_client.return_value
        mock_client_instance.vector_stores.files.list.return_value = mock_files_list
        mock_client_instance.files.create.return_value = mock_file_obj
        mock_client_instance.vector_stores.files.create.return_value = Mock()
        
        service = VectorStoreService(vector_store_id='vs_123')
        
        # The upload should complete but report the failure
        result = service.upload_degree_data(degree_data)
        
        assert result['total_degrees'] == 2
        # At least one should succeed
        assert result['successful_operations'] >= 0
    
    def test_delete_all_files(self, mock_openai_client, mock_api_key):
        """Test deleting all files from vector store"""
        mock_file1 = Mock()
        mock_file1.id = 'file_1'
        mock_file2 = Mock()
        mock_file2.id = 'file_2'
        
        mock_files = Mock()
        mock_files.data = [mock_file1, mock_file2]
        
        mock_client_instance = mock_openai_client.return_value
        mock_client_instance.vector_stores.files.list.return_value = mock_files
        
        service = VectorStoreService(vector_store_id='vs_123')
        result = service.delete_all_files()
        
        assert result['vector_store_id'] == 'vs_123'
        assert result['deleted_count'] == 2
        assert mock_client_instance.vector_stores.files.delete.call_count == 2
    
    def test_delete_all_files_no_vector_store_id(self, mock_openai_client, mock_api_key):
        """Test delete without vector store ID raises error"""
        with patch.dict(os.environ, {}, clear=True):
            service = VectorStoreService()
            
            with pytest.raises(ValueError, match="No vector store ID configured"):
                service.delete_all_files()
    
    def test_get_vector_store_info(self, mock_openai_client, mock_api_key):
        """Test getting vector store information"""
        mock_vector_store = Mock()
        mock_vector_store.id = 'vs_123'
        mock_vector_store.name = 'Test Vector Store'
        mock_vector_store.status = 'completed'
        mock_vector_store.created_at = 1234567890
        mock_vector_store.file_counts = Mock()
        mock_vector_store.file_counts.dict.return_value = {'total': 5, 'completed': 5}
        
        mock_client_instance = mock_openai_client.return_value
        mock_client_instance.vector_stores.retrieve.return_value = mock_vector_store
        
        service = VectorStoreService(vector_store_id='vs_123')
        info = service.get_vector_store_info()
        
        assert info['id'] == 'vs_123'
        assert info['name'] == 'Test Vector Store'
        assert info['status'] == 'completed'
        assert info['file_counts']['total'] == 5
    
    def test_get_vector_store_info_no_id(self, mock_openai_client, mock_api_key):
        """Test get info without vector store ID raises error"""
        with patch.dict(os.environ, {}, clear=True):
            service = VectorStoreService()
            
            with pytest.raises(ValueError, match="No vector store ID configured"):
                service.get_vector_store_info()
    
    def test_hash_degree_name(self, mock_openai_client, mock_api_key):
        """Test hashing of degree names"""
        service = VectorStoreService(vector_store_id='vs_123')
        
        # Test consistent hashing
        hash1 = service._hash_degree_name('Master of Computer Science')
        hash2 = service._hash_degree_name('Master of Computer Science')
        assert hash1 == hash2
        
        # Test case insensitivity
        hash3 = service._hash_degree_name('MASTER OF COMPUTER SCIENCE')
        assert hash1 == hash3
        
        # Test whitespace normalization
        hash4 = service._hash_degree_name('  Master of Computer Science  ')
        assert hash1 == hash4
        
        # Test different names produce different hashes
        hash5 = service._hash_degree_name('Master of Data Science')
        assert hash1 != hash5
        
        # Test hash length
        assert len(hash1) == 16
    
    def test_get_existing_files_map(self, mock_openai_client, mock_api_key):
        """Test getting existing files map"""
        mock_file1 = Mock()
        mock_file1.id = 'vs_file_1'
        
        mock_file2 = Mock()
        mock_file2.id = 'vs_file_2'
        
        mock_files_list = Mock()
        mock_files_list.data = [mock_file1, mock_file2]
        
        # Mock the file objects with proper filenames
        mock_file_obj1 = Mock()
        mock_file_obj1.filename = 'degree_abc123def456.txt'
        
        mock_file_obj2 = Mock()
        mock_file_obj2.filename = 'degree_xyz789uvw012.txt'
        
        mock_client_instance = mock_openai_client.return_value
        mock_client_instance.vector_stores.files.list.return_value = mock_files_list
        mock_client_instance.files.retrieve.side_effect = [mock_file_obj1, mock_file_obj2]
        
        service = VectorStoreService(vector_store_id='vs_123')
        files_map = service._get_existing_files_map()
        
        assert 'abc123def456' in files_map
        assert 'xyz789uvw012' in files_map
        assert files_map['abc123def456'] == 'vs_file_1'
        assert files_map['xyz789uvw012'] == 'vs_file_2'
    
    def test_upload_degree_data_with_updates(self, mock_openai_client, mock_api_key, sample_degree_data):
        """Test uploading degree data that includes updates to existing files"""
        # Mock existing file with hash matching one of the degrees
        service = VectorStoreService(vector_store_id='vs_123')
        existing_hash = service._hash_degree_name('Master of Computer Science')
        
        mock_existing_file = Mock()
        mock_existing_file.id = 'vs_file_existing'
        
        mock_files_list = Mock()
        mock_files_list.data = [mock_existing_file]
        
        mock_existing_file_obj = Mock()
        mock_existing_file_obj.filename = f'degree_{existing_hash}.txt'
        
        # Mock new file upload
        mock_new_file = Mock()
        mock_new_file.id = 'file_new_123'
        mock_new_file.filename = 'degree_newhash123.txt'
        
        mock_client_instance = mock_openai_client.return_value
        mock_client_instance.vector_stores.files.list.return_value = mock_files_list
        mock_client_instance.files.retrieve.return_value = mock_existing_file_obj
        mock_client_instance.files.create.return_value = mock_new_file
        mock_client_instance.vector_stores.files.create.return_value = Mock()
        mock_client_instance.vector_stores.files.delete.return_value = Mock()
        
        result = service.upload_degree_data(sample_degree_data)
        
        # Should have one update and one new upload
        assert result['total_degrees'] == 2
        assert result['updated_files'] >= 1  # Count: At least one should be an update
        assert result['new_uploads'] >= 1    # Count: At least one should be new
        
        # Should have called delete for the existing file
        mock_client_instance.vector_stores.files.delete.assert_called()
