import io
import os
import uuid
from PIL import Image as PILImage
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from ..auth import get_current_user
from ..database import get_db
from ..models import Image, User
from typing import Optional
from pydantic import BaseModel
from ..transforms import apply_transformations
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from ..limiter import limiter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/images", tags=["images"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


def to_dict(img: Image) -> dict:
    return {
        "id": img.id,
        "url": f"/images/{img.id}",
        "format": img.format,
        "width": img.width,
        "height": img.height,
        "size_bytes": img.size_bytes,
        "created_at": img.created_at,
    }
class ResizeParams(BaseModel):
    width: int = Field(gt=0, le=4000)
    height: int = Field(gt=0, le=4000)
class Transformations(BaseModel):
    resize: Optional[ResizeParams] = None
    crop: Optional[dict] = None
    rotate: Optional[float] = None
    flip: Optional[bool] = None
    mirror: Optional[bool] = None
    filters: Optional[dict] = None
    format: Optional[str] = None


class TransformBody(BaseModel):
    transformations: Transformations

@router.post("", status_code=201)
async def upload_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = await file.read()

    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="Max file size is 5MB")

    try:
        pil_img = PILImage.open(io.BytesIO(data))
        pil_img.load()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    if pil_img.format not in ALLOWED_FORMATS:
        raise HTTPException(status_code=400, detail="Allowed formats: JPEG, PNG, WEBP")

    filename = f"{uuid.uuid4().hex}.{pil_img.format.lower()}"
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
        f.write(data)

    record = Image(
        owner_id=user.id,
        filename=filename,
        format=pil_img.format,
        width=pil_img.width,
        height=pil_img.height,
        size_bytes=len(data),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return to_dict(record)

@router.get("")
def list_images(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Image).filter(Image.owner_id == user.id)
    total = query.count()
    items = (
        query.order_by(Image.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "items": [to_dict(i) for i in items],
    }

@router.get("/{image_id}")
def get_image(
    image_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.get(Image,image_id)
    if not record or record.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(os.path.join(UPLOAD_DIR, record.filename))

@router.post("/{image_id}/transform", status_code=201)
@limiter.limit("10/minute")
def transform_image(
    request: Request,
    image_id: int,
    body: TransformBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.get(Image, image_id)
    if not record or record.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Image not found")

    t = body.transformations.model_dump(exclude_none=True)
    pil_img = PILImage.open(os.path.join(UPLOAD_DIR, record.filename))

    try:
        result = apply_transformations(pil_img, t)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Transformation failed: {e}")

    fmt = t.get("format", record.format).upper()
    if fmt == "JPG":
        fmt = "JPEG"
    if fmt not in ALLOWED_FORMATS:
        raise HTTPException(status_code=400, detail="Allowed formats: JPEG, PNG, WEBP")
    if fmt == "JPEG":
        result = result.convert("RGB")

    filename = f"{uuid.uuid4().hex}.{fmt.lower()}"
    path = os.path.join(UPLOAD_DIR, filename)
    result.save(path, fmt)

    new_record = Image(
        owner_id=user.id,
        filename=filename,
        format=fmt,
        width=result.width,
        height=result.height,
        size_bytes=os.path.getsize(path),
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return to_dict(new_record)