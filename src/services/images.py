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
    """
    A class that provides image-related services such as uploading, resizing, adding filters, and generating QR codes.
    """

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    async def upload_image(self, file):
        """Uploads an image to the cloud storage.

        Args:
            file: The file object representing the image to be uploaded.

        Returns:
            A dictionary containing the public ID and URL of the uploaded image.
        """
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
        """Resizes an image using Cloudinary API.

        Args:
            image_id (str): The ID of the image to be resized.\n
            width (int): The desired width of the resized image.\n
            height (int): The desired height of the resized image.\n
            user (User): The user performing the resize operation.\n
            db (Session): The database session.\n

        Returns:
            str: The URL of the resized image.

        Raises:
            HTTPException: If the width or height is invalid.
        """
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
        """Apply a filter to an image and return the transformed URL.

        Args:
            image_id (str): The ID of the image to apply the filter to.\n
            filter (str): The name of the filter to apply.\n
            user (User): The user performing the operation.\n
            db (Session): The database session.\n

        Returns:
            str: The URL of the transformed image.

        Raises:
            HTTPException: If the filter is invalid.
        """
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
        """Generates a QR code image from the given image URL.

        Args:
            image_url (str): The URL of the image to be encoded in the QR code.

        Returns:
            bytes: The bytes representation of the generated QR code image in PNG format.
        """
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
