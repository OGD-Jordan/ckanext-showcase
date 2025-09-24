import logging

import ckan.lib.uploader as uploader
import ckan.plugins.toolkit as tk
from ckanext.showcase.logic import notifiy
from ckanext.showcase.logic.action.action_decorator import notify_after_action
from ckanext.showcase.model import ShowcaseApprovalStatus
from ckan.common import _
import ckanext.showcase.logic.schema as showcase_schema
from ckanext.showcase.data.constants import *
from ckan.logic import validate as validate_decorator

log = logging.getLogger(__name__)


def showcase_update(context, data_dict):
    tk.check_access('ckanext_showcase_update',context, data_dict)

    data_dict['old_filename'] = data_dict.get('image_url','')
    image_data =  tk.h.single_image_upload(context, data_dict, upload_folder='showcase')
    data_dict.update(image_data)

    site_user = tk.get_action("get_site_user")({"ignore_auth": True}, {})
    updated_context = {'ignore_auth': True, 'user':site_user['name']}
    pkg = tk.get_action('package_update')(
        {**context.copy(), **updated_context}, 
        data_dict
        )

    tk.get_action('ckanext_showcase_status_update')(
        {**context.copy(), **updated_context}, 
        {"id": pkg.get("id",pkg.get("name", '')) }
    )

    return pkg


@validate_decorator(showcase_schema.showcase_status_update_schema)
def status_update(context, data_dict):
    tk.check_access('ckanext_showcase_status_update',context, data_dict)
    
    showcase_id = data_dict.get('id')
    status = data_dict.get('status', ApprovalStatus.PENDING)
    feedback = data_dict.get('feedback','') if status == ApprovalStatus.NEEDS_REVISION else ''

    update_status = ShowcaseApprovalStatus.update_status(
        showcase_id,
        feedback,
        status
    )
    
    if context.get('user', None) != 'default':
        notifiy.status_update(update_status.get('showcase_id', None))

    return {**update_status, 'id': update_status.get('showcase_id', None)}


