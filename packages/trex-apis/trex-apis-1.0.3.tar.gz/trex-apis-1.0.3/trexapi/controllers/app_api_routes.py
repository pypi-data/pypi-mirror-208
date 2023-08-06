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
from trexapi.forms.user_api_forms import UserRegistrationForm
from trexapi.conf import APPLICATION_NAME, APPLICATION_BASE_URL
from trexmail.email_helper import trigger_send_email
from trexmodel.models.datastore.admin_models import AppBannerFile
from trexlib.utils.common.common_util import sort_dict_list

app_api_bp = Blueprint('app_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/app')

logger = logging.getLogger('debug')


@app_api_bp.route('/settings', methods=['GET'])
def app_setting():
    logger.debug('---app_setting---')
    
    banner_file_list = []
    db_client = create_db_client(caller_info="app_setting")
    with db_client.context():
        
        result_listing = AppBannerFile.list()
        logger.debug('result_listing=%s', result_listing)
                
        if result_listing:
            for banner_file in result_listing:
                #banner_file_list.append(banner_file.to_dict(dict_properties=['banner_file_public_url','sequence'], show_key=False))
                banner_file_list.append({
                                        'image_url': banner_file.banner_file_public_url,
                                        'sequence': banner_file.sequence,
                                        })
                
    ##sorted_banner_file_list = sort_dict_list(banner_file_list, sort_attr_name='sequence')
    
    app_settings =  {
                        'banners': banner_file_list,
        
                    }
    '''
    return create_rest_message(status_code=StatusCode.OK,
                                               **app_settings,
                                               )
    '''
    return app_settings