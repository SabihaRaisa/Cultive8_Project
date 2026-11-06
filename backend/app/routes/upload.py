
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.log_reader import LogReader

router = APIRouter(prefix="/api/logs", tags=["Log Upload"])


@router.post("/upload")
async def upload_log(file: UploadFile = File(...)):

    if not file.filename or Path(file.filename).suffix.lower() not in [".log", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail="Only .log and .txt files are supported."
        )

    temp_path = None

    try:
        content = await file.read(LogReader.MAX_FILE_SIZE + 1)

        if len(content) > LogReader.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Maximum upload size is 10 MB."
            )

        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".log",
            delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        result = LogReader.read_log_file(str(temp_path))

        return {
            "status": "success",
            "message": "Log file uploaded successfully.",
            "data": result
        }

    except HTTPException:
        raise

    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error while processing the file."
        )

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        await file.close()
