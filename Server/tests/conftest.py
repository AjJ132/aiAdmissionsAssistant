"""
Shared test fixtures and configuration for pytest
"""
import pytest
import json
import os
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_lambda_context():
    """Mock AWS Lambda context object"""
    context = Mock()
    context.function_name = "test-function"
    context.function_version = "$LATEST"
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    context.memory_limit_in_mb = "128"
    context.remaining_time_in_millis = lambda: 30000
    context.log_group_name = "/aws/lambda/test-function"
    context.log_stream_name = "2024/01/01/[$LATEST]test"
    context.aws_request_id = "test-request-id"
    return context


@pytest.fixture
def sample_lambda_event():
    """Sample Lambda API Gateway v2 event"""
    return {
        "routeKey": "POST /scrape",
        "version": "2.0",
        "rawPath": "/scrape",
        "rawQueryString": "",
        "headers": {
            "content-type": "application/json"
        },
        "queryStringParameters": {},
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "test-api",
            "domainName": "test.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "test",
            "http": {
                "method": "POST",
                "path": "/scrape",
                "protocol": "HTTP/1.1",
                "sourceIp": "192.168.1.1",
                "userAgent": "test-agent"
            },
            "requestId": "test-request-id",
            "stage": "$default",
            "time": "01/Jan/2024:00:00:00 +0000",
            "timeEpoch": 1704067200000
        },
        "body": json.dumps({"key": "value"}),
        "isBase64Encoded": False
    }


@pytest.fixture
def sample_scraping_config():
    """Sample scraping configuration"""
    return {
        "grad_admissions_list_url": "https://example.com/graduate-programs",
        "grad_admissions_list_xpath": "//ul[@class='degree-list']",
        "timeout": 30,
        "max_retries": 3
    }


@pytest.fixture
def sample_degree_list_html():
    """Sample HTML for degree list page"""
    return """
    <html>
        <body>
            <div>
                <ul class="degree-list">
                    <li><a href="https://example.com/mba">Master of Business Administration</a></li>
                    <li><a href="https://example.com/mcs">Master of Computer Science</a></li>
                    <li><a href="https://example.com/med">Master of Education</a></li>
                </ul>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_degree_page_html():
    """Sample HTML for a degree detail page"""
    return """
    <html>
        <head>
            <title>Master of Computer Science | University</title>
        </head>
        <body>
            <main>
                <h1>Master of Computer Science</h1>
                <p>The Master of Computer Science program prepares students for advanced careers in software development, 
                artificial intelligence, and data science. This comprehensive program combines theoretical foundations 
                with practical applications in modern computing.</p>
                
                <h3 id="snapshot">Program Snapshot</h3>
                <div>
                    <p>Credit Hours: 36</p>
                    <p>Format: Online and On-Campus</p>
                    <p>Duration: 2 years full-time</p>
                </div>
                
                <h3>Admission Requirements</h3>
                <div class="two-column">
                    <ul>
                        <li><div>Bachelor's degree in Computer Science or related field</div></li>
                        <li><div>Minimum GPA of 3.0</div></li>
                        <li><div>GRE scores (optional)</div></li>
                        <li><div>Three letters of recommendation</div></li>
                        <li><div>Statement of purpose</div></li>
                    </ul>
                </div>
                
                <h3>Program Benefits</h3>
                <ul>
                    <li>Gain expertise in machine learning and AI</li>
                    <li>Work on real-world industry projects</li>
                    <li>Network with industry professionals</li>
                    <li>Access to cutting-edge research facilities</li>
                </ul>
                
                <h3>Contact Information</h3>
                <p>Phone: <a href="tel:555-123-4567">(555) 123-4567</a></p>
                <p>Email: <a href="mailto:cs-grad@example.com">cs-grad@example.com</a></p>
                
                <h3>Related Programs</h3>
                <ul>
                    <li><a href="https://example.com/degree/data-science">Master of Data Science</a></li>
                    <li><a href="https://example.com/degree/cyber-security">Master of Cybersecurity</a></li>
                </ul>
            </main>
        </body>
    </html>
    """


@pytest.fixture
def sample_degree_page_with_unicode():
    """Sample HTML with Unicode characters that need cleaning"""
    return """
    <html>
        <body>
            <h1>Master\u2019s Degree in Engineering</h1>
            <p>The university\u2019s engineering program offers state\u2014of\u2014the\u2014art facilities
            and prepares students for careers in various fields\u2026</p>
            <p>Contact: email\u00a0us\u00a0at\u00a0info@example.com</p>
        </body>
    </html>
    """


@pytest.fixture
def mock_web_request_service():
    """Mock WebRequestService"""
    from unittest.mock import AsyncMock
    
    service = AsyncMock()
    service.fetchPage = AsyncMock()
    return service


@pytest.fixture
def mock_scraping_utils():
    """Mock ScrapingUtils"""
    from unittest.mock import Mock
    
    utils = Mock()
    utils.parse_degree_list = Mock()
    utils.extract_main_content = Mock()
    return utils


@pytest.fixture
def sample_degree_data():
    """Sample degree data structure"""
    return [
        {"name": "Master of Business Administration", "url": "https://example.com/mba"},
        {"name": "Master of Computer Science", "url": "https://example.com/mcs"},
        {"name": "Master of Education", "url": "https://example.com/med"}
    ]


@pytest.fixture
def sample_extracted_content():
    """Sample extracted content from a degree page"""
    return {
        'title': 'Master of Computer Science',
        'description': 'The Master of Computer Science program prepares students for advanced careers.',
        'program_snapshot': {
            'Credit Hours': '36',
            'Format': 'Online and On-Campus',
            'Duration': '2 years full-time'
        },
        'admission_requirements': [
            "Bachelor's degree in Computer Science or related field",
            'Minimum GPA of 3.0',
            'GRE scores (optional)',
            'Three letters of recommendation',
            'Statement of purpose'
        ],
        'program_benefits': [
            'Gain expertise in machine learning and AI',
            'Work on real-world industry projects'
        ],
        'contact_info': {
            'phone': '(555) 123-4567',
            'email': 'cs-grad@example.com'
        },
        'related_programs': [
            {'name': 'Master of Data Science', 'url': 'https://example.com/degree/data-science'}
        ],
        'key_sections': {},
        'all_text': 'Sample text content'
    }


@pytest.fixture
def temp_config_file(tmp_path, sample_scraping_config):
    """Create a temporary config file"""
    config_dir = tmp_path / "src" / "util"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "scraping_config.json"
    config_file.write_text(json.dumps(sample_scraping_config))
    return str(config_file)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables and paths"""
    # Add the project root to the Python path
    import sys
    project_root = os.path.dirname(os.path.dirname(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
