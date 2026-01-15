import io
import pypdf
from fastapi import UploadFile, HTTPException

async def parse_resume(file: UploadFile) -> str:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        content = await file.read()
        pdf_reader = pypdf.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        # Reset file cursor just in case
        await file.seek(0)
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")
