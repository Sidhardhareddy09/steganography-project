import io
import os
from pathlib import Path

from django.conf import settings
from django.shortcuts import render
from django.utils.text import get_valid_filename
from PIL import Image
import stepic

# Create your views here.


def index(request):
    return render(request, "index.html")


def hide_text_in_image(image: Image.Image, text: str) -> Image.Image:
    # stepic expects a string and works best on RGB images.
    if image.mode != "RGB":
        image = image.convert("RGB")
    return stepic.encode(image, text)  # pass the string directly


def extract_text_from_image(image: Image.Image) -> str:
    data = stepic.decode(image)
    if isinstance(data, bytes):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return ""
    if data is None:
        return ""
    return str(data)


def encryption_view(request):
    message = ""
    encrypted_image_url = None

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        image_file = request.FILES.get("image")

        if not text:
            message = "No text provided to hide."
        elif not image_file:
            message = "No image uploaded."
        else:
            try:
                image = Image.open(image_file)

                # Ensure PNG format for consistency (convert if needed)
                if image.format != "PNG":
                    image = image.convert("RGB")  # stepic expects RGB for embedding
                    buffer = io.BytesIO()
                    image.save(buffer, format="PNG")
                    buffer.seek(0)
                    image = Image.open(buffer)

                new_image = hide_text_in_image(image, text)

                # Build output path under MEDIA_ROOT
                encrypted_dir = Path(settings.MEDIA_ROOT) / "encrypted_images"
                encrypted_dir.mkdir(parents=True, exist_ok=True)

                safe_name = get_valid_filename(image_file.name)
                output_filename = f"new_{safe_name.rsplit('.', 1)[0]}.png"
                output_path = encrypted_dir / output_filename

                new_image.save(output_path, format="PNG")

                encrypted_image_url = os.path.join(
                    settings.MEDIA_URL.rstrip("/"), "encrypted_images", output_filename
                )

                message = "Text has been encrypted in the image."
            except Exception as e:
                message = f"An error occurred during encryption: {e}"

    context = {
        "message": message,
        "encrypted_image_url": encrypted_image_url,
    }
    return render(request, "encryption.html", context)


def decryption_view(request):
    text = ""
    error = ""

    if request.method == "POST":
        image_file = request.FILES.get("image")
        if not image_file:
            error = "No image uploaded."
        else:
            try:
                image = Image.open(image_file)

                if image.format != "PNG":
                    image = image.convert("RGB")
                    buffer = io.BytesIO()
                    image.save(buffer, format="PNG")
                    buffer.seek(0)
                    image = Image.open(buffer)

                text = extract_text_from_image(image)
                if text == "":
                    error = "No hidden text found or failed to decode."
            except Exception as e:
                error = f"An error occurred during decryption: {e}"

    context = {
        "text": text,
        "error": error,
    }
    return render(request, "decryption.html", context)
