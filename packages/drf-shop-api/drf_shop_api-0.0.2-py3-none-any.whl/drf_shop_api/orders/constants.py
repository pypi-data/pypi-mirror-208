from enum import Enum


class OrderStatus(Enum):
    CREATED = "Created"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    CANCELED = "Refunded"


class ShipmentStatus(Enum):
    CREATED = "Created"
    FULFILLED = "Fulfilled"


class PaymentStatus(Enum):
    UNCOMPLETED = "Uncompleted"
    COMPLETED = "Completed"
