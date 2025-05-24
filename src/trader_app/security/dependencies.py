from fastapi import Header, HTTPException, status, Request, Depends
from datetime import datetime, timedelta
from src.trader_app.security.ssh_auth import verify_signature
import os

MAX_SKEW_SECONDS = 30

async def get_ssh_authenticated_user(
    x_ssh_signature: str = Header(None, alias="X-SSH-Signature"),
    x_ssh_timestamp: str = Header(None, alias="X-SSH-Timestamp")
):
    """
    FastAPI dependency for SSH-key-based authentication.
    Requires X-SSH-Signature and X-SSH-Timestamp headers.
    Verifies the signature and timestamp. Raises 401 if invalid.
    Bypassed if TESTING=1 is set in the environment.
    """
    if os.getenv("TESTING") == "1":
        return {"authenticated": True, "bypass": True}
    try:
        if not x_ssh_signature or not x_ssh_timestamp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing SSH authentication headers."
            )
        # Parse and check timestamp
        ts = datetime.fromisoformat(x_ssh_timestamp.replace("Z", ""))
        now = datetime.utcnow()
        if abs((now - ts).total_seconds()) > MAX_SKEW_SECONDS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Timestamp is too old or in the future."
            )
        # Verify signature
        message = f"timestamp:{x_ssh_timestamp}".encode()
        if not verify_signature(message, x_ssh_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid SSH signature."
            )
        return {"authenticated": True}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"SSH authentication failed: {e}"
        ) 