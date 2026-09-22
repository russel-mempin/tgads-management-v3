from fastapi import APIRouter

from app.models import ExtraService

router = APIRouter(prefix="/services", tags=["services"], dependencies=[Depends(get_current_active_user)])


@router.get("/extras", response_model=list[ExtraService])
def read_all_extras(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_extras(db, offset=offset, limit=limit)