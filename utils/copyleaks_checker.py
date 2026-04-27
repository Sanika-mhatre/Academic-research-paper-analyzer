import os
import uuid
import base64
from pathlib import Path
from dotenv import load_dotenv

# -------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# -------------------------------------------

# Get base directory of project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file (contains API credentials)
load_dotenv(BASE_DIR / ".env")

# Get Copyleaks credentials from environment
COPYLEAKS_EMAIL = os.getenv("COPYLEAKS_EMAIL")
COPYLEAKS_API_KEY = os.getenv("COPYLEAKS_API_KEY")


def submit_to_copyleaks(text):
    """
    Submit text to Copyleaks for plagiarism scan.

    NOTE:
    - Copyleaks is asynchronous (does not return result instantly)
    - It returns a scan_id which is used to track the scan
    """

    # -------------------------------------------
    # CHECK IF API CREDENTIALS EXIST
    # -------------------------------------------
    if not COPYLEAKS_EMAIL or not COPYLEAKS_API_KEY:
        return {
            "status": "skipped",
            "scan_id": None,
            "message": "Copyleaks skipped: email/API key not found in .env file."
        }

    try:
        # Import Copyleaks SDK
        from copyleaks.copyleaks import Copyleaks
        from copyleaks.models.submit.document import FileDocument
        from copyleaks.models.submit.properties.scan_properties import ScanProperties

        # -------------------------------------------
        # LOGIN TO COPYLEAKS
        # -------------------------------------------
        auth_token = Copyleaks.login(COPYLEAKS_EMAIL, COPYLEAKS_API_KEY)

        # -------------------------------------------
        # GENERATE UNIQUE SCAN ID
        # -------------------------------------------
        # Each scan must have a unique ID (max 36 chars)
        scan_id = uuid.uuid4().hex[:32]

        # -------------------------------------------
        # CONVERT TEXT TO BASE64
        # -------------------------------------------
        # Copyleaks expects file content in base64 format
        base64_content = base64.b64encode(text.encode("utf-8")).decode("utf-8")

        # -------------------------------------------
        # SET SCAN PROPERTIES
        # -------------------------------------------
        # Webhook URL (not used currently, placeholder)
        scan_properties = ScanProperties("https://example.com/webhook/{STATUS}")

        # Enable sandbox mode (for testing, no real charges)
        scan_properties.set_sandbox(True)

        # -------------------------------------------
        # CREATE DOCUMENT OBJECT
        # -------------------------------------------
        file_submission = FileDocument(base64_content, "research_paper.txt")

        # Attach properties to submission
        file_submission.set_properties(scan_properties)

        # -------------------------------------------
        # SUBMIT FILE TO COPYLEAKS
        # -------------------------------------------
        Copyleaks.submit_file(auth_token, scan_id, file_submission)

        # -------------------------------------------
        # RETURN SUCCESS RESPONSE
        # -------------------------------------------
        return {
            "status": "submitted",
            "scan_id": scan_id,
            "message": f"Copyleaks sandbox scan submitted successfully. Scan ID: {scan_id}"
        }

    except Exception as e:
        # -------------------------------------------
        # HANDLE ERRORS
        # -------------------------------------------
        return {
            "status": "error",
            "scan_id": None,
            "message": f"Copyleaks error: {str(e)}"
        }