from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException

from ..models_api import (
    ProcessCreationInput, ProcessCreationResponse, 
    OutlineUpdateRequest, OutlineUpdateResponse,
    RetrievalStartRequest, RetrievalStartResponse,
    RetrievalStatusResponse, CompositionStartResponse, ArticleResponse
)
from ..services.process_service import ProcessService
from ..services.status_manager import ProcessStatusManager, status_manager_instance # Singleton instance
from ..core_integrator import AgentIntegrator, agent_integrator_instance # Singleton instance
from ..dependencies import get_status_manager # If we prefer dependency injection for manager

router = APIRouter()

# Instantiate service with dependencies
# This could also be done via FastAPI Depends if services had more complex deps
_process_service_instance = ProcessService(status_manager=status_manager_instance, agent_integrator=agent_integrator_instance)


def get_process_service() -> ProcessService:
    # In a more complex app, this could resolve dependencies for ProcessService itself
    return _process_service_instance

@router.post("/start", response_model=ProcessCreationResponse)
async def create_process_and_generate_outline(
    creation_input: ProcessCreationInput,
    service: ProcessService = Depends(get_process_service)
):
    """Initiate a new article generation process and get the initial outline."""
    return await service.create_new_process(creation_input)

@router.post("/{process_id}/outline", response_model=OutlineUpdateResponse)
async def update_outline(
    process_id: str,
    update_request: OutlineUpdateRequest,
    service: ProcessService = Depends(get_process_service)
):
    """Update the outline for a given process ID."""
    return await service.update_process_outline(process_id, update_request)

@router.post("/{process_id}/retrieval/start", response_model=RetrievalStartResponse)
async def start_retrieval(
    process_id: str,
    retrieval_request: RetrievalStartRequest,
    background_tasks: BackgroundTasks,
    service: ProcessService = Depends(get_process_service)
):
    """Start the iterative retrieval process for the given process ID."""
    return await service.start_iterative_retrieval(process_id, retrieval_request, background_tasks)

@router.get("/{process_id}/retrieval/status", response_model=RetrievalStatusResponse)
async def get_retrieval_status(
    process_id: str,
    service: ProcessService = Depends(get_process_service)
):
    """Get the current status of the iterative retrieval process."""
    return await service.get_retrieval_status_for_process(process_id)

@router.post("/{process_id}/compose/start", response_model=CompositionStartResponse)
async def start_composition(
    process_id: str,
    background_tasks: BackgroundTasks,
    service: ProcessService = Depends(get_process_service)
):
    """Start the final article composition process."""
    return await service.start_article_composition(process_id, background_tasks)

@router.get("/{process_id}/article", response_model=ArticleResponse)
async def get_article(
    process_id: str,
    service: ProcessService = Depends(get_process_service)
):
    """Get the composed article and its status."""
    return await service.get_composed_article(process_id)
