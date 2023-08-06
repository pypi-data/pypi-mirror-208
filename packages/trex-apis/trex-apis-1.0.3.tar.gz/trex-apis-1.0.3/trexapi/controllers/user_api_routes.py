'''
Created on 7 Jul 2021

@author: jacklok
'''

from flask import Blueprint, request
import logging
from trexlib.utils.log_util import get_tracelog
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.user_models import User
from trexadmin.libs.http import create_rest_message
from trexadmin.libs.http import StatusCode
from werkzeug.datastructures import ImmutableMultiDict
from trexapi.forms.user_api_forms import UserRegistrationForm, UserUpdateForm
from trexapi.conf import APPLICATION_NAME, APPLICATION_BASE_URL
from trexmail.email_helper import trigger_send_email
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.models.datastore.reward_models import CustomerEntitledVoucher,\
    CustomerPointReward, CustomerEntitledTierRewardSummary
from trexapi.utils.api_helpers import generate_user_auth_token
from trexapi.decorators.api_decorators import user_auth_token_required
from trexadmin.libs.decorators import elapsed_time_trace
from flask.json import jsonify

user_api_bp = Blueprint('user_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/users')

logger = logging.getLogger('debug')


@user_api_bp.route('/register', methods=['POST'])
def user_register():
    logger.debug('user_register: ---user_register---')
    
    try:
        user_data_in_json   = request.get_json()
        logger.debug('user_register: user_data_in_json=%s', user_data_in_json)
        
        register_user_form  = UserRegistrationForm(ImmutableMultiDict(user_data_in_json))
        if register_user_form.validate():
            logger.debug('user_register:  registration input is valid')
            db_client = create_db_client(caller_info="user_register")
            
            registered_user_acct    = None
            
            with db_client.context():
                email           = register_user_form.email.data
                name            = register_user_form.name.data
                mobile_phone    = register_user_form.mobile_phone.data
                birth_date      = register_user_form.birth_date.data
                gender          = register_user_form.gender.data
                password        = register_user_form.password.data
                
                birth_date = datetime.strptime(birth_date, '%d-%m-%Y')
                
                logger.debug('email=%s', email)
                logger.debug('name=%s', name)
                logger.debug('mobile_phone=%s', mobile_phone)
                logger.debug('birth_date=%s', birth_date)
                logger.debug('gender=%s', gender)
                logger.debug('password=%s', password)
                
                checking_registered_user_acct = User.get_by_email(email)
                if checking_registered_user_acct is None:
                    if is_not_empty(mobile_phone):
                        checking_registered_user_acct = User.get_by_mobile_phone(mobile_phone)
                        if checking_registered_user_acct is None:
                            registered_user_acct = User.create(name=name, 
                                                               email=email, 
                                                               mobile_phone=mobile_phone, 
                                                               birth_date=birth_date,
                                                               gender=gender,
                                                               password=password, 
                                                               create_email_vc=True, 
                                                               create_mobile_phone_vc=True
                                                               )
                            logger.debug('new registered_user_acct=%s', registered_user_acct)
                        else:
                            if checking_registered_user_acct.is_mobile_phone_verified==True:
                                return create_rest_message('Mobile Phone have been taken', status_code=StatusCode.BAD_REQUEST)
                    else:
                        registered_user_acct = User.create(name=name, 
                                                               email=email, 
                                                               birth_date=birth_date,
                                                               gender=gender,
                                                               password=password, 
                                                               create_email_vc=True, 
                                                               create_mobile_phone_vc=True
                                                               )
                        
                        logger.debug('new registered_user_acct=%s', registered_user_acct)
                        
                else:
                    return create_rest_message('Email have been taken', status_code=StatusCode.BAD_REQUEST)
                
                                
            if registered_user_acct is not None:
                
                send_email_verification_code_email(registered_user_acct)
                (expiry_datetime, token)    = generate_user_auth_token(registered_user_acct.user_id, registered_user_acct.reference_code)
                
                return create_rest_message(status_code=StatusCode.OK, 
                                           auth_token                           = token,
                                           reference_code                       = registered_user_acct.reference_code,
                                           email_vc_expiry_datetime             = str(registered_user_acct.email_vc_expiry_datetime),
                                           mobile_phone_vc_expiry_datetime      = str(registered_user_acct.mobile_phone_vc_expiry_datetime),
                                           )
            else:
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('user_register: user registration input is invalid')
            error_message = register_user_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('user_register: Fail to register user due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@user_api_bp.route('/update', methods=['POST'])
def user_update():
    logger.debug('user_update: ---user_register---')
    
    try:
        user_data_in_json   = request.get_json()
        logger.debug('user_update: user_data_in_json=%s', user_data_in_json)
        
        update_user_form  = UserUpdateForm(ImmutableMultiDict(user_data_in_json))
        if update_user_form.validate():
            logger.debug('update_user_form:  update input is valid')
            db_client = create_db_client(caller_info="user_update")
            
            with db_client.context():
                reference_code  = update_user_form.reference_code.data
                name            = update_user_form.name.data
                mobile_phone    = update_user_form.mobile_phone.data
                birth_date      = update_user_form.birth_date.data
                gender          = update_user_form.gender.data
                
                birth_date      = datetime.strptime(birth_date, '%d-%m-%Y')
                
                logger.debug('reference_code=%s', reference_code)
                logger.debug('name=%s', name)
                logger.debug('mobile_phone=%s', mobile_phone)
                logger.debug('birth_date=%s', birth_date)
                logger.debug('gender=%s', gender)
                
                user_acct = User.get_by_reference_code(reference_code)
                if user_acct:
                    original_mobile_phone   = user_acct.mobile_phone
                    user_acct.name          = name
                    user_acct.mobile_phone  = mobile_phone
                    user_acct.birth_date    = birth_date
                    user_acct.gender        = gender
                    
                    if is_not_empty(mobile_phone):
                        if original_mobile_phone!=mobile_phone:
                            checking_mobile_phone_user_acct = User.get_by_mobile_phone(mobile_phone)
                            if checking_mobile_phone_user_acct is None:
                                User.update(user_acct)
                            else:
                                return create_rest_message('Mobile Phone have been taken', status_code=StatusCode.BAD_REQUEST)
                        else:
                            User.update(user_acct)
                                
                    
                else:
                    return create_rest_message('User account is not found', status_code=StatusCode.BAD_REQUEST)
                
                                
            return create_rest_message(status_code=StatusCode.OK)
            
        else:
            logger.warn('user_register: user registration input is invalid')
            error_message = update_user_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('user_register: Fail to update user due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    

@user_api_bp.route('/auth', methods=['POST'])
def auth_user():
    
    user_data_in_json   = request.get_json()
    email               = user_data_in_json.get('email')
    password            = user_data_in_json.get('password')
    
    if is_not_empty(email) and is_not_empty(password):
        db_client = create_db_client(caller_info="auth_user")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_email(email)
        
        if user_acct:
            logger.debug('auth_user: found user account by email=%s', email)    
            logger.debug('auth_user: found user account by password=%s', password)
            if user_acct.is_valid_password(password):
                (expiry_datetime, token)    = generate_user_auth_token(user_acct.user_id, user_acct.reference_code)
                
                response_data = {
                                    'auth_token'              : token,
                                    }
                    
                response_data.update(user_details_dict(user_acct))
                
                logger.debug('auth_user debug: response_data=%s', response_data)
                
                return create_rest_message(status_code=StatusCode.OK, 
                                           **response_data
                                           
                                           )
            
            else:
                logger.warn('auth_user: user password is invalid')
                return create_rest_message('User email or password is not match', status_code=StatusCode.BAD_REQUEST)
            
        else:
            return create_rest_message('User email or password is not match', status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('auth_user: user verify input is invalid')
        return create_rest_message('Missing email or password', status_code=StatusCode.BAD_REQUEST)
    
@user_api_bp.route('/verify-email', methods=['POST'])
def verify_email_account():
    
    user_data_in_json   = request.get_json()
    email               = user_data_in_json.get('email')
    verification_code   = user_data_in_json.get('verification_code')
    
    if is_not_empty(email) and is_not_empty(verification_code):
        db_client = create_db_client(caller_info="verify_email_account")
        user_acct = None
        
        logger.debug('verify_email_account: going to find user account by email=%s', email)
        
        with db_client.context():
            user_acct = User.get_by_email(email)
        
        if user_acct:
            logger.debug('verify_email_account: found user account by email=%s', email)    
            if user_acct.email_vc==verification_code:
                is_within_seconds = (user_acct.email_vc_expiry_datetime - datetime.now()).seconds
                if is_within_seconds>0:
                    with db_client.context():
                        user_acct.mark_email_verified()
                    return create_rest_message(status_code=StatusCode.OK)
                else:
                    return create_rest_message("Verification Code is expired already", status_code=StatusCode.BAD_REQUEST)
            
            else:
                logger.warn('verify_email_account: verification code is invalid')
                return create_rest_message("Invalid verification code", status_code=StatusCode.BAD_REQUEST)
            
        else:
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('verify_email_account: user verify input is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
    
@user_api_bp.route('/verify-email', methods=['POST'])
def verify_mobile_phone_account():
    
    user_data_in_json   = request.get_json()
    mobile_phone        = user_data_in_json.get('mobile_phone')
    verification_code   = user_data_in_json.get('verification_code')
    
    if is_not_empty(mobile_phone) and is_not_empty(verification_code):
        db_client = create_db_client(caller_info="verify_mobile_phone_account")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_mobile_phone(mobile_phone)
        
        if user_acct:
            logger.debug('verify_mobile_phone_account: found user account by mobile_phone=%s', mobile_phone)    
            if user_acct.mobile_phone_vc==verification_code:
                is_within_seconds = (user_acct.mobile_phone_vc_expiry_datetime - datetime.now()).seconds
                if is_within_seconds>0:
                    with db_client.context():
                        user_acct.mark_email_verified()
                    return create_rest_message(status_code=StatusCode.OK)
                else:
                    return create_rest_message("Verification Code is expired already", status_code=StatusCode.BAD_REQUEST)
            
            else:
                logger.warn('verify_mobile_phone_account: verification code is invalid')
                return create_rest_message("Invalid verification code", status_code=StatusCode.BAD_REQUEST)
            
        else:
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('verify_mobile_phone_account: user verify input is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)        

@user_api_bp.route('/register-as-customer', methods=['POST'])
#@user_auth_token_required
def register_user_as_customer():
    user_data_in_json           = request.get_json()
    reference_code              = user_data_in_json.get('reference_code')
    merchant_reference_code     = user_data_in_json.get('merchant_reference_code')
    outlet_key                  = user_data_in_json.get('outlet_key')
    
    logger.debug('register_user_as_customer: user_data_in_json=%s', user_data_in_json)
    
    try:
        if is_not_empty(reference_code):
            logger.debug('customer registration input is valid')
            db_client = create_db_client(caller_info="register_user_as_customer")
            
            created_customer        = None
            existing_user_acct      = None
            is_email_used           = False
            is_mobile_phone_used    = False
            merchant_act_key        = None
            
            merchant_acct           = None
            
            with db_client.context():
                existing_user_acct  = User.get_by_reference_code(reference_code)
                if existing_user_acct:
                    outlet              = Outlet.fetch(outlet_key)
                        
                    if outlet:
                        merchant_acct       = outlet.merchant_acct_entity
                        merchant_act_key    = outlet.merchant_acct_key  
                        logger.debug('Valid granted outlet key for merchant acct')
                        
                        created_customer = Customer.get_by_reference_code(reference_code, merchant_acct)
                         
                        if created_customer is None:
                            
                            
                            email           = existing_user_acct.email
                            mobile_phone    = existing_user_acct.mobile_phone
                            
                            logger.debug('email=%s', email)
                            logger.debug('mobile_phone=%s', mobile_phone)
                            
                            checking_customer = Customer.get_by_email(email, merchant_acct=merchant_acct) 
                            
                            if checking_customer:
                                is_email_used = True
                            else:
                                if is_not_empty(mobile_phone):
                                    checking_customer = Customer.get_by_mobile_phone(mobile_phone, merchant_acct=merchant_acct)
                                    if checking_customer:
                                        is_mobile_phone_used = True
                            
                            logger.debug('is_email_used=%s', is_email_used)
                            logger.debug('is_mobile_phone_used=%s', is_mobile_phone_used)
                            
                            if is_email_used == False and is_mobile_phone_used == False:
                            
                                created_customer = Customer.create_from_user(outlet, existing_user_acct, merchant_reference_code=merchant_reference_code)
                        
                            
                        logger.debug('created_customer=%s', created_customer)
                        
                    else:
                        logger.warn('Invalid granted outlet key or merchant account id')
                
                if created_customer:
                    
                    
                    
                    response_data = {
                                    'customer_key'              : created_customer.key_in_str,
                                    'registered_datetime'       : created_customer.registered_datetime.strftime("%d-%m-%Y %H:%M:%S"),
                                    'merchant_reference_code'   : created_customer.merchant_reference_code,
                                    'reference_code'            : created_customer.reference_code,
                                    'merchant_account_key'      : merchant_act_key,
                                    'company_name'              : merchant_acct.company_name,
                                    'outlet_key'                : outlet_key,  
                                    #'user_details'              : user_details_dict(existing_user_acct),
                                    }
                    
                    response_data.update(user_details_dict(existing_user_acct))
                    
                    logger.debug('register_user_as_customer debug: response_data=%s', response_data)
                    
                    return create_rest_message(status_code=StatusCode.OK, **response_data)
                    
                else:
                    if is_email_used==True:
                        return create_rest_message('Email have been taken', status_code=StatusCode.BAD_REQUEST)
                    
                    elif is_mobile_phone_used==True:
                        return create_rest_message('Mobile phone have been taken', status_code=StatusCode.BAD_REQUEST)
                    else:
                        return create_rest_message('Failed to register customer', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('customer registration input is invalid')
            
            return create_rest_message("Missing register customer input data", status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register customer due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

def user_details_dict(user_acct):
    is_email_verified           = user_acct.is_email_verified
    is_mobile_phone_verified    = user_acct.is_mobile_phone_verified
    
    logger.debug('user_details_dict debug: is_email_verified=%s', is_email_verified)
    logger.debug('user_details_dict debug: is_mobile_phone_verified=%s', is_mobile_phone_verified)
    
    email_vc_expiry_datetime            = None
    mobile_phone_vc_expiry_datetime     = None
    
    email_verified_datetime             = None
    mobile_phone_verified_datetime      = None
    
    if is_email_verified == False and is_not_empty(user_acct.email_vc_expiry_datetime):
        #vg_generated_datetime = user_acct.vg_generated_datetime.strftime(user_acct.vg_generated_datetime, '%d/%m/%Y, %H:%M:%S')
        email_vc_expiry_datetime = str(user_acct.email_vc_expiry_datetime)
    else:
        email_verified_datetime = str(user_acct.email_verified_datetime)
            
    if is_mobile_phone_verified == False and is_not_empty(user_acct.mobile_phone_vc_expiry_datetime):
        #vg_generated_datetime = user_acct.vg_generated_datetime.strftime(user_acct.vg_generated_datetime, '%d/%m/%Y, %H:%M:%S')
        mobile_phone_vc_expiry_datetime = str(user_acct.mobile_phone_vc_expiry_datetime)
    else:
        mobile_phone_verified_datetime = str(user_acct.mobile_phone_verified_datetime)
        
    birth_date_str = None
    if is_not_empty(user_acct.birth_date):
        birth_date_str = user_acct.birth_date.strftime('%d-%m-%Y')
         
    
    user_details = {
                       'reference_code'                       : user_acct.reference_code, 
                       'name'                                 : user_acct.name, 
                       'email'                                : user_acct.email, 
                       'gender'                               : user_acct.gender,
                       'birth_date'                           : birth_date_str,  
                       'is_email_verified'                    : is_email_verified,
                       'is_mobile_phone_verified'             : is_mobile_phone_verified,
                    }
    
    if is_not_empty(email_vc_expiry_datetime):
        user_details['email_vc_expiry_datetime'] = email_vc_expiry_datetime
        
    if is_not_empty(mobile_phone_vc_expiry_datetime):
        user_details['mobile_phone_vc_expiry_datetime'] = mobile_phone_vc_expiry_datetime
        
    
    if is_not_empty(email_verified_datetime):
        user_details['email_verified_datetime'] = email_verified_datetime
        
    if is_not_empty(mobile_phone_verified_datetime):
        user_details['mobile_phone_verified_datetime'] = mobile_phone_verified_datetime        
    
    return user_details
    
@user_api_bp.route('/customer/<reference_code>', methods=['GET'])
def read_user_customer_acct(reference_code):
    logger.debug('read_user_customer_acct: reference_code=%s', reference_code)
    
    try:
        if is_not_empty(reference_code):
            logger.debug('customer registration input is valid')
            db_client = create_db_client(caller_info="register_user_as_customer")
            
            customer                = None
            outlet_key              = request.headers.get('x-outlet-key')
            merchant_acct           = None
            existing_user_acct      = None
            
            logger.debug('outlet_key=%s', outlet_key)
            
            with db_client.context():
                outlet          = Outlet.fetch(outlet_key)
                    
                if outlet:
                    merchant_acct = outlet.merchant_acct_entity    
                    logger.debug('outlet.merchant_acct_key=%s', outlet.merchant_acct_key)
                    
                    
                    customer = Customer.get_by_reference_code(reference_code, merchant_acct)
                    existing_user_acct = User.get_by_reference_code(reference_code)
                     
                else:
                    logger.warn('Invalid granted outlet key or merchant account id')
                
                if customer:
                    
                    response_data = {
                                    'customer_key'              : customer.key_in_str,
                                    'registered_datetime'       : customer.registered_datetime.strftime("%d-%m-%Y %H:%M:%S"),
                                    'merchant_reference_code'   : customer.merchant_reference_code,
                                    'reference_code'            : customer.reference_code,
                                    'merchant_account_key'      : customer.registered_merchant_acct_key,
                                    'outlet_key'                : outlet_key,  
                                    #'user_details'              : user_details_dict(existing_user_acct), 
                                    }
                    
                    response_data.update(user_details_dict(existing_user_acct))
                    
                    logger.debug('read_user_customer_acct debug: response_data=%s', response_data)
                    
                    return create_rest_message(status_code=StatusCode.OK, **response_data)
                    
                else:
                    return create_rest_message('Customer account not found', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('customer registration input is invalid')
            
            return create_rest_message("Missing register customer input data", status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to read customer details due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    

@user_api_bp.route('/customer/<customer_key>/reward/summary', methods=['GET'])
@user_auth_token_required
@elapsed_time_trace(trace_key="read_customer_reward_summary")
def read_customer_reward_summary(customer_key):
    reference_code  = request.headers.get('x-reference-code')
    logger.debug('reference_code=%s', reference_code)
    #vouchers_list   = []
    tier_rewards    = []
    
    db_client = create_db_client(caller_info="read_customer_reward_summary")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            #customer_vouchers_list          = CustomerEntitledVoucher.list_all_by_customer(customer)
            customer_tier_reward_summary    = CustomerEntitledTierRewardSummary.list_tier_reward_summary_by_customer(customer)
            CustomerPointReward.list_by_customer(customer)
            '''
            if customer_vouchers_list:
                for v in customer_vouchers_list:
                    vouchers_list.append(v.to_dict())
            '''        
            if customer_tier_reward_summary:
                for v in customer_tier_reward_summary:
                    tier_rewards.append(v.to_dict())
    
    
    
    result = {
            'reference_code'    : reference_code,
            #'vouchers'          : vouchers_list,
            'tier_rewards'      : tier_rewards,
            'reward_summary'    : customer.reward_summary,
            'prepaid_summary'   : customer.prepaid_summary,
            'voucher_summary'   : customer.entitled_voucher_summary,
            }
    
    return jsonify(result)
    
@user_api_bp.route('/<reference_code>', methods=['GET'])
@user_auth_token_required
def read_user_acct(reference_code):
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="read_user_acct")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('verify_user: found user account by reference_code=%s', reference_code)    
            is_email_verified           = user_acct.is_email_verified
            is_mobile_phone_verified    = user_acct.is_email_verified
            
            email_vc_expiry_datetime             = None
            mobile_phone_vc_expiry_datetime      = None
            
            if is_email_verified == False:
                #vg_generated_datetime = user_acct.vg_generated_datetime.strftime(user_acct.vg_generated_datetime, '%d/%m/%Y, %H:%M:%S')
                email_vc_expiry_datetime = str(user_acct.email_vc_expiry_datetime)
                
            if is_mobile_phone_verified == False:
                #vg_generated_datetime = user_acct.vg_generated_datetime.strftime(user_acct.vg_generated_datetime, '%d/%m/%Y, %H:%M:%S')
                mobile_phone_vc_expiry_datetime = str(user_acct.mobile_phone_vc_expiry_datetime)    
                
            return create_rest_message(status_code=StatusCode.OK, 
                                       reference_code                       = user_acct.reference_code, 
                                       name                                 = user_acct.name, 
                                       email                                = user_acct.email, 
                                       is_email_verified                    = is_email_verified,
                                       is_mobile_phone_verified             = is_mobile_phone_verified,
                                       email_vc_expiry_datetime             = email_vc_expiry_datetime,
                                       mobile_phone_vc_expiry_datetime      = mobile_phone_vc_expiry_datetime,
                                       )
        else:
            logger.debug('user account is not found')
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('verify_user: user verify input is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    

@user_api_bp.route('/<reference_code>/joined-brands-list', methods=['GET'])
#@user_auth_token_required
def list_joined_brands(reference_code):
    limit           = request.args.get('limit')
    start_cursor    = request.args.get('start_cursor')
    
    logger.debug('limit=%s', limit)
    logger.debug('start_cursor=%s', start_cursor)
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="list_joined_brands")
        brands_list     = []
        user_acct       = None
        result_data     = {}
        
        if is_not_empty(limit):
            limit = int(limit)
        
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('verify_user: found user account by reference_code=%s', reference_code)
            
            
            
            with db_client.context():
                (customer_accts_list, next_cursor) = Customer.list_paginated_by_user_account(user_acct, start_cursor=start_cursor, limit=limit)
                
                for customer_acct in customer_accts_list:
                    merchant_acct = customer_acct.registered_merchant_acct
                    brands_list.append({
                                        'key'       : merchant_acct.key_in_str,
                                        'name'      : merchant_acct.brand_name,
                                        'logo_url'  : merchant_acct.logo_public_url,
                                        
                                        })
                    '''
                    brands_list.append({
                                        'key'       : merchant_acct.key_in_str,
                                        'name'      : merchant_acct.brand_name,
                                        'logo_url'  : merchant_acct.logo_public_url,
                                        
                                        })
                    brands_list.append({
                                        'key'       : merchant_acct.key_in_str,
                                        'name'      : merchant_acct.brand_name,
                                        'logo_url'  : merchant_acct.logo_public_url,
                                        
                                        })
                    brands_list.append({
                                        'key'       : merchant_acct.key_in_str,
                                        'name'      : merchant_acct.brand_name,
                                        'logo_url'  : merchant_acct.logo_public_url,
                                        
                                        })
                    brands_list.append({
                                        'key'       : merchant_acct.key_in_str,
                                        'name'      : merchant_acct.brand_name,
                                        'logo_url'  : merchant_acct.logo_public_url,
                                        
                                        })
                    brands_list.append({
                                        'key'       : merchant_acct.key_in_str,
                                        'name'      : merchant_acct.brand_name,
                                        'logo_url'  : merchant_acct.logo_public_url,
                                        
                                        })
                     '''                    
                result_data= {
                                'result'        : brands_list,
                                'count'         : len(brands_list),
                                }
                  
                if is_not_empty(next_cursor):
                    result_data['next_cursor'] = next_cursor  
        
        
        
        return create_rest_message(status_code=StatusCode.OK,
                                   **result_data, 
                                   )
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)   
    
@user_api_bp.route('/reset-email-vc', methods=['PUT'])
def reset_email_verification_code():
    email = request.args.get('email') or request.form.get('email') or request.json.get('email')
    
    logger.debug('reset_email_verification_code: going to reset email verification code by email=%s', email)
    
    if is_not_empty(email):
        db_client = create_db_client(caller_info="reset_email_verification_code")
        user_acct = None
        
        
        
        with db_client.context():
            user_acct = User.get_by_email(email)
        
        if user_acct:
            logger.debug('reset_email_verification_code: found user account by email=%s', email)    
            is_email_verified           = user_acct.is_email_verified
            
            logger.debug('reset_email_verification_code: is_email_verified=%s', is_email_verified)
            
            email_vc_expiry_datetime = None
            
            with db_client.context():
                user_acct.reset_email_vc()
            email_vc_expiry_datetime = user_acct.email_vc_expiry_datetime
                
                #send_email_verification_code_email(user_acct)
            
            logger.debug('reset_email_verification_code: email_vc_expiry_datetime=%s', email_vc_expiry_datetime)
            logger.debug('reset_email_verification_code: verification code=%s', user_acct.email_vc)
                
            return create_rest_message(status_code=StatusCode.OK, 
                                       email_vc_expiry_datetime          = str(email_vc_expiry_datetime),
                                       
                                       )
        else:
            return create_rest_message('Cannot find user by email %s' % email, status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('reset_email_verification_code: reference code is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 
    
@user_api_bp.route('/reset-mobile-phone-vc', methods=['PUT'])
def reset_mobile_phone_verification_code():
    mobile_phone = request.args.get('mobile_phone') or request.form.get('mobile_phone') or request.json.get('mobile_phone')
    if is_not_empty(mobile_phone):
        db_client = create_db_client(caller_info="reset_verification_code")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_mobile_phone(mobile_phone)
        
        if user_acct:
            logger.debug('reset_mobile_phone_verification_code: found user account by mobile_phone=%s', mobile_phone)    
            is_mobile_phone_verified           = user_acct.is_mobile_phone_verified
            mobile_phone_vc_expiry_datetime = None
            
            with db_client.context():
                user_acct.reset_mobile_phone_vc()
                
            logger.debug('reset_mobile_phone_verification_code: mobile_phone_vc_expiry_datetime=%s', mobile_phone_vc_expiry_datetime)
            logger.debug('reset_mobile_phone_verification_code: verification code=%s', user_acct.mobile_phone_vc)   
            return create_rest_message(status_code=StatusCode.OK, 
                                       mobile_phone_vc_expiry_datetime   = str(mobile_phone_vc_expiry_datetime),
                                       
                                       )
        else:
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('reset_mobile_phone_verification_code: mobile phone is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)  
    
@user_api_bp.route('/request-reset-password', methods=['POST'])
def request_reset_password_post():
    email = request.args.get('email') or request.form.get('email') or request.json.get('email')
    
    logger.debug('reset_password_request_post: going to reset email verification code by email=%s', email)
    
    if is_not_empty(email):
        db_client = create_db_client(caller_info="reset_email_verification_code")
        user_acct = None
        
        
        
        with db_client.context():
            user_acct = User.get_by_email(email)
        
        if user_acct:
            logger.debug('reset_password_request_post: found user account by email=%s', email)    
            is_email_verified           = user_acct.is_email_verified
            
            logger.debug('reset_email_verification_code: is_email_verified=%s', is_email_verified)
            
            if is_email_verified:
                with db_client.context():
                    user_acct.reset_password_request()
                
                send_reset_password_request_email(user_acct)
                
            return create_rest_message(status_code=StatusCode.OK
                                       
                                       )
        else:
            return create_rest_message('Cannot find user by email %s' % email, status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('reset_password_post: email is invalid')
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)                 


def send_email_verification_code_email(user_acct):
    message = '''
                Hi {name},
                
                
                Thanks for signing up with {application_name}!
                Your account has been created, you can login with email {email} in future. 
                
                Just one more step to get started! Please enter below code to activate your account .
                
                
                {verification_code}
                
                
                The code will be expired after 30 minutes.
                
                Cheers,
                {application_name} Team
                
                
                ***Please do not reply to this email. This is an auto-generated email.***
    
            '''.format(name=user_acct.name, email=user_acct.email, verification_code=user_acct.email_vc, application_name=APPLICATION_NAME)
    
    subject      = 'Email Verification from {application_name}'.format(application_name=APPLICATION_NAME)
    
    trigger_send_email(recipient_address = user_acct.email, subject=subject, message=message)
    '''
    send_email(sender           = DEFAULT_SENDER, 
                   to_address   = [user_acct.email], 
                   subject      = subject, 
                   body         = message,
                   app          = current_app
                   )
    '''
def send_reset_password_request_email(user_acct):
    reset_password_link = '{base_url}/user/reset-password-request/{request_reset_password_token}'.format(base_url=APPLICATION_BASE_URL, request_reset_password_token=user_acct.request_reset_password_token)
    
    message = '''
                Hi {name},
                
                
                Forgot your password? No worries.
                We received your request to reset the password for your account. 
                
                Just one more step to reset the password, please click the below link:
                
                
                {reset_password_link}
                
                
                
                Or copy and paste the URL into your web browser.
                
                Cheers,
                {application_name} Team
                
                
                ***Please do not reply to this email. This is an auto-generated email.***
    
            '''.format(name=user_acct.name, email=user_acct.email, 
                       reset_password_link=reset_password_link, 
                       application_name=APPLICATION_NAME)
    
    subject = 'Request to reset password to {application_name}'.format(application_name=APPLICATION_NAME)
            
    trigger_send_email(recipient_address = user_acct.email, subject=subject, message=message)
    '''
    send_email(sender           = DEFAULT_SENDER, 
                   to_address   = [user_acct.email], 
                   subject      = subject, 
                   body         = message,
                   app          = current_app
                   )    
    '''               