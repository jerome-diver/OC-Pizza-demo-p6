"""Convert data type or format or form to be able to insert in database"""

from PIL import Image
from io import BytesIO
from uuid import uuid4
from hashlib import sha512
from pathlib import Path


class Convert():
    """Convert images, IP, or any data type to be inserted in oc-pizza"""

    def __init__(self):
        self._salt: bytes = None

    def thumb(self, image_file):
        """Return new filename thumbnail
        and byte content data to insert
        inside Postgresql bytea field's type"""

        img_file = Path(image_file)
        thumb_file = str(img_file.parent) + "/" + img_file.stem + "_thumb" \
                      + img_file.suffix
        format = "PNG" if img_file.suffix == ".png" else "JPEG"
        image = Image.open(image_file)
        image.thumbnail((64,64))
        print(thumb_file)
        image.save(thumb_file, quality=50, optimized=True)
        byte_file = BytesIO()
        image.save(byte_file, format=format)
        return Path(thumb_file).resolve(), byte_file.getvalue()

    def password(self, password):
        """Return a random salt and linked hashed password
        in bytes format to be able to insert inside bytea Postgresql field
        type"""

        self._salt = uuid4().bytes
        hashed_password = sha512(self._salt + password.encode()).digest()
        return hashed_password

    @property
    def salt(self):
        """Return own salt"""

        return self._salt