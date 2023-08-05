from datetime import datetime, timezone
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    WAITING = "waiting"
    SUCCESS = "success"
    FAILURE = "failure"
    CODE_GENERATED = "code_generated"


def auto_order_number() -> str:
    order_number = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")[:-4]
    return order_number


def parse_order_number(order_number: str) -> str:
    if "_" in order_number:
        return order_number.split("_")[0]
    return order_number[:16]
