from fastapi import APIRouter, HTTPException
from typing import Optional
import logging
from models import Template, TemplateList, APIResponse
from database import db
from utils.groq_client import groq_client

router = APIRouter(prefix="/templates", tags=["templates"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=APIResponse)
async def create_template(template: Template):
    """Create a new message template."""
    try:
        # Extract variables from template content
        variables = [
            word[1:-1] for word in template.content.split()
            if word.startswith('{') and word.endswith('}')
        ]
        template.variables = list(set(variables))
        
        # Add template to database
        template_id = db.add_template(template)
        
        return APIResponse(
            success=True,
            message="Template created successfully",
            data={"template_id": template_id}
        )

    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=TemplateList)
async def list_templates():
    """List all message templates."""
    try:
        templates = db.list_templates()
        return TemplateList(templates=templates, total=len(templates))

    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{template_id}", response_model=Template)
async def get_template(template_id: str):
    """Get a specific template by ID."""
    try:
        template = db.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{template_id}", response_model=APIResponse)
async def update_template(template_id: str, template: Template):
    """Update an existing template."""
    try:
        # Extract variables from updated content
        variables = [
            word[1:-1] for word in template.content.split()
            if word.startswith('{') and word.endswith('}')
        ]
        template.variables = list(set(variables))
        
        # Update template in database
        if db.update_template(template_id, template.dict(exclude_unset=True)):
            return APIResponse(
                success=True,
                message=f"Template {template_id} updated successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Template not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{template_id}", response_model=APIResponse)
async def delete_template(template_id: str):
    """Delete a template."""
    try:
        if db.delete_template(template_id):
            return APIResponse(
                success=True,
                message=f"Template {template_id} deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Template not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=APIResponse)
async def generate_template_suggestions(
    business_type: str,
    purpose: str
):
    """Generate template suggestions using Groq AI."""
    try:
        suggestions = await groq_client.generate_template_suggestions(
            business_type,
            purpose
        )
        
        if not suggestions:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate template suggestions"
            )
        
        return APIResponse(
            success=True,
            message="Successfully generated template suggestions",
            data={"suggestions": suggestions}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating template suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{template_id}/preview", response_model=APIResponse)
async def preview_template(
    template_id: str,
    sample_data: dict
):
    """Preview a template with sample data."""
    try:
        template = db.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Process template with sample data
        processed_content = template.content
        for key, value in sample_data.items():
            placeholder = "{" + key + "}"
            processed_content = processed_content.replace(placeholder, str(value))
        
        return APIResponse(
            success=True,
            message="Template preview generated",
            data={"preview": processed_content}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating template preview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
