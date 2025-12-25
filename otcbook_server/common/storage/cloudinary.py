import cloudinary.uploader
from typing import BinaryIO

def upload_private_pdf(
    file_obj: BinaryIO,
    public_id: str,
) -> str:
    """
    Upload a PDF to Cloudinary as a private raw asset.
    Returns the secure URL.
    """
    result = cloudinary.uploader.upload(
        file_obj,
        public_id=public_id,
        resource_type="raw",
        type="private",
        overwrite=True,
    )

    return result["secure_url"]
