from typing import List, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import codefly_sdk.codefly as codefly
from pydantic import BaseModel

from src.search import Search

codefly.init()

app = FastAPI()

if True: #codefly.is_local():
    origins = [
        "*",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


search_client = Search()



@app.get("/version")
async def version():
    return {"version": codefly.get_version()}

class SearchResult(BaseModel):
    nctId: str
    briefTitle: str
    officialTitle: Optional[str] = None
    conditions: List[str] = []
    overallStatus: str

@app.get('/search', response_model=List[SearchResult])
async def search(
        q: str = Query(..., min_length=1, description="Search query"),
        fields: List[str] = Query(["briefTitle", "officialTitle", "conditions"], description="Fields to search in"),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=100, description="Results per page")
):
    try:
        body = {
            'size': size,
            'from': (page - 1) * size,
            'query': {
                'multi_match': {
                    'query': q,
                    'fields': fields
                }
            }
        }

        results = search_client.find(body)

        if results is None:
            raise HTTPException(status_code=500, detail="Search operation failed")

        hits = results.get('hits', {}).get('hits', [])
        print("hits", len(hits))
        results = [
            SearchResult(
                nctId=hit['_source'].get('nctId', ''),
                briefTitle=hit['_source'].get('briefTitle', ''),
                officialTitle=hit['_source'].get('officialTitle'),
                conditions=hit['_source'].get('conditions', []),
                overallStatus=hit['_source'].get('overallStatus', '')
            )
            for hit in hits
        ]
        print(results)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/index-info')
async def index_info():
    stats = search_client.get_index_stats()
    if stats is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve index stats")

    return {
        "doc_count": stats['indices']['clinical_trials']['total']['docs']['count'],
        "size_in_bytes": stats['indices']['clinical_trials']['total']['store']['size_in_bytes']
    }

@app.post('/reindex')
async def reindex():
    search_client.delete_index()
    search_client.index()
    return {"message": "Reindexing completed"}
