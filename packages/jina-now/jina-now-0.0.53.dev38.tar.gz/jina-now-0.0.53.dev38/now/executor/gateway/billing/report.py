from hubble import Client as HubbleClient  # noqa
from hubble.payment.client import PaymentClient  # noqa
from jina.logging.logger import JinaLogger

from now.constants import (
    NOWGATEWAY_SEARCH_FEE_PRO_QUANTITY,
    NOWGATEWAY_SEARCH_FEE_QUANTITY,
)
from now.executor.abstract.auth.auth import _get_user_info  # noqa
from now.executor.gateway.billing.client import BillingClient

logger = JinaLogger(__file__)


class UserPaymentClient:
    user_id: str = None
    user_payment_client = None  # type: BillingClient

    @classmethod
    def init_user_id(cls, user_id: str):
        logger.info('** Entered init_user_id() **')
        cls.user_id = user_id
        cls.user_payment_client = BillingClient(user_id=user_id)
        logger.info('** Exited init_user_id() **')


def report_search_usage(token=None):
    logger.info('** Entered report_search_usage() **')
    payment_client = UserPaymentClient.user_payment_client
    payment_client.report(
        quantity_basic=NOWGATEWAY_SEARCH_FEE_QUANTITY,
        quantity_pro=NOWGATEWAY_SEARCH_FEE_PRO_QUANTITY,
    )
