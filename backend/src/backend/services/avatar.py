import asyncio
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError
from starlette import status

from backend.core.config import settings

MAX_AVATAR_SIZE_BYTES = 5 * 1024 * 1024
MAX_AVATAR_PIXELS = 20_000_000
AVATAR_URL_PREFIX = "/api/v1/media/avatars/"
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}


def _store_avatar(content: bytes, storage_dir: Path) -> str:
    if len(content) > MAX_AVATAR_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Максимальный размер аватара — 5 МБ.",
        )
    try:
        with Image.open(BytesIO(content)) as source:
            if source.format not in ALLOWED_IMAGE_FORMATS:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Выбери изображение JPEG, PNG или WebP.",
                )
            if source.width * source.height > MAX_AVATAR_PIXELS:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Размер изображения слишком большой.",
                )
            if source.width < 32 or source.height < 32:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Изображение должно быть не меньше 32 × 32 пикселей.",
                )
            # ADDED: Re-encode uploads to normalized WebP and discard source metadata.
            image = ImageOps.exif_transpose(source)
            image = ImageOps.fit(
                image,
                (512, 512),
                method=Image.Resampling.LANCZOS,
            )
            if "A" in image.getbands():
                image = image.convert("RGBA")
            else:
                image = image.convert("RGB")
    except HTTPException:
        raise
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл не является корректным изображением.",
        ) from error

    storage_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.webp"
    path = storage_dir / filename
    image.save(path, format="WEBP", quality=86, method=5)
    return f"{AVATAR_URL_PREFIX}{filename}"


async def store_avatar(content: bytes) -> str:
    return await asyncio.to_thread(
        _store_avatar,
        content,
        settings.avatar_storage_dir,
    )


def _delete_avatar(avatar_url: str | None, storage_dir: Path) -> None:
    if not avatar_url or not avatar_url.startswith(AVATAR_URL_PREFIX):
        return
    filename = avatar_url.removeprefix(AVATAR_URL_PREFIX)
    if not filename or Path(filename).name != filename:
        return
    path = storage_dir / filename
    if path.parent.resolve() != storage_dir.resolve():
        return
    path.unlink(missing_ok=True)


async def delete_avatar(avatar_url: str | None) -> None:
    await asyncio.to_thread(
        _delete_avatar,
        avatar_url,
        settings.avatar_storage_dir,
    )
