from enum import Enum


class UserStatus(str, Enum):
    pending_email = "pending_email"
    active = "active"
    blocked = "blocked"
    deleted = "deleted"

class CodeStatus(str, Enum):
    email_verify = "email_verify"
    password_reset = "password_reset"

class SellerApplicationsStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class BusinessType(str, Enum):
    ip = "ip"
    ooo = "ooo"
    self_employed = "self_employed"

class ShopType(str, Enum):
    brand = "brand"
    designer = "designer"
    merch = "merch"
    resale = "resale"

class ShopStatus(str, Enum):
    active = "active"
    blocked = "blocked"


