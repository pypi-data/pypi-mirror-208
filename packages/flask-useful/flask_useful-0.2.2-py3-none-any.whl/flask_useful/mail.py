"""
The module contains functions for working with E-Mails.
"""

import typing as t

from flask import (
    render_template,
    render_template_string,
    Flask,
)
from flask_mail import (
    email_dispatched,
    Mail,
    Message,
)


__all__ = (
    'get_mail_instance',
    'render_html_message',
)


def get_mail_instance(app: t.Optional[Flask] = None) -> Mail:
    """Returns the configured instance of the Flask-Mail extension."""
    mail = Mail(app)
    email_dispatched.connect(email_dispatched_handler)
    return mail


def email_dispatched_handler(
    message: Message,
    app: Flask,
) -> None:
    """Logs messages to the console in debug mode."""
    if app.debug or app.config['MAIL_SUPPRESS_SEND']:
        app.logger.debug(message.as_string())


def make_template(
    base: str,
    blocks: t.Dict[str, str],
) -> str:
    """Creates a Jinja template on the fly."""
    result = ['{%- extends "', base, '" -%}']

    for name, body in blocks.items():
        result.extend(['{% block ', name, ' %}', body, '{% endblock %}'])

    return ''.join(result)


def render_html_message(
    template: str,
    blocks: t.Optional[t.Dict[str, str]] = None,
    /,
    **context: t.Any,
) -> str:
    """
    Returns the body of the email in HTML format.

    Arguments:
        template (str): The name of the template to render.
        blocks (dict): The content of the blocks to be replaced.
        context (dict): The variables to make available in the template.
    """
    if blocks is None:
        return render_template(template, **context)
    _template = make_template(template, blocks)
    return render_template_string(_template, **context)
