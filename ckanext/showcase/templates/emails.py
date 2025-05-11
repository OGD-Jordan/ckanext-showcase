from ckan.common import _, config
import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk

class EmailTemplates():
    @classmethod
    def site_title(cls):
        return config.get('ckan.site_title')
    

    @classmethod
    def site_url(cls):
        return config.get('ckan.site_url')

    @classmethod
    def render_template(cls, template_name, body_vars):
        return tk.render(f'emails/showcase/{template_name}.html', body_vars)

    
    @classmethod 
    def get_showcase_create(cls, body_vars):
        showcase = body_vars['showcase']
        body_vars['action_url'] = h.url_for('showcase_blueprint.read', id = showcase['id']),
        body_vars['site_title']= cls.site_title()
        body_vars['site_url']= cls.site_url()
        return cls.render_template('showcase_create', body_vars)


    @classmethod
    def get_status_update(cls, body_vars):
        body_vars['site_title']= cls.site_title()
        body_vars['site_url']= cls.site_url()
        showcase = body_vars['showcase']
        body_vars['action_url'] = h.url_for('showcase_blueprint.read', id = showcase['id']),
        return cls.render_template('status_update', body_vars)


class SubjectTemplates():
    @classmethod
    def get_showcase_create(cls, body_vars):
        showcase = body_vars['showcase']

        return {
            'en': _("Reuse case '%s' was submitted for review." % showcase['title']),
            'ar': "تم تقديم حالة إعادة الاستخدام '%s' للمراجعة." % showcase['title_ar']
        }

    @classmethod
    def get_status_update(cls, body_vars):
        showcase = body_vars['showcase']

        return {
            'en': _("Reuse case '%s' status was updated." % showcase['title']),
            'ar': "تم تحديث حالة حالة إعادة الاستخدام '%s'." % showcase['title_ar']
        }


class NotificationTemplates():
    @classmethod
    def compose_email_body(cls, lines_en, lines_ar):
        return {
            'en': "\n\n".join(lines_en),
            'ar': "\n\n".join(lines_ar),
        }

    @classmethod
    def get_showcase_create(cls, body_vars):
        showcase = body_vars['showcase']
        opening_word = body_vars['opening_word']

        lines_en = [
            _("%s reuse case was submitted to the Portal Supervisor for review." % opening_word),
        ]
        lines_ar = [
            "تم تقديم حالة إعادة الاستخدام إلى مشرف البوابة للمراجعة.",
        ]

        return cls.compose_email_body(lines_en, lines_ar)

    @classmethod
    def get_status_update(cls, body_vars):
        showcase = body_vars['showcase']
        status = showcase['status']

        title = showcase['title']
        lines_en = [
            _("Status of reuse case '%s' was updated to '%s'." % (title, status)),
        ]
        
        title = showcase['title_ar']
        lines_ar = [
            "تم تحديث حالة حالة إعادة الاستخدام '%s' إلى '%s'." % (title, status),
        ]

        return cls.compose_email_body(lines_en, lines_ar)
