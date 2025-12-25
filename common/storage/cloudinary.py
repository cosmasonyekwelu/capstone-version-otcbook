import cloudinary.uploader
from typing import BinaryIO


def upload_private_file(
    *,
    file_obj: BinaryIO,
    public_id: str,
) -> str:
    """
    Upload a file to Cloudinary as a PRIVATE asset.

    - Supports images, PDFs, and other raw files
    - Does not expose public URLs
    - Returns a secure URL for backend use only
    """

    result = cloudinary.uploader.upload(
        file_obj,
        public_id=public_id,
        resource_type="raw",
        type="private",
        overwrite=True,
    )

    return result["secure_url"]
