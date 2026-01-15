"""
Test fixtures and configuration for backend tests
"""
import sys
import os

# Add project root to python path to allow importing main and app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
async def client():
    """Create async test client for API testing"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_job_role():
    """Sample job role for testing"""
    return "Senior Software Engineer"


@pytest.fixture
def sample_pdf_content():
    """Minimal valid PDF content for testing"""
    # This is a minimal valid PDF structure
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
191
%%EOF"""
