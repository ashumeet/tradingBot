from fastapi import APIRouter, Depends, status
from trader_app.models.account import AccountSummaryResponse
from trader_app.models.portfolio import PositionResponse
from trader_app.services.account_service import AccountService
from typing import List
from src.trader_app.security.dependencies import get_ssh_authenticated_user

router = APIRouter(prefix="/api/v1", tags=["account", "positions"])

def get_account_service() -> AccountService:
    """
    Dependency provider for AccountService. Override in tests as needed.
    """
    return AccountService()

@router.get(
    "/account",
    response_model=AccountSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get account summary",
    description="""
    Returns the account summary including balance, buying power, equity, and other key metrics.
    """,
    response_description="Account summary response",
    responses={
        200: {
            "description": "Account summary successfully returned.",
            "content": {
                "application/json": {
                    "example": AccountSummaryResponse.model_config["json_schema_extra"]["example"]
                }
            }
        },
        502: {"description": "Alpaca API error"},
        500: {"description": "Internal server error"}
    }
)
def get_account_summary(account_service: AccountService = Depends(get_account_service), auth=Depends(get_ssh_authenticated_user)):
    """
    Get account summary (balance, buying power, equity, etc.)
    """
    return account_service.get_account_summary()

@router.get(
    "/positions",
    response_model=List[PositionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all positions",
    description="""
    Returns all current positions in the account.
    """,
    response_description="List of positions",
    responses={
        200: {
            "description": "Positions returned successfully.",
            "content": {
                "application/json": {
                    "example": [PositionResponse.model_config["json_schema_extra"]["example"]]
                }
            }
        },
        502: {"description": "Alpaca API error"},
        500: {"description": "Internal server error"}
    }
)
def get_all_positions(account_service: AccountService = Depends(get_account_service), auth=Depends(get_ssh_authenticated_user)):
    """
    Get all current positions in the account.
    """
    return account_service.get_all_positions()
