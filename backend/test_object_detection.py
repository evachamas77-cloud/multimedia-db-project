
from pathlib import Path

from app.database import SessionLocal
from app import models
from app.object_detection import detect_objects


# Database ID of the image we want to test
IMAGE_ID = 1


def main():

    print("\n========== YOLO OBJECT DETECTION TEST ==========\n")

    # Connect to the database
    db = SessionLocal()

    try:
        # Find the image in the database
        print(f"Searching for image ID: {IMAGE_ID}")

        frame = db.query(models.Frame).filter(
            models.Frame.id == IMAGE_ID
        ).first()

        if frame is None:
            print("ERROR: Image not found in database.")
            return

        # Get the actual image file path
        image_path = Path(frame.file_path)

        print("Image found:", frame.filename)

        if not image_path.is_file():
            print("ERROR: Image file does not exist.")
            return

        # Run YOLO
        print("\nRunning YOLO object detection...")

        result = detect_objects(str(image_path))

        # Display detected objects
        print("\n========== DETECTION RESULTS ==========\n")

        for index, item in enumerate(
            result["detected_objects"], start=1
        ):

            print(
                f"{index}. {item['object']} "
                f"| Confidence: {item['confidence']:.1%}"
            )

            print(
                "   Bounding box:",
                item["bounding_box"]
            )

        # Display total number of detections
        print("\nTotal detected objects:", result["total_objects"])

        # Display annotated image location
        print("\nAnnotated image saved successfully:")
        print(result["annotated_image"])

        # Confirm the file exists
        annotated_path = Path(result["annotated_image"])

        if annotated_path.is_file():
            print("\nConfirmed: Annotated image exists.")
        else:
            print("\nERROR: Annotated image was not found.")

        print("\n========== TEST COMPLETED ==========\n")

    except Exception as error:
        print("\nTEST FAILED:")
        print(type(error).__name__, str(error))

    finally:
        db.close()


if __name__ == "__main__":
    main()

