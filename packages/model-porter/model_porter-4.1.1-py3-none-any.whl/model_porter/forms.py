from django import forms
from django.core.signing import BadSignature, Signer
from django.utils.translation import gettext_lazy as _

__all__ = ['ImportForm', 'ConfirmImportForm', 'ConfirmImportManagementForm']


class ImportForm(forms.Form):
    import_file = forms.FileField(
        label=_("File to import"),
    )

    def __init__(self, allowed_extensions, *args, **kwargs):
        super().__init__(*args, **kwargs)

        accept = ",".join([".{}".format(x) for x in allowed_extensions])
        self.fields["import_file"].widget = forms.FileInput() #attrs={"accept": accept})

        uppercased_extensions = [x.upper() for x in allowed_extensions]
        allowed_extensions_text = ", ".join(uppercased_extensions)
        help_text = _("Supported formats: %(supported_formats)s.") % {
            "supported_formats": allowed_extensions_text,
        }
        self.fields["import_file"].help_text = help_text


class ConfirmImportManagementForm(forms.Form):
    """
    Store the import file name and input format in the form so that it can be used in the next step

    The initial values are signed, to prevent them from being tampered with.
    """

    import_file_name = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.signer = Signer()
        initial = kwargs.get("initial", {})
        for key in {"import_file_name"}:
            if key in initial:
                # Sign initial data so it cannot be tampered with
                initial[key] = self.signer.sign(initial[key])
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        for key in {"import_file_name"}:
            try:
                cleaned_data[key] = self.signer.unsign(cleaned_data[key])
            except BadSignature as e:
                raise forms.ValidationError(e.message)
        return cleaned_data


class ConfirmImportForm(ConfirmImportManagementForm):

    def __init__(self, repository, *args, **kwargs):
        super().__init__(*args, **kwargs)

