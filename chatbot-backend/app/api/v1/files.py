from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import shutil
from pathlib import Path
from app.db.session import get_db
from app.models.user import User
from app.models.file import File
from app.schemas.file import FileUploadResponse, FileListResponse
from app.core.security import get_current_user
from app.core.config import settings
from app.services.rag import process_uploaded_file

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    user_dir = Path(settings.UPLOAD_DIR) / str(current_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = user_dir / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    new_file = File(
        user_id=current_user.id,
        filename=file.filename,
        filepath=str(file_path),
        file_type=file_ext[1:]
    )
    db.add(new_file)
    await db.commit()
    await db.refresh(new_file)
    
    try:
        await process_uploaded_file(new_file, current_user.id, db)
    except Exception as e:
        print(f"Error processing file: {e}")
    
    return new_file

@router.get("/", response_model=List[FileListResponse])
async def list_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(File)
        .where(File.user_id == current_user.id)
        .order_by(File.created_at.desc())
    )
    files = result.scalars().all()
    return files

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(File).where(File.id == file_id))
    file_record = result.scalar_one_or_none()
    
    if not file_record or file_record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    if os.path.exists(file_record.filepath):
        os.remove(file_record.filepath)
    
    await db.delete(file_record)
    await db.commit()
    return None
