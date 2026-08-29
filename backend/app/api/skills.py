from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SkillCreate, SkillResponse
from app import crud

router = APIRouter()

@router.get("", response_model=List[SkillResponse])
def list_skills(db: Session = Depends(get_db)):
    """List all available skills with icons, descriptions, and categories."""
    skills = crud.get_all_skills(db)
    return [
        SkillResponse(
            id=s.id,
            name=s.name,
            display_name=s.display_name,
            description=s.description,
            icon=s.icon,
            category=s.category,
            parameters_schema=s.parameters_schema
        )
        for s in skills
    ]

@router.post("", response_model=SkillResponse)
def register_skill(skill_in: SkillCreate, db: Session = Depends(get_db)):
    """Register or update an AI skill/tool."""
    skill = crud.create_or_update_skill(db, skill_in)
    return SkillResponse(
        id=skill.id,
        name=skill.name,
        display_name=skill.display_name,
        description=skill.description,
        icon=skill.icon,
        category=skill.category,
        parameters_schema=skill.parameters_schema
    )
