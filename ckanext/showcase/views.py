# -*- coding: utf-8 -*-

from ckanext.showcase.data.constants import ApprovalStatus
from flask import Blueprint
from markupsafe import Markup


import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
import ckan.views.dataset as dataset
import ckan.lib.captcha as captcha
from ckan.common import g

import ckanext.showcase.utils as utils

showcase = Blueprint('showcase_blueprint', __name__)


def index():
    return dataset.search(utils.DATASET_TYPE_NAME)


class CreateView(dataset.CreateView):
    def _prepare(self):  # noqa
        context = cast(Context, {
            u'model': model,
            u'session': model.Session,
            u'user': current_user.name,
            u'auth_user_obj': current_user,
            u'save': self._is_save()
        })
        try:
            tk.check_access('ckanext_showcase_create', context)
        except tk.NotAuthorized:
            return base.abort(403,  Markup(
                _(u'In order to share a reuse case, you must be registered on the portal.<br><br><a href="%(url)s">Click here to login</a>')
                % {'url': h.url_for('user.login')}
              )
            )
        return context
    
    def get(self, data=None, errors=None, error_summary=None):
        return super(CreateView, self).get(utils.DATASET_TYPE_NAME, data,
                                           errors, error_summary)

    def post(self):
        context = self._prepare()

        data_dict = dataset.clean_dict(
            dataset.dict_fns.unflatten(
                dataset.tuplize_dict(dataset.parse_params(tk.request.form))))
        data_dict.update(
            dataset.clean_dict(
                dataset.dict_fns.unflatten(
                    dataset.tuplize_dict(dataset.parse_params(
                        tk.request.files)))))
        data_dict['type'] = utils.DATASET_TYPE_NAME

        try:
            captcha.check_recaptcha(request)
        except captcha.CaptchaError:
            error_msg = _(u'Bad Captcha. Please try again.')
            h.flash_error(error_msg)
            return self.get(data_dict)
        except:
            error_msg = _(u'Some Issue with Captcha Connection.')
            h.flash_error(error_msg)
            return self.get(data_dict)


        try:
            pkg_dict = tk.get_action('ckanext_showcase_create')(context,
                                                                data_dict)

        except tk.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            data_dict['state'] = 'none'
            return self.get(data_dict, errors, error_summary)

        # redirect to manage datasets
        url = h.url_for('showcase_blueprint.manage_datasets',
                        id=pkg_dict['name'])
        return h.redirect_to(url)


def manage_datasets(id):
    return utils.manage_datasets_view(id)


def delete(id):
    return utils.delete_view(id)


def read(id):
    return utils.read_view(id)


class EditView(dataset.EditView):
    def get(self, id, data=None, errors=None, error_summary=None):
        context = self._prepare()
        utils.check_edit_view_auth(id)

        package_type = 'showcase'
        try:
            view_context = context.copy()
            view_context['for_view'] = True
            pkg_dict = tk.get_action(u'ckanext_showcase_show')(
                view_context, {u'id': id})
            context[u'for_edit'] = True
            old_data = tk.get_action(u'ckanext_showcase_show')(context, {u'id': id})
            # old data is from the database and data is passed from the
            # user if there is a validation error. Use users data if there.
            if data:
                old_data.update(data)
            data = old_data
        except (dataset.NotFound, dataset.NotAuthorized):
            return base.abort(404, _(u'Dataset not found'))
        assert data is not None

        pkg = context.get(u"package")
        resources_json = h.dump_json(data.get(u'resources', []))
        user = current_user.name
        try:
            tk.check_access(u'ckanext_showcase_update', context, {'id':id})
        except dataset.NotAuthorized:
            return base.abort(
                403,
                _(u'User %r not authorized to edit %s') % (user, id)
            )
        
        errors = errors or {}
        form_snippet = dataset._get_pkg_template(
            u'package_form', package_type=package_type
        )
        form_vars: dict = {
            u'data': data,
            u'errors': errors,
            u'error_summary': error_summary,
            u'action': u'edit',
            u'dataset_type': package_type,
            u'form_style': u'edit'
        }
        errors_json = h.dump_json(errors)

        # TODO: remove
        g.pkg = pkg
        g.resources_json = resources_json
        g.errors_json = errors_json

        dataset._setup_template_variables(
            context, {u'id': id}, package_type=package_type
        )

        # we have already completed stage 1
        form_vars[u'stage'] = [u'active']

        edit_template = dataset._get_pkg_template(u'edit_template', package_type)
        return base.render(
            edit_template,
            extra_vars={
                u'form_vars': form_vars,
                u'form_snippet': form_snippet,
                u'dataset_type': package_type,
                u'pkg_dict': pkg_dict,
                u'pkg': pkg,
                u'resources_json': resources_json,
                u'form_snippet': form_snippet,
                u'errors_json': errors_json
            }
        )


    def post(self, id):
        if tk.check_ckan_version(min_version='2.10.0'):
            context = self._prepare()
        else:
            # Remove when dropping support for 2.9
            context = self._prepare(id)

        utils.check_edit_view_auth(id)

        data_dict = dataset.clean_dict(
            dataset.dict_fns.unflatten(
                dataset.tuplize_dict(dataset.parse_params(tk.request.form))))
        data_dict.update(
            dataset.clean_dict(
                dataset.dict_fns.unflatten(
                    dataset.tuplize_dict(dataset.parse_params(
                        tk.request.files)))))

        data_dict['id'] = id
        try:
            pkg = tk.get_action('ckanext_showcase_update')(context, data_dict)
        except tk.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.get(id, data_dict, errors, error_summary)

        tk.c.pkg_dict = pkg

        # redirect to showcase details page
        url = h.url_for('showcase_blueprint.manage_datasets',
                id=pkg['name'])
        return h.redirect_to(url)


def dataset_showcase_list(id):
    return utils.dataset_showcase_list(id)


def upload():
    return utils.upload()




showcase.add_url_rule('/showcase', view_func=index, endpoint="index")
showcase.add_url_rule('/showcase/new', view_func=CreateView.as_view('new'), endpoint="new")
showcase.add_url_rule('/showcase/delete/<id>',
                      view_func=delete,
                      methods=['GET', 'POST'],
                      endpoint="delete")
showcase.add_url_rule('/showcase/<id>', view_func=read, endpoint="read")
showcase.add_url_rule('/showcase/edit/<id>',
                      view_func=EditView.as_view('edit'),
                      methods=['GET', 'POST'],
                      endpoint="edit")
showcase.add_url_rule('/showcase/manage_datasets/<id>',
                      view_func=manage_datasets,
                      methods=['GET', 'POST'],
                      endpoint="manage_datasets")
showcase.add_url_rule('/dataset/showcases/<id>',
                      view_func=dataset_showcase_list,
                      methods=['GET', 'POST'],
                      endpoint="dataset_showcase_list")
showcase.add_url_rule('/showcase_upload',
                      view_func=upload,
                      methods=['POST'])




from flask import Blueprint, request
from ckan.lib.helpers import helper_functions as h


import logging
import ckan.lib.base as base
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
import ckan.plugins.toolkit as tk
import ckan.model as model

import ckanext.showcase.logic.schema as schema

from typing import  Union, cast
from flask import Blueprint
from flask.views import MethodView
from ckan.common import current_user, _, request

from ckan.types import Context, Response
from flask import request
from functools import partial
from ckan.lib.helpers import Page


_get_action = logic.get_action
_tuplize_dict = logic.tuplize_dict
_clean_dict = logic.clean_dict
_parse_params = logic.parse_params


log = logging.getLogger(__name__)


def dashboard_list():
    utils.check_dashboard_list_view_auth()
    context = cast(Context, {
        u'model': model,
        u'session': model.Session,
        u'user': current_user.name,
        u'auth_user_obj': current_user,
        })

    data_dict = {**request.args}
    
    data_dict, errors = dict_fns.validate(data_dict, schema.showcase_search_schema(), context)

    sort = data_dict.get('sort', 'metadata_created desc')
    limit = data_dict.get('limit', 20)
    showcases = tk.get_action('ckanext_showcase_search')(context, {**data_dict, 'sort':sort, 'limit': limit})
    
    showcase_statistics = tk.get_action('ckanext_showcase_statics')(context, data_dict)


    params_nopage = [
        (k, v) for k, v in request.args.items(multi=True)
        if k != u'page'
        ]

    pager_url = partial(utils.pager_url, params_nopage)

    pagination = Page(
        collection=showcases['items'],
        page=data_dict.get('page', 1),
        url=pager_url,
        item_count=showcases.get('total'),
        items_per_page=limit,
        )
    pagination.items=showcases['items']


    return base.render(u'showcase/dashboard/search.html',
        extra_vars={
            "showcases": showcases.get('items'),
            "count": showcases.get('total'),
            u'errors': errors,
            'data_dict': data_dict,
            'selected_sorting': sort,
            'page': pagination,
            'statistics': showcase_statistics,
            }
        )


class StatusUpdate(MethodView):
    def _prepare(self) -> Context:
        context = cast(Context, {
            u'model': model,
            u'session': model.Session,
            u'user': current_user.name,
            u'auth_user_obj': current_user,
        })
        return context

    def get(self,
            id: str,
            data = None,
            errors = None,
            error_summary = None
            ) -> Union[Response, str]:
        utils.check_status_update_view_auth(id)
        context = self._prepare()
        
        showcase = _get_action(u'ckanext_showcase_show')(context, {u'id': id})
        showcase_datasets = _get_action(u'ckanext_showcase_package_list')(context, {u'showcase_id': id})
        showcase_status = _get_action(u'ckanext_showcase_status_show')(context, {u'id': id})

        data = {**showcase_status, **(data or {})}

        user_info = _get_action(u'user_management_show')({**context, 'ignore_auth': True}, {u'id': showcase.get('creator_user_id')})
        
        errors = errors or {}
        errors_json = h.dump_json(errors)
        
        
        return base.render(
            'showcase/dashboard/actions.html',
            extra_vars={
                u'data': data,
                u'errors': errors,
                u'error_summary': error_summary,
                
                u'showcase': showcase,
                'showcase_datasets': showcase_datasets,
                'showcase_status': showcase_status,
                
                u'user_info': user_info,
                u'errors_json': errors_json
            }
        )

    def post(self, id):
        context = self._prepare()

        data_dict = _clean_dict(
            dict_fns.unflatten(
                _tuplize_dict(_parse_params(tk.request.form))))
        data_dict.update(
            _clean_dict(
                dict_fns.unflatten(
                    _tuplize_dict(_parse_params(
                        tk.request.files)))))

        data_dict['id'] = id

        try:
            updated_showcase = tk.get_action('ckanext_showcase_status_update')(context, data_dict)

        except tk.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.get(id, data_dict, errors, error_summary)


        url = h.url_for('showcase_blueprint.dashboard_read', id=id)
        return h.redirect_to(url)
    


def dashboard_read(id):
    context = {
        'model': model,
        'session': model.Session,
        'user': tk.g.user or tk.g.author,
        'auth_user_obj': tk.g.userobj
    }
    data_dict = {'id': id}

    try:
        showcase = tk.get_action('ckanext_showcase_show')(context, data_dict)
        showcase_datasets = _get_action(u'ckanext_showcase_package_list')(context, {u'showcase_id': id})
        user_info = tk.get_action(u'user_management_show')({**context, 'ignore_auth': True}, {u'id': showcase.get('creator_user_id')})

    except tk.ObjectNotFound:
        return tk.abort(404, _('Reuse Case not found'))
    except tk.NotAuthorized:
        return tk.abort(401, _('User not authorized to view this Reuse Case'))

    return tk.render(u'showcase/dashboard/detail.html', 
        extra_vars={
            "showcase": showcase,
            "user_info": user_info,
            "showcase_datasets": showcase_datasets,
            }
        )


showcase.add_url_rule('/dashboard/showcase/', view_func=dashboard_list, endpoint="dashboard_index")
showcase.add_url_rule('/dashboard/showcase/update/<id>', view_func=StatusUpdate.as_view('edit'),
                      methods=['GET', 'POST'],
                      endpoint="dashboard_update")
showcase.add_url_rule('/dashboard/showcase/<id>', view_func=dashboard_read, endpoint="dashboard_read")



def get_blueprints():
    return [showcase]
