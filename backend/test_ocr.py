
from pathlib import Path

from app.ocr import extract_text


# Locate the test image inside app/uploads
image_path = (
    Path(__file__).parent
    / "app"
    / "uploads"
    / "test multimedia.jpg"
)


def main():

    try:
        # Check that the image exists
        if not image_path.is_file():
            raise FileNotFoundError

        # Run OCR
        result = extract_text(
            str(image_path),
            language="en"
        )

        # Display clean results
        print("\n========== OCR RESULTS ==========")

        print("Language:", result["language"])

        print("\nFull extracted text:")
        print(result["full_text"])

        print("\nDetected text regions:")

        for item in result["extracted_text"]:

            status = (
                " - UNCERTAIN"
                if item["uncertain"]
                else ""
            )

            print(
                f"- {item['text']} "
                f"| Confidence: {item['confidence']:.1%}"
                f"{status}"
            )

        print(
            "\nTotal detected regions:",
            result["total_text_regions"]
        )

        print("=================================\n")

    except FileNotFoundError:
        print(f"ERROR: Test image not found: {image_path}")

    except ValueError as error:
        print("ERROR:", error)


if __name__ == "__main__":
    main()
