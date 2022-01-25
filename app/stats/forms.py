from django import forms

TIME_SCOPES= [
    ('annually', 'Annually'),
    ('monthly', 'Monthly'),
    ]
    
class StatFilterForm(forms.Form):
    time_scope = forms.CharField(label='Time scope', widget=forms.Select(choices=TIME_SCOPES))

    