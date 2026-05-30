from django import forms

class DateFilterForm(forms.Form):
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )

    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )