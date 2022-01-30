from django import forms

TIME_SCOPES= [
    ('annually', 'Annually'),
    ('monthly', 'Monthly'),
    ]
    
class StatFilterForm(forms.Form):
    time_scope = forms.CharField(label='Time scope', widget=forms.Select(choices=TIME_SCOPES, attrs={'class': 'px-4 py-3 w-full rounded-md bg-gray-100 border-transparent focus:border-gray-500 focus:bg-white focus:ring-0 text-sm'}))

    