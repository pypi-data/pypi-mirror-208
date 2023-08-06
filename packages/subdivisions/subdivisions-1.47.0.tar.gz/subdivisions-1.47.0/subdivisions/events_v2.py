from enum import Enum


class OrderEvents(Enum):
    ORDER_PROPOSAL_REQUEST = "order_proposal_request"
    ORDER_PROPOSAL_CALCULATED = "order_proposal_calculated"
    ORDER_PROPOSAL_ANALYZED = "order_proposal_analyzed"
    ORDER_PROPOSAL_AVAILABLE = "order_proposal_available"
    ORDER_PROPOSAL_ACCEPTED = "order_proposal_accepted"
    ORDER_SCHEDULE_REQUEST = "order_schedule_request"


class ERPEvent(Enum):
    NEW_ERP_DATA_AVAILABLE = "new_erp_data_available"


class CustomerEvents(Enum):
    REGISTERED = "registered"
    DATA_SOURCE_CONNECTED = "data_source_connected"
    VALIDATION_FINISHED = "validation_finished"


class BankEvent(Enum):
    NEW_BOLETOS_ISSUED = "new_boletos_issued"
