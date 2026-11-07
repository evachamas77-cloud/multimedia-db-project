
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse
from pathlib import Path
import shutil
import uuid

from app.database import engine, Base, SessionLocal
from app import models
from app.image_processing import analyze_image
from app.ocr import extract_text
from app.object_detection import detect_objects


# Create the FastAPI application
app = FastAPI(
    title="Multimedia Database API",
    description="Backend for an AI assistant for visually impaired people",
    version="1.0.0"
)


# Define the image upload directory
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Multimedia Database API is running!",
        "status": "success"
    }


# Upload an image
@app.post("/upload-frame")
async def upload_frame(file: UploadFile = File(...)):

    allowed_types = ["image/jpeg", "image/png", "image/webp"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and WEBP images are allowed."
        )

    extension = Path(file.filename or "").suffix.lower()

    if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file extension."
        )

    filename = f"{uuid.uuid4()}{extension}"
    file_path = UPLOAD_DIR / filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        db = SessionLocal()

        try:
            new_frame = models.Frame(
                filename=filename,
                file_path=str(file_path)
            )

            db.add(new_frame)
            db.commit()
            db.refresh(new_frame)

        except Exception:
            db.rollback()

            if file_path.exists():
                file_path.unlink()

            raise HTTPException(
                status_code=500,
                detail="Could not save image information to the database."
            )

        finally:
            db.close()

    finally:
        await file.close()

    return {
        "message": "Image uploaded and recorded successfully!",
        "id": new_frame.id,
        "filename": new_frame.filename,
        "status": "success"
    }


# Retrieve all uploaded image records
@app.get("/frames")
def get_frames():

    db = SessionLocal()

    try:
        frames = db.query(models.Frame).order_by(
            models.Frame.uploaded_at.desc()
        ).all()

        return [
            {
                "id": frame.id,
                "filename": frame.filename,
                "file_path": frame.file_path,
                "uploaded_at": frame.uploaded_at
            }
            for frame in frames
        ]

    finally:
        db.close()


# Retrieve the actual image file
@app.get("/frames/{frame_id}/image")
def get_frame_image(frame_id: int):

    db = SessionLocal()

    try:
        frame = db.query(models.Frame).filter(
            models.Frame.id == frame_id
        ).first()

        if frame is None:
            raise HTTPException(
                status_code=404,
                detail="Image not found."
            )

        image_path = Path(frame.file_path)

        if not image_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Image file not found."
            )

        return FileResponse(image_path)

    finally:
        db.close()


# Delete an image and its associated analyses
@app.delete("/frames/{frame_id}")
def delete_frame(frame_id: int):

    db = SessionLocal()

    try:
        frame = db.query(models.Frame).filter(
            models.Frame.id == frame_id
        ).first()

        if frame is None:
            raise HTTPException(
                status_code=404,
                detail="Image not found."
            )

        file_path = Path(frame.file_path)

        # Delete the annotated image if it exists
        annotated_path = (
            file_path.parent
            / f"{file_path.stem}_detected.jpg"
        )

        if annotated_path.is_file():
            annotated_path.unlink()

        if file_path.is_file():
            file_path.unlink()

        # Delete all analyses associated with this image
        db.query(models.Analysis).filter(
            models.Analysis.frame_id == frame_id
        ).delete(synchronize_session=False)

        db.delete(frame)
        db.commit()

        return {
            "message": "Image and associated analyses deleted successfully!",
            "id": frame_id,
            "status": "success"
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# Analyze image quality using OpenCV
@app.get("/frames/{frame_id}/analyze")
def analyze_frame(frame_id: int):

    db = SessionLocal()

    try:
        frame = db.query(models.Frame).filter(
            models.Frame.id == frame_id
        ).first()

        if frame is None:
            raise HTTPException(
                status_code=404,
                detail="Image not found."
            )

        image_path = Path(frame.file_path)

        if not image_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Image file not found."
            )

        try:
            result = analyze_image(str(image_path))

        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        return {
            "id": frame.id,
            "filename": frame.filename,
            "image_analysis": result,
            "status": "success"
        }

    finally:
        db.close()


# Extract text using EasyOCR and save results in SQLite
@app.get("/frames/{frame_id}/ocr")
def ocr_frame(frame_id: int, language: str = "en"):

    db = SessionLocal()

    try:
        frame = db.query(models.Frame).filter(
            models.Frame.id == frame_id
        ).first()

        if frame is None:
            raise HTTPException(
                status_code=404,
                detail="Image not found."
            )

        image_path = Path(frame.file_path)

        if not image_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Image file not found."
            )

        try:
            result = extract_text(
                str(image_path),
                language=language
            )

        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        # Save OCR results in the analyses table
        analysis_record = models.Analysis(
            frame_id=frame.id,
            analysis_type="ocr",
            results=result
        )

        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)

        return {
            "id": frame.id,
            "filename": frame.filename,
            "analysis_id": analysis_record.id,
            "ocr_results": result,
            "status": "success",
            "saved_to_database": True
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# Detect objects using YOLO and save results in SQLite
@app.get("/frames/{frame_id}/detect")
def detect_frame(frame_id: int, request: Request):

    db = SessionLocal()

    try:
        frame = db.query(models.Frame).filter(
            models.Frame.id == frame_id
        ).first()

        if frame is None:
            raise HTTPException(
                status_code=404,
                detail="Image not found."
            )

        image_path = Path(frame.file_path)

        if not image_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Image file not found."
            )

        try:
            result = detect_objects(str(image_path))

        except (ValueError, FileNotFoundError) as error:
            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        # Create a URL for the annotated image
        annotated_image_url = str(
            request.url_for(
                "get_detected_frame_image",
                frame_id=frame.id
            )
        )

        # Prepare the YOLO results for database storage
        detection_data = {
            "detected_objects": result["detected_objects"],
            "total_objects": result["total_objects"],
            "annotated_image_url": annotated_image_url
        }

        # Save object detection results in the analyses table
        analysis_record = models.Analysis(
            frame_id=frame.id,
            analysis_type="object_detection",
            results=detection_data
        )

        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)

        return {
            "id": frame.id,
            "filename": frame.filename,
            "analysis_id": analysis_record.id,
            "detected_objects": result["detected_objects"],
            "total_objects": result["total_objects"],
            "annotated_image_url": annotated_image_url,
            "status": "success",
            "saved_to_database": True
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# Retrieve the YOLO annotated image
@app.get(
    "/frames/{frame_id}/detected-image",
    name="get_detected_frame_image"
)
def get_detected_frame_image(frame_id: int):

    db = SessionLocal()

    try:
        frame = db.query(models.Frame).filter(
            models.Frame.id == frame_id
        ).first()

        if frame is None:
            raise HTTPException(
                status_code=404,
                detail="Image not found."
            )

        original_path = Path(frame.file_path)

        annotated_path = (
            original_path.parent
            / f"{original_path.stem}_detected.jpg"
        )

        if not annotated_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Annotated image not found. Run object detection first."
            )

        return FileResponse(
            annotated_path,
            media_type="image/jpeg"
        )

    finally:
        db.close()


# Retrieve all AI analyses associated with an image
@app.get("/frames/{frame_id}/analyses")
def get_frame_analyses(frame_id: int):

    db = SessionLocal()

    try:
        frame = db.query(models.Frame).filter(
            models.Frame.id == frame_id
        ).first()

        if frame is None:
            raise HTTPException(
                status_code=404,
                detail="Image not found."
            )

        analyses = db.query(models.Analysis).filter(
            models.Analysis.frame_id == frame_id
        ).order_by(
            models.Analysis.created_at.desc()
        ).all()

        return {
            "frame_id": frame_id,
            "filename": frame.filename,
            "total_analyses": len(analyses),
            "analyses": [
                {
                    "analysis_id": analysis.id,
                    "analysis_type": analysis.analysis_type,
                    "results": analysis.results,
                    "created_at": analysis.created_at
                }
                for analysis in analyses
            ]
        }

    finally:
        db.close()
