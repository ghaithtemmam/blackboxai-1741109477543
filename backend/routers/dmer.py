from fastapi import APIRouter, HTTPException, File, UploadFile, BackgroundTasks
from typing import List, Optional
import logging
from models import DMRequest, DMResponse, DMCampaignStatus, AutoReplyConfig, APIResponse
from database import db
from utils.instagram_client import instagram_client
from utils.file_parser import file_parser
from auto_reply import auto_reply_manager
import uuid
from datetime import datetime

router = APIRouter(prefix="/dmer", tags=["dmer"])
logger = logging.getLogger(__name__)

# Store campaign statuses in memory
active_campaigns = {}

@router.post("/send", response_model=APIResponse)
async def send_bulk_dms(
    background_tasks: BackgroundTasks,
    template_id: str,
    file: UploadFile = File(...),
    instagram_account_username: Optional[str] = None
):
    """
    Start a bulk DM campaign using a CSV file of recipients and a message template.
    """
    try:
        # Parse CSV file
        recipients, errors = await file_parser.parse_csv(file)
        if not recipients:
            raise HTTPException(
                status_code=400,
                detail=f"No valid recipients found in CSV. Errors: {errors}"
            )

        # Get template
        template = db.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        # Generate campaign ID
        campaign_id = str(uuid.uuid4())

        # Initialize campaign status
        campaign_status = DMCampaignStatus(
            campaign_id=campaign_id,
            total_messages=len(recipients),
            sent_messages=0,
            failed_messages=0,
            status="running",
            start_time=datetime.now()
        )
        active_campaigns[campaign_id] = campaign_status

        # Start sending messages in background
        background_tasks.add_task(
            process_bulk_dms,
            campaign_id,
            recipients,
            template,
            instagram_account_username
        )

        return APIResponse(
            success=True,
            message="Bulk DM campaign started",
            data={
                "campaign_id": campaign_id,
                "total_recipients": len(recipients),
                "errors": errors
            }
        )

    except Exception as e:
        logger.error(f"Error starting bulk DM campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns", response_model=List[DMCampaignStatus])
async def list_campaigns():
    """List all DM campaigns and their statuses."""
    try:
        return list(active_campaigns.values())
    except Exception as e:
        logger.error(f"Error listing campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}", response_model=DMCampaignStatus)
async def get_campaign_status(campaign_id: str):
    """Get the status of a specific DM campaign."""
    try:
        if campaign_id not in active_campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return active_campaigns[campaign_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-reply/{username}", response_model=APIResponse)
async def configure_auto_reply(username: str, config: AutoReplyConfig):
    """Configure auto-reply settings for an Instagram account."""
    try:
        # Verify account exists
        account = db.get_account(username)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # If enabling auto-reply, verify template exists
        if config.is_enabled and config.template_id:
            template = db.get_template(config.template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")

        # Update auto-reply configuration
        await auto_reply_manager.update_config(username, config)

        return APIResponse(
            success=True,
            message=f"Auto-reply {'enabled' if config.is_enabled else 'disabled'} for {username}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring auto-reply: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_bulk_dms(
    campaign_id: str,
    recipients: List[dict],
    template: Template,
    instagram_account_username: Optional[str]
):
    """Process bulk DMs in background."""
    try:
        campaign = active_campaigns[campaign_id]

        # If no specific account provided, get first available account
        if not instagram_account_username:
            accounts = db.list_accounts()
            if not accounts:
                raise Exception("No Instagram accounts available")
            instagram_account_username = accounts[0].username

        # Get account
        account = db.get_account(instagram_account_username)
        if not account:
            raise Exception(f"Account {instagram_account_username} not found")

        # Ensure account is logged in
        success, error = await instagram_client.login(account)
        if not success:
            raise Exception(f"Failed to login as {instagram_account_username}: {error}")

        # Process each recipient
        for recipient in recipients:
            try:
                # Process template variables
                message = file_parser.process_template_variables(
                    template.content,
                    recipient
                )

                # Send DM
                success, error = await instagram_client.send_dm(
                    instagram_account_username,
                    recipient['username'],
                    message
                )

                if success:
                    campaign.sent_messages += 1
                else:
                    campaign.failed_messages += 1
                    campaign.errors.append({
                        "username": recipient['username'],
                        "error": error
                    })

            except Exception as e:
                campaign.failed_messages += 1
                campaign.errors.append({
                    "username": recipient['username'],
                    "error": str(e)
                })

        # Update campaign status
        campaign.status = "completed"
        campaign.end_time = datetime.now()

    except Exception as e:
        logger.error(f"Campaign {campaign_id} failed: {str(e)}")
        if campaign_id in active_campaigns:
            campaign = active_campaigns[campaign_id]
            campaign.status = "failed"
            campaign.end_time = datetime.now()
            campaign.errors.append({"error": str(e)})

@router.delete("/campaigns/{campaign_id}", response_model=APIResponse)
async def delete_campaign(campaign_id: str):
    """Delete a campaign and its status."""
    try:
        if campaign_id not in active_campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        del active_campaigns[campaign_id]
        
        return APIResponse(
            success=True,
            message=f"Campaign {campaign_id} deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
