from fastapi import FastAPI, Depends, status, Query, Response, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from .database import engine
from . import models
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas, crud
from app.database import get_db
from app.filters import parse_natural_language


app = FastAPI()

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the String Analyzer API!",
        "endpoints": {
            "POST /strings": "Analyze and store a string",
            "GET /strings/{value}": "Retrieve analysis of a specific string",
            "GET /strings": "Retrieve all strings with optional query filtering",
            "GET /strings/filter-by-natural-language?query=...": "Filter using natural language queries like 'all single word palindromic strings'",
            "DELETE /strings/{value}": "Delete a string from the database",
            "GET /docs": "Interactive API documentation (Swagger UI)",
            "GET /redoc": "Alternative API documentation (ReDoc)"
        },
        "note": "Use the /docs endpoint to try the API interactively."
    }

@app.post("/strings", response_model=schemas.StringResponse, status_code=status.HTTP_201_CREATED)
async def analyze_string(payload: schemas.StringCreate, db: AsyncSession = Depends(get_db)):
    new_string = await crud.create_analyzed_string(db, payload)

    return {
        "id": new_string.id,
        "value": new_string.value,
        "properties": {
            "length": new_string.length,
            "is_palindrome": new_string.is_palindrome,
            "unique_characters": new_string.unique_characters,
            "word_count": new_string.word_count,
            "sha256_hash": new_string.sha256_hash,
            "character_frequency_map": new_string.character_frequency_map,
        },
        "created_at": new_string.created_at
    }

@app.get("/strings/filter-by-natural-language")
async def filter_by_natural_language(query: str, db: AsyncSession = Depends(get_db)):
    try:
        parsed_filters = parse_natural_language(query)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unable to parse natural language query.")

    strings, _ = await crud.filter_strings(
        db,
        is_palindrome=parsed_filters.get("is_palindrome"),
        min_length=parsed_filters.get("min_length"),
        max_length=parsed_filters.get("max_length"),
        word_count=parsed_filters.get("word_count"),
        contains_character=parsed_filters.get("contains_character"),
    )

    data = []
    for s in strings:
        data.append({
            "id": s.id,
            "value": s.value,
            "properties": {
                "length": s.length,
                "is_palindrome": s.is_palindrome,
                "unique_characters": s.unique_characters,
                "word_count": s.word_count,
                "sha256_hash": s.sha256_hash,
                "character_frequency_map": s.character_frequency_map,
            },
            "created_at": s.created_at
        })

    # ✅ Return even if data is empty
    return {
        "data": data,
        "count": len(data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters
        }
    }

@app.get("/strings/{value}", response_model=schemas.StringResponse)
async def get_string(value: str, db: AsyncSession = Depends(get_db)):
    if value == "filter-by-natural-language":
        raise HTTPException(status_code=404, detail="Invalid string value.")
    
    string = await crud.get_string_by_value(db, value)
    return {
        "id": string.id,
        "value": string.value,
        "properties": {
            "length": string.length,
            "is_palindrome": string.is_palindrome,
            "unique_characters": string.unique_characters,
            "word_count": string.word_count,
            "sha256_hash": string.sha256_hash,
            "character_frequency_map": string.character_frequency_map,
        },
        "created_at": string.created_at
    }

@app.get("/strings")
async def get_filtered_strings(
    is_palindrome: Optional[bool] = Query(None),
    min_length: Optional[int] = Query(None),
    max_length: Optional[int] = Query(None),
    word_count: Optional[int] = Query(None),
    contains_character: Optional[str] = Query(None, min_length=1, max_length=1),
    db: AsyncSession = Depends(get_db)
):
    strings, filters_applied = await crud.filter_strings(
        db,
        is_palindrome,
        min_length,
        max_length,
        word_count,
        contains_character
    )

    data = []
    for s in strings:
        data.append({
            "id": s.id,
            "value": s.value,
            "properties": {
                "length": s.length,
                "is_palindrome": s.is_palindrome,
                "unique_characters": s.unique_characters,
                "word_count": s.word_count,
                "sha256_hash": s.sha256_hash,
                "character_frequency_map": s.character_frequency_map,
            },
            "created_at": s.created_at
        })

    return {
        "data": data,
        "count": len(data),
        "filters_applied": {k: v for k, v in filters_applied.items() if v is not None}
    }

@app.delete("/strings/{value}", status_code=204)
async def delete_string(value: str, db: AsyncSession = Depends(get_db)):
    await crud.delete_string_by_value(db, value)
    return Response(status_code=204)