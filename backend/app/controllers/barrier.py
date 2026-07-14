from fastapi import APIRouter, Request

from app.core.dependencies import DbSession
from app.core.rate_limit import limiter
from app.schemas.barrier import BarrierCheckRequest, BarrierCheckResponse
from app.services.barrier_service import BarrierService

router = APIRouter(prefix="/barrier", tags=["barrier"])


@router.post(
    "/check-access",
    response_model=BarrierCheckResponse,
    summary="Check whether a registration number has an approved parking application",
)
@limiter.limit("30/minute")
async def check_access(
    request: Request, data: BarrierCheckRequest, db: DbSession
) -> BarrierCheckResponse:
    granted = await BarrierService(db).check_access(data.registration_number)
    return BarrierCheckResponse(
        registration_number=data.registration_number, access_granted=granted
    )
