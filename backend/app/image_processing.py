
import cv2
from pathlib import Path


def analyze_image(image_path: str):
    """
    Analyze an image and return its dimensions
    and sharpness information.
    """

    # Read the image
    image = cv2.imread(str(image_path))

    # Check whether the image was read successfully
    if image is None:
        raise ValueError("Could not read the image.")

    # Get image dimensions
    height, width = image.shape[:2]

    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate image sharpness
    sharpness = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    # Classify image quality approximately
    if sharpness < 100:
        quality = "Blurry or low detail"
    else:
        quality = "Relatively sharp"

    return {
        "width": width,
        "height": height,
        "sharpness": round(sharpness, 2),
        "quality": quality
    }
