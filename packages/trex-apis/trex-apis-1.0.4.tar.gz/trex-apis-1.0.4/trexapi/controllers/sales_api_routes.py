from flask import Blueprint, request, session, jsonify 
from flask_restful import abort
import logging
from trexlib.utils.log_util import get_tracelog
from flask_restful import Api
from trexmodel.utils.model.model_util import create_db_client
#from flask.json import jsonify
from datetime import datetime, timedelta
from trexapi.decorators.api_decorators import auth_token_required,\
    outlet_key_required
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.models.datastore.user_models import User
from trexadmin.libs.http import create_rest_message
from trexadmin.libs.http import StatusCode
from trexmodel.models.datastore.merchant_models import Outlet,\
    MerchantAcct, MerchantUser
from werkzeug.datastructures import ImmutableMultiDict
from trexmodel.models.datastore.transaction_models import SalesTransaction

from trexapi.utils.reward_transaction_helper import create_sales_transaction,\
    redeem_reward_transaction, create_topup_prepaid_transaction
from trexapi.utils.api_helpers import get_logged_in_api_username
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexapi import conf
from trexmodel.models.datastore.prepaid_models import PrepaidSettings
from trexadmin.libs.jinja.common_filters import format_currency_with_currency_label_filter
from trexadmin.libs.flask.utils.flask_helper import get_merchant_configured_currency_details
from trexmodel import program_conf
from trexapi.forms.sales_api_forms import SalesTransactionForm
from trexlib.utils.crypto_util import encrypt
from trexapi.conf import EARN_INSTANT_REWARD_URL



sales_api_bp = Blueprint('sales_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/sales')

logger = logging.getLogger('debug')


@sales_api_bp.route('/ping', methods=['GET'])
def ping():
    return 'pong', 200

@sales_api_bp.route('/create-sales-transaction', methods=['PUT'])
@auth_token_required
@outlet_key_required
def post_sales_transaction():
    
    logger.info('---post_sales_transaction---')
    
    transaction_data_in_json   = request.get_json()
        
    logger.info('transaction_data_in_json=%s', transaction_data_in_json)
    
    transaction_form = SalesTransactionForm(ImmutableMultiDict(transaction_data_in_json))
    
    if transaction_form.validate():
        logger.debug('reward transaction data is valid')
        
        sales_amount        = float(transaction_form.sales_amount.data)
        tax_amount          = transaction_form.tax_amount.data
        invoice_id          = transaction_form.invoice_id.data
        remarks             = transaction_form.remarks.data
        invoice_details     = transaction_data_in_json.get('invoice_details')
        
        transact_datetime   = None
        
        
        if tax_amount is None:
            tax_amount = .0
        else:
            tax_amount = float(tax_amount)
         
        logger.debug('sales_amount=%s', sales_amount)
        logger.debug('tax_amount=%s', tax_amount)
        logger.debug('invoice_id=%s', invoice_id)
        logger.debug('remarks=%s', remarks)
        logger.debug('invoice_details=%s', invoice_details)
        
        db_client = create_db_client(caller_info="givea_reward")
        
        check_transaction_by_invoice_id = None
        
        if is_not_empty(invoice_id):
            with db_client.context():
                check_transaction_by_invoice_id = SalesTransaction.get_by_invoice_id(invoice_id)
        
        if check_transaction_by_invoice_id:
            return create_rest_message("The invoice id have been taken", status_code=StatusCode.BAD_REQUEST)
        else:
            transact_datetime_in_gmt    = transaction_form.transact_datetime.data
            merchant_username           = get_logged_in_api_username()
            
            
            if merchant_username:
                try:
                    with db_client.context():
                        transact_outlet         = Outlet.fetch(request.headers.get('x-outlet-key'))
                        merchant_acct           = transact_outlet.merchant_acct_entity
                        
                            
                        if transact_datetime_in_gmt:
                            transact_datetime    =  transact_datetime_in_gmt - timedelta(hours=merchant_acct.gmt_hour)
                            
                            now                  = datetime.utcnow()
                            if transact_datetime > now:
                                return create_rest_message('Transact datetime cannot be future', status_code=StatusCode.BAD_REQUEST)
                        
                        
                        
                        transact_merchant_user = MerchantUser.get_by_username(merchant_username)
                        
                        sales_transaction = create_sales_transaction( 
                                                                        transact_outlet     = transact_outlet, 
                                                                        sales_amount        = sales_amount,
                                                                        tax_amount          = tax_amount,
                                                                        invoice_id          = invoice_id,
                                                                        remarks             = remarks,
                                                                        transact_by         = transact_merchant_user,
                                                                        transact_datetime   = transact_datetime,
                                                                        invoice_details     = invoice_details,
                                                                    )
                        
                    if sales_transaction:
                        encrypted_transaction_id    = encrypt(sales_transaction.transaction_id)
                        logger.debug('EARN_INSTANT_REWARD_URL=%s', EARN_INSTANT_REWARD_URL)
                        entitled_url                = EARN_INSTANT_REWARD_URL.format(code=encrypted_transaction_id)
                        
                        transaction_details =  {
                                                "entitled_url"            : entitled_url,
                                                }
                            
                    return jsonify(transaction_details)
                except:
                    logger.error('Failed to proceed transaction due to %s', get_tracelog())
                    return create_rest_message('Failed to proceed transaction', status_code=StatusCode.BAD_REQUEST)
                            
            else:
                return create_rest_message('Missing transact user account', status_code=StatusCode.BAD_REQUEST)
        
    else:
        logger.warn('sales transaction data input is invalid')
        error_message = transaction_form.create_rest_return_error_message()
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
