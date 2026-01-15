from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Optional

from app.services.core.database import get_db
from app.middleware.auth import verify_clerk_token

from app.services.core.gamification.gamification_service import gamification_service
from app.services.core.gamification.career_manager import career_manager

router = APIRouter()

@router.get("/tree")
async def get_career_tree() -> Dict[str, Any]:
    """
    Get the static definition of the Career Tree.
    Frontend uses this to render the map (Nodes, Connections, Positions).
    """
    return {
        "nodes": career_manager.get_all_nodes(),
        "ranks": career_manager.params.get("ranks", {})
    }

@router.get("/status")
async def get_user_gamification_status(
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's RPG status: Level, XP, Stats, Unlocked Nodes.
    """
    return await gamification_service.get_user_status(db, auth_user_id)

@router.post("/setup")
async def setup_user_profile(
    target_role: str = Body(..., embed=True),
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize or Update user's Gamification Profile (Target Role).
    Triggered by Onboarding Quiz.
    """
    progress = await gamification_service.get_or_create_progress(db, auth_user_id)
    progress.target_role = target_role
    await db.commit()
    
    return {"status": "success", "target_role": target_role}

@router.post("/debug/complete-node")
async def debug_complete_node(
    node_id: str,
    score: int = 100,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Debug endpoint to force-complete a node and trigger XP/Level up.
    """
    # Mock metrics
    metrics = {
        "technical": score,
        "communication": score,
        "problem_solving": score,
        "experience": score, 
        "professionalism": score,
        "cultural_fit": score
    }
    
    return await gamification_service.complete_node(db, auth_user_id, node_id, score, metrics)
