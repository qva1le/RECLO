from src.models.users import UsersOrm
from src.schemas.subscriptions import SubscriptionStatusOut
from src.services.base import BaseService


class SubscriptionService(BaseService):
    async def activate_subscription(self, user_id: int, months: int) -> UsersOrm:
        ...

    async def get_user_subscription_status(self, user_id: int) -> SubscriptionStatusOut:
        ...