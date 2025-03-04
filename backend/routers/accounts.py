from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
import logging
from models import InstagramAccount, AccountList, APIResponse
from database import db
from utils.instagram_client import instagram_client
from utils.file_parser import file_parser

router = APIRouter(prefix="/accounts", tags=["accounts"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=APIResponse)
async def add_account(account: InstagramAccount):
    """Add a single Instagram account."""
    try:
        # Test login before adding
        success, error = await instagram_client.login(account)
        if not success:
            raise HTTPException(status_code=400, detail=f"Login failed: {error}")

        # Add account to database
        if db.add_account(account):
            return APIResponse(
                success=True,
                message=f"Successfully added account {account.username}",
                data={"username": account.username}
            )
        else:
            raise HTTPException(status_code=400, detail="Account already exists")

    except Exception as e:
        logger.error(f"Error adding account: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", response_model=APIResponse)
async def bulk_add_accounts(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Bulk add Instagram accounts from CSV file."""
    try:
        # Parse CSV file
        accounts, errors = await file_parser.parse_instagram_accounts_csv(file)
        
        if not accounts:
            raise HTTPException(
                status_code=400,
                detail=f"No valid accounts found in CSV. Errors: {errors}"
            )

        # Add accounts in background
        background_tasks.add_task(bulk_process_accounts, accounts)

        return APIResponse(
            success=True,
            message=f"Processing {len(accounts)} accounts in background",
            data={"total_accounts": len(accounts), "errors": errors}
        )

    except Exception as e:
        logger.error(f"Error processing accounts CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=AccountList)
async def list_accounts():
    """List all Instagram accounts."""
    try:
        accounts = db.list_accounts()
        return AccountList(accounts=accounts, total=len(accounts))

    except Exception as e:
        logger.error(f"Error listing accounts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{username}", response_model=InstagramAccount)
async def get_account(username: str):
    """Get details of a specific Instagram account."""
    try:
        account = db.get_account(username)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting account {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{username}", response_model=APIResponse)
async def delete_account(username: str):
    """Delete an Instagram account."""
    try:
        # Logout if account is logged in
        instagram_client.logout(username)
        
        # Delete from database
        if db.delete_account(username):
            return APIResponse(
                success=True,
                message=f"Successfully deleted account {username}"
            )
        else:
            raise HTTPException(status_code=404, detail="Account not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{username}/login", response_model=APIResponse)
async def login_account(username: str):
    """Login to an Instagram account."""
    try:
        account = db.get_account(username)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        success, error = await instagram_client.login(account)
        if not success:
            raise HTTPException(status_code=400, detail=f"Login failed: {error}")

        return APIResponse(
            success=True,
            message=f"Successfully logged in as {username}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in account {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{username}/logout", response_model=APIResponse)
async def logout_account(username: str):
    """Logout from an Instagram account."""
    try:
        instagram_client.logout(username)
        return APIResponse(
            success=True,
            message=f"Successfully logged out {username}"
        )

    except Exception as e:
        logger.error(f"Error logging out account {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def bulk_process_accounts(accounts: List[dict]):
    """Process bulk account additions in background."""
    for account_data in accounts:
        try:
            account = InstagramAccount(**account_data)
            
            # Test login
            success, error = await instagram_client.login(account)
            if success:
                # Add to database if login successful
                db.add_account(account)
                logger.info(f"Successfully added account {account.username}")
            else:
                logger.error(f"Failed to add account {account.username}: {error}")

        except Exception as e:
            logger.error(f"Error processing account {account_data.get('username')}: {str(e)}")
