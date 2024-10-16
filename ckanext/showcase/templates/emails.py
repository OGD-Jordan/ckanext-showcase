from ckan.common import _, config
import ckan.lib.helpers as h


class EmailTemplates():
    @classmethod
    def site_title(cls):
        return config.get('ckan.site_title')
    

    @classmethod
    def site_url(cls):
        return config.get('ckan.site_url')


    @classmethod
    def footer_lines(cls):
        return [
            _("Have a nice day."),
            "---",
            _("Message sent by %s (%s)" % (cls.site_title(), cls.site_url()))
        ]

    @classmethod
    def compose_email_body(cls, lines, body_vars):
        user_name = body_vars['user_name']

        text = "\n\n".join(
            [_("Dear %s," % user_name)] + lines + cls.footer_lines()
            )
        return text

    
    @classmethod
    def get_showcase_create(cls, body_vars):
        showcase = body_vars['showcase']
        opening_word = body_vars['opening_word']
        action_url = h.url_for('showcase_blueprint.read', id = showcase['id']),


        lines = [
            _("%s resuse case was submitted to Portal Supervisor for review." % opening_word),
            _("You can check the current status of your resuse case at %s" % cls.site_url() + action_url[0]),
        ]

        return cls.compose_email_body(lines, body_vars)


    @classmethod
    def get_status_update(cls, body_vars):
        showcase = body_vars['showcase']
        action_url = h.url_for('showcase_blueprint.read', id = showcase['id']),

        lines = [
            _("Status of reuse case \'%s\' was updated to %s." % (showcase['display_title'], showcase['status'])),
            _("You can check the current status of resuse at %s" % cls.site_url() + action_url[0]),
        ]

        return cls.compose_email_body(lines, body_vars)


class SubjectTemplates():
    @classmethod
    def get_showcase_create(cls, body_vars):
        showcase = body_vars['showcase']

        return  _("Reuse case \'%s\' was submitted for review." % showcase['display_title'])


    @classmethod
    def get_status_update(cls, body_vars):
        showcase = body_vars['showcase']

        return _("Reuse case \'%s\' status was updated." % showcase['display_title']),



class NotificationTemplates():
    @classmethod
    def compose_email_body(cls, lines, body_vars):
        text = "\n\n".join(lines)
        return text

    
    @classmethod
    def get_showcase_create(cls, body_vars):
        showcase = body_vars['showcase']
        opening_word = body_vars['opening_word']


        lines = [
            _("%s resuse case was submitted to the Portal Supervisor for review." % opening_word),
        ]

        return cls.compose_email_body(lines, body_vars)

    @classmethod
    def get_status_update(cls, body_vars):
        showcase = body_vars['showcase']

        lines = [
            _("Status of reuse case \'%s\' was updated to {showcase['status']}." % showcase['display_title']),
        ]

        return cls.compose_email_body(lines, body_vars)

