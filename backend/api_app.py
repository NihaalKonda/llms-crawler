from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .crawler import crawl_site
from .generator import generate_llms_txt, generate_llms_full_txt

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    url: str

@app.post("/api/crawl")
def crawl(req: CrawlRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        result = crawl_site(url)
        pages = result.pages
        llms_txt = generate_llms_txt(pages)
        llms_full_txt = generate_llms_full_txt(pages)
        return {
            "llms_txt": llms_txt,
            "llms_full_txt": llms_full_txt,
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Crawl error: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))