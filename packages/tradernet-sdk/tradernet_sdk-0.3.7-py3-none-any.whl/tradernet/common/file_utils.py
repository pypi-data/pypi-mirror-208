from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile


def extract_zip(content: bytes) -> dict[str, str]:
    """
    Extracting a zipped file into a dictionary having the structure
    "name->content".
    Parameters
    ----------
    content : bytes
        Byte-representation of an archive.
    Returns
    -------
    dict[str, str]
        Resulting dictionary.
    """
    with ZipFile(BytesIO(content)) as zip_file:
        return {
            name: zip_file.read(name).decode() for name in zip_file.namelist()
        }
