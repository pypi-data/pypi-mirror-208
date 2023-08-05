from __future__ import annotations
import typing as t

from flask import views
from flask import request, url_for, redirect, render_template
from flask.typing import ResponseReturnValue
from flask_wtf import FlaskForm

from .utils import camel_to_list, make_url


class FormMixin(object):
    """
    Mixin to work with HTML-forms.

    Attributes:
        form_class (:py:class:`~flask_wtf.FlaskForm`):
            A reference to the base class of the form.
        success_endpoint (:obj:`str`):
            The endpoint to which to go if the form was processed successfully.
        success_endpoint_map (:obj:`dict`):
            Mapping the action name to an endpoint to navigate to if the form was successfully processed.
            The action name is the value of the value attribute of the submit button, or is specified manually.
    """

    form_class = None
    success_endpoint = None
    success_endpoint_map = None

    def get_form(self, *args: t.Any, **kwargs: t.Any) -> FlaskForm:
        """
        Returns:
            :py:class:`~flask_wtf.FlaskForm`: An instance of the form class.
        """
        return self.get_form_class()(*args, **kwargs)

    def get_form_class(self) -> t.Type[FlaskForm]:
        """
        Returns:
             :py:class:`~flask_wtf.FlaskForm`: A reference to the base class of the form.
        """
        if self.form_class is None:
            raise AttributeError(
                'You must assign the value of the attribute `form_class`, '
                f'or override the `{self.__class__.__name__}.get_form_class()` method.'
            )
        return self.form_class

    def form_valid(self, form):
        """Runs if the form is processed successfully."""
        raise NotImplementedError

    def form_invalid(self, form):
        """Runs if errors occurred while processing the form."""
        raise NotImplementedError

    def get_success_endpoint(self):
        """Returns the endpoint to which to go if the form was processed successfully."""
        if self.success_endpoint_map is not None:
            action_name = request.form.get('_action')
            return self.success_endpoint_map[action_name]

        if self.success_endpoint is not None:
            return self.success_endpoint

        raise AttributeError(
            'You must assign the value of the attribute `success_endpoint` or `success_endpoint_map`, '
            f'or override the `{self.__class__.__name__}.get_success_endpoint()` method.'
        )

    def make_redirect(self, obj=None):
        """
        Args:
            obj (object|dict): The object whose property values are used to build the URL.

        Returns:
            :class:`werkzeug.wrappers.Response`: The redirect to follow if the form was successfully processed.
        """
        endpoint = self.get_success_endpoint()
        success_url = url_for(endpoint) if obj is None else make_url(endpoint, obj)
        return redirect(success_url)

    def process_form(self):
        """
        Creates a form, validates and calls a method for further processing.

        Returns:
            :class:`werkzeug.wrappers.Response`: response object.
        """
        form = self.get_form()

        if form.validate_on_submit():
            return self.form_valid(form)

        return self.form_invalid(form)


class MethodView(views.MethodView):
    """
    Arguments:
        template_name (:obj:`str`):
            The name of the template, can be passed to the :py:meth:`~flask.views.View.as_view` method.

    Attributes:
        template_name (:obj:`str`): The name of the template.
    """

    template_name = None

    def __init__(self, template_name=None):
        if template_name:
            self.template_name = template_name

    def get_template_name(self) -> t.Union[str, t.List[str]]:
        """
        Returns the name of the template.

        If the template_name property is not set, the value will be generated automatically based on the class name.

        Example:
            >>> class MyEntityAction(MethodView): pass
            >>> view = MyEntityAction()
            >>> view.get_template_name()
            "my_entity/action.html"

        """
        if self.template_name is None:
            name = camel_to_list(self.__class__.__name__, lower=True)
            self.template_name = '{1}/{0}.html'.format(name.pop(), '_'.join(name))
        return self.template_name

    def render_template(self, **context: t.Any) -> str:
        """Render a template with passed context."""
        return render_template(self.get_template_name(), **context)


class FormView(MethodView, FormMixin):
    def get_object(self, *args: t.Any, **kwargs: t.Any) -> t.Optional[t.Any]:
        return None

    def get(self, *args: t.Any, **kwargs: t.Any) -> ResponseReturnValue:
        obj = self.get_object(*args, **kwargs)
        return self.render_template(obj=obj, form=self.get_form(obj=obj))

    def post(self, *args: t.Any, **kwargs: t.Any) -> ResponseReturnValue:
        obj = self.get_object(*args, **kwargs)
        form = self.get_form(obj=obj)

        if form.validate_on_submit():
            return self.form_valid(form, obj)

        return self.form_invalid(form, obj)

    def form_invalid(self, form: FlaskForm, obj: t.Any = None) -> ResponseReturnValue:
        """Runs if errors occurred while processing the form."""
        return self.render_template(obj=obj, form=form)

    def form_valid(self, form: FlaskForm, obj: t.Any = None) -> ResponseReturnValue:
        """Runs if the form is processed successfully."""
        raise NotImplementedError
