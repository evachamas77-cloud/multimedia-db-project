

import easyocr


# Cache OCR readers so pretrained models are not loaded repeatedly.
_readers = {}


def get_reader(language: str):
    """
    Return the appropriate EasyOCR reader.
    Supported languages: English, French and Arabic.
    """

    if language not in ["en", "fr", "ar"]:
        raise ValueError(
            "Unsupported language. Use en, fr or ar."
        )

    if language not in _readers:

        if language == "ar":
            languages = ["ar", "en"]
        else:
            languages = ["en", "fr"]

        _readers[language] = easyocr.Reader(
            languages,
            gpu=False
        )

    return _readers[language]


def extract_text(image_path: str, language: str = "en"):
    """
    Extract all text detected in an image.
    Preserve confidence scores and bounding boxes.
    Do not discard low-confidence detections.
    """

    reader = get_reader(language)

    results = reader.readtext(image_path)

    extracted_text = []

    for bounding_box, text, confidence in results:

        extracted_text.append({
            "text": text,
            "confidence": round(float(confidence), 3),
            "uncertain": float(confidence) < 0.50,
            "bounding_box": [
                [
                    round(float(point[0]), 2),
                    round(float(point[1]), 2)
                ]
                for point in bounding_box
            ]
        })

    full_text = " ".join(
        item["text"]
        for item in extracted_text
        if item["text"].strip()
    )

    return {
        "language": language,
        "full_text": full_text,
        "extracted_text": extracted_text,
        "total_text_regions": len(extracted_text)
    }
