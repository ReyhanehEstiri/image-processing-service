import io
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image as PILImage
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Image, User

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