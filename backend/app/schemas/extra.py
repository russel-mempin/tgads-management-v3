import uuid

from app.models import ExtraServiceBase


class ExtraPublic(ExtraServiceBase):
    id: uuid.UUID