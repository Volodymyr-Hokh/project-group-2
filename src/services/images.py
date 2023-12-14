from base64 import b64encode
from io import BytesIO
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException
from sqlalchemy.orm import Session
import qrcode
from qrcode.image.base import BaseImage

from src.conf.config import settings
from src.database.models import User
from src.repository.images import get_image


class ImageService:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    async def upload_image(self, file):
        """ """
        unique_filename = str(uuid4())
        public_id = f"KillerInstagram/{unique_filename}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            version=r.get("version")
        )
        return {"public_id": public_id, "url": src_url}

    async def resize_image(
        self, image_id: str, width: int, height: int, user: User, db: Session
    ):
        """ """
        image = await get_image(image_id, user=user, db=db)
        transformed_url = cloudinary.uploader.explicit(
            image.public_id,
            type="upload",
            eager=[
                {
                    "width": width,
                    "height": height,
                    "crop": "fill",
                    "gravity": "auto",
                },
                {"fetch_format": "auto"},
                {"radius": "max"},
            ],
        )
        try:
            url_to_return = transformed_url["eager"][0]["secure_url"]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid width or height")
        return url_to_return

    async def add_filter(self, image_id: str, filter: str, user: User, db: Session):
        """ """
        filters = [
            "al_dente",
            "athena",
            "audrey",
            "aurora",
            "daguerre",
            "eucalyptus",
            "fes",
            "frost",
            "hairspray",
            "hokusai",
            "incognito",
            "linen",
            "peacock",
            "primavera",
            "quartz",
            "red_rock",
            "refresh",
            "sizzle",
            "sonnet",
            "ukulele",
            "zorro",
        ]
        effect = f"art:{filter}" if filter in filters else filter
        image = await get_image(image_id, user=user, db=db)
        transformed_url = cloudinary.uploader.explicit(
            image.public_id,
            type="upload",
            eager=[
                {
                    "effect": effect,
                },
                {"fetch_format": "auto"},
                {"radius": "max"},
            ],
        )
        try:
            url_to_return = transformed_url["eager"][0]["secure_url"]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid filter")
        return url_to_return

    async def generate_qr_code(self, image_url: str):
        """ """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(image_url)
        qr.make(fit=True)
        qr_code = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        qr_code.save(buffered, "PNG")
        qr_bytes = buffered.getvalue()
        return qr_bytes


image_service = ImageService()
