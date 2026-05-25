from app.models import ServiceTypeBase
import uuid


class ServicePublic(ServiceTypeBase):
    id: uuid.UUID
    
class ServiceCreate(ServiceTypeBase):
    pass