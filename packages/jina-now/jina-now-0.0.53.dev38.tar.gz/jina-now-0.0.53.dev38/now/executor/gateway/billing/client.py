import os
import traceback
from json import JSONDecodeError

from hubble.excepts import BaseError
from hubble.payment.client import PaymentClient  # noqa
from jina.logging.logger import JinaLogger

from now.utils.common.helpers import current_time

logger = JinaLogger(__file__)


class BillingClient:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.m2m_token = None
        self.payment_client = None
        self.session_token = None
        self.init_payment_client()

    def init_payment_client(self):
        try:
            logger.info('** Entered init_payment_client() **')
            self.m2m_token = os.environ.get('M2M')
            self.payment_client = PaymentClient(m2m_token=self.m2m_token)
            self.session_token = self.payment_client.get_user_token(
                user_id=self.user_id
            )['data']
        except (BaseError, JSONDecodeError) as e:
            logger.error(f'Error while initialising payment client for user, {e}')
            traceback.print_exc()
            raise e
        except Exception as e:  # noqa
            logger.error(
                f'Found an unhandled exception while initialising payment client, {e}'
            )
            traceback.print_exc()
            raise e

    def report(self, quantity_basic, quantity_pro):
        logger.info('Time of reporting for credits usage: {}'.format(current_time()))
        app_id = 'search'
        try:
            acc_status = self.get_account_status()
            product_id = acc_status['internal_product_id']
            logger.info(
                f'Credits before: {acc_status["credits"]} & product_id: {product_id}'
            )
            if product_id == 'free-plan':
                quantity = quantity_basic
            else:
                quantity = quantity_pro
            if self.can_charge(acc_status):
                self.payment_client.report_usage(  # noqa
                    self.session_token,
                    app_id,
                    product_id,
                    quantity,
                    meta={
                        'appId': 'search-app',
                        'feeType': 'search-fee',
                        'source': 'gateway',
                        'planType': product_id,
                        'flowId': os.environ.get('FLOW_ID'),
                        'flowNamespace': 'jnamespace-'
                        + os.environ.get('K8S_NAMESPACE_NAME', ''),
                        'timeNow': current_time(),
                    },
                )
                logger.info(f'**** `{round(quantity, 3)}` credits charged ****')
                acc_status = self.get_account_status()
                logger.info(f'Credits after: {acc_status["credits"]}')
            else:
                logger.info(f'**** Could not charge. Check payment summary ****')
            logger.info(f'User account status:\n{acc_status}')
        except Exception as e:
            # Do not continue with request if payment fails
            logger.error(f'Error while reporting credits usage {e}')
            traceback.print_exc()
            raise e

    def get_account_status(self):
        resp = self.payment_client.get_summary(
            token=self.session_token, app_id='search'
        )
        has_payment_method = resp['data'].get('hasPaymentMethod', False)
        user_credits = resp['data'].get('credits', None)
        internal_product_id = resp['data'].get('internalProductId', None)
        user_account_status = resp['data'].get('userAccountStatus', None)
        return {
            'has_payment_method': has_payment_method,
            'credits': user_credits,
            'internal_product_id': internal_product_id,
            'user_account_status': user_account_status,
        }

    @staticmethod
    def can_charge(user_acc_status):
        return (
            (user_acc_status['credits'] is not None and user_acc_status['credits'] > 0)
            or user_acc_status['has_payment_method']
        ) and user_acc_status['user_account_status'] == 'active'
