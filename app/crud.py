from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from .models import AnalyzedString
from .utils import analyze_string
from .schemas import StringCreate
from sqlalchemy import and_, or_
from typing import Optional, Dict, Any, Tuple, List


async def create_analyzed_string(db: AsyncSession, string_data: StringCreate):
    try:
        if not hasattr(string_data, 'value') or not isinstance(string_data.value, str) or not string_data.value.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid input. 'value' must be a non-empty string."
            )

        value = string_data.value.strip()
        analysis = analyze_string(value)

        # Check for duplicate
        existing = await get_string_by_sha256(db, analysis["sha256_hash"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="String already exists in the system"
            )

        new_string = AnalyzedString(
            id=analysis["sha256_hash"],
            value=value,
            length=analysis["length"],
            is_palindrome=analysis["is_palindrome"],
            unique_characters=analysis["unique_characters"],
            word_count=analysis["word_count"],
            sha256_hash=analysis["sha256_hash"],
            character_frequency_map=analysis["character_frequency_map"],
        )

        db.add(new_string)
        await db.commit()
        await db.refresh(new_string)
        return new_string

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating string: {str(e)}"
        )

async def get_string_by_sha256(db: AsyncSession, sha256_hash: str) -> Optional[AnalyzedString]:
    """Helper function to get a string by its SHA-256 hash."""
    result = await db.execute(
        select(AnalyzedString).where(AnalyzedString.sha256_hash == sha256_hash)
    )
    return result.scalar_one_or_none()

async def get_string_by_value(db: AsyncSession, value: str) -> AnalyzedString:
    """Get a string by its exact value."""
    if not value or not isinstance(value, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid string value"
        )

    try:
        result = await db.execute(
            select(AnalyzedString).where(AnalyzedString.value == value)
        )
        string = result.scalar_one_or_none()
        
        if not string:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="String not found."
            )
            
        return string
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving string"
        )

async def filter_strings(
    db: AsyncSession,
    is_palindrome: Optional[bool] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    word_count: Optional[int] = None,
    contains_character: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Tuple[List[AnalyzedString], Dict[str, Any]]:
    """
    Filter strings based on various criteria.
    
    Returns a tuple of (records, applied_filters)
    """
    try:
        # Validate input parameters
        if min_length is not None and min_length < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_length must be a non-negative integer"
            )
            
        if max_length is not None and max_length < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_length must be a non-negative integer"
            )
            
        if word_count is not None and word_count < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="word_count must be a non-negative integer"
            )
            
        if contains_character and len(contains_character) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="contains_character must be a single character"
            )

        # Build query
        query = select(AnalyzedString)
        filters = []
        
        if is_palindrome is not None:
            filters.append(AnalyzedString.is_palindrome == is_palindrome)
            
        if min_length is not None:
            filters.append(AnalyzedString.length >= min_length)
            
        if max_length is not None:
            filters.append(AnalyzedString.length <= max_length)
            
        if word_count is not None:
            filters.append(AnalyzedString.word_count == word_count)
            
        if contains_character is not None:
            filters.append(AnalyzedString.value.ilike(f'%{contains_character}%'))
        
        # Apply filters if any
        if filters:
            query = query.where(and_(*filters))
            
        # Add pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        records = result.scalars().all()
        
        # Prepare filters_applied dictionary
        filters_applied = {
            'is_palindrome': is_palindrome,
            'min_length': min_length,
            'max_length': max_length,
            'word_count': word_count,
            'contains_character': contains_character,
            'limit': limit,
            'offset': offset
        }
        
        return records, {k: v for k, v in filters_applied.items() if v is not None}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error filtering strings: {str(e)}"
        )

async def delete_string_by_value(db: AsyncSession, value: str) -> None:
    """Delete a string by its value."""
    try:
        if not value or not isinstance(value, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid string value"
            )
            
        # Find the string
        result = await db.execute(
            select(AnalyzedString).where(AnalyzedString.value == value)
        )
        string = result.scalar_one_or_none()
        
        if not string:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="String not found."
            )
            
        # Delete the string
        await db.delete(string)
        await db.commit()
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting string: {str(e)}"
        )
