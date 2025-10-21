from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from .models import AnalyzedString
from .utils import analyze_string
from .schemas import StringCreate
from sqlalchemy import and_
from typing import Optional


async def create_analyzed_string(db: AsyncSession, string_data: StringCreate):
    value = string_data.value
    if not isinstance(value, str) or value.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid string input.")

    analysis = analyze_string(value)

    # Check for duplicate
    result = await db.execute(select(AnalyzedString).where(AnalyzedString.sha256_hash == analysis["sha256_hash"]))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=409, detail="String already exists.")

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

async def get_string_by_value(db: AsyncSession, value: str):
    stmt = select(AnalyzedString).where(AnalyzedString.value == value)
    result = await db.execute(stmt)
    string = result.scalar_one_or_none()

    if not string:
        raise HTTPException(status_code=404, detail="String not found.")

    return string

async def filter_strings(
    db: AsyncSession,
    is_palindrome: Optional[bool] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    word_count: Optional[int] = None,
    contains_character: Optional[str] = None
):
    filters = []
    query = select(AnalyzedString)

    if is_palindrome is not None:
        filters.append(AnalyzedString.is_palindrome == is_palindrome)

    if min_length is not None:
        filters.append(AnalyzedString.length >= min_length)

    if max_length is not None:
        filters.append(AnalyzedString.length <= max_length)

    if word_count is not None:
        filters.append(AnalyzedString.word_count == word_count)

    if contains_character is not None:
        filters.append(AnalyzedString.value.contains(contains_character))

    if filters:
        query = query.where(and_(*filters))

    result = await db.execute(query)
    records = result.scalars().all()

    return records, {
        "is_palindrome": is_palindrome,
        "min_length": min_length,
        "max_length": max_length,
        "word_count": word_count,
        "contains_character": contains_character
    }

async def delete_string_by_value(db: AsyncSession, value: str):
    stmt = select(AnalyzedString).where(AnalyzedString.value == value)
    result = await db.execute(stmt)
    string = result.scalar_one_or_none()

    if not string:
        raise HTTPException(status_code=404, detail="String not found.")

    await db.delete(string)
    await db.commit()
