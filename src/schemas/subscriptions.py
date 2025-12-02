from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class SubscriptionPeriod(str, Enum):
    one_month = "1m"
    three_months = "3m"
    six_months = "6m"

class SubscriptionPurchaseIn(BaseModel):
    period: SubscriptionPeriod


class SubscriptionStatusOut(BaseModel):
    is_active: bool
    expires_at: datetime | None
    remaining_days: int | None



