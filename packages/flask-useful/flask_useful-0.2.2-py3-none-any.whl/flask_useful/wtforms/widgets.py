from markupsafe import escape, Markup


class CheckboxGroup(object):
    """
    A widget for a group of checkboxes or radio buttons, depending on the type of elements.

    Attributes:
        inline (bool): Widgets are arranged in a row, not a list.
    """

    def __init__(self, inline=False):
        self.inline = inline

    def __call__(self, field, **kwargs):
        html = []
        css_class = 'form-check form-check-inline' if self.inline else 'form-check'

        for f in field:
            html.extend((
                f'<div class="{css_class}">',
                f(class_='form-check-input'),
                f.label(class_='form-check-label'),
                '</div>'
            ))

        return Markup(''.join(html))
