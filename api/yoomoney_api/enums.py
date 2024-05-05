from enum import Enum


class PaymentStatus(Enum):
    """Статус платежа"""

    SUCCESS = "success"
    REFUSED = "refused"
    IN_PROGRESS = "in_progress"

    BROKEN = None
