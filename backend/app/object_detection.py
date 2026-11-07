
from ultralytics import YOLO
from pathlib import Path
import cv2


# Load the pretrained YOLO model once
model = YOLO("yolo26n.pt")


def detect_objects(image_path: str):
    """
    Detect objects in an image and return:
    - Object names
    - Confidence scores
    - Bounding box coordinates
    - Total number of detected objects
    - Path to the annotated image
    """

    # Convert the image path to a Path object
    image_path = Path(image_path)

    # Check that the image exists
    if not image_path.is_file():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # Run YOLO object detection
    results = model.predict(
        source=str(image_path),
        conf=0.25,
        verbose=False
    )

    if not results:
        raise ValueError(
            "YOLO could not process this image."
        )

    detected_objects = []

    # Extract information about detected objects
    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            object_name = result.names[class_id]

            confidence = float(box.conf[0])

            coordinates = [
                round(float(value), 2)
                for value in box.xyxy[0].tolist()
            ]

            detected_objects.append({
                "object": object_name,
                "confidence": round(confidence, 3),
                "bounding_box": coordinates
            })

    # Generate an annotated image with bounding boxes
    annotated_image = results[0].plot()

    # Create the output image path
    output_path = (
        image_path.parent
        / f"{image_path.stem}_detected.jpg"
    )

    # Save the annotated image
    saved = cv2.imwrite(
        str(output_path),
        annotated_image
    )

    if not saved:
        raise ValueError(
            "Could not save the annotated image."
        )

    # Return all detection results
    return {
        "detected_objects": detected_objects,
        "total_objects": len(detected_objects),
        "annotated_image": str(output_path)
    }

