from .. import ty
from ..models import (
    BrokerDeleting,
    BrokerReading,
    BrokerRegistering,
    BrokerRegistrationCreating,
    BrokerRegistrationReturning,
    BrokerReturning,
    BrokerUpdating,
)
from .base import ModelClient


class Broker(
    ModelClient[
        BrokerRegistering,
        BrokerReading,
        BrokerUpdating,
        BrokerDeleting,
        BrokerReturning,
        BrokerReturning,
    ]
):
    Creating = BrokerRegistering
    Reading = BrokerReading
    Updating = BrokerUpdating
    Deleting = BrokerDeleting
    Returning = BrokerReturning

    class Token(ty.BaseModel):
        token: str

    def create(
        self, data: ty.Optional[BrokerRegistrationCreating] = None, **kwargs: ty.Any
    ) -> BrokerRegistrationReturning:
        data = data if data else BrokerRegistrationCreating(**kwargs)
        res = self.request(
            "POST",
            endpoint="create",
            data=data,
            return_model=BrokerRegistrationReturning,
        )
        return ty.cast(BrokerRegistrationReturning, res)

    async def create_async(
        self, data: ty.Optional[BrokerRegistrationCreating] = None, **kwargs: ty.Any
    ) -> BrokerRegistrationReturning:
        data = data if data else BrokerRegistrationCreating(**kwargs)
        res = await self.request_async(
            "POST",
            endpoint="create",
            data=data,
            return_model=BrokerRegistrationReturning,
        )
        return ty.cast(BrokerRegistrationReturning, res)

    def register(
        self, data: ty.Optional[BrokerRegistering] = None, **kwargs: ty.Any
    ) -> BrokerReturning:
        data = data if data else BrokerRegistering(**kwargs)
        res = self.request(
            "POST",
            endpoint="register",
            data=data,
            return_model=BrokerReturning,
        )
        return ty.cast(BrokerReturning, res)

    async def register_async(
        self, data: ty.Optional[BrokerRegistering] = None, **kwargs: ty.Any
    ) -> BrokerReturning:
        data = data if data else BrokerRegistering(**kwargs)
        res = await self.request_async(
            "POST",
            endpoint="register",
            data=data,
            return_model=BrokerReturning,
        )
        return ty.cast(BrokerReturning, res)
