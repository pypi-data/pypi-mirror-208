from django.forms import BaseForm, HiddenInput


def disable_form_field(form: BaseForm, field_name):
    if field_name in form.fields:
        form.fields[field_name].disabled = True
        form.fields[field_name].required = False


def hide_form_field(form: BaseForm, field_name):
    if field_name in form.fields:
        disable_form_field(form, field_name)
        form.fields[field_name].widget = HiddenInput()
