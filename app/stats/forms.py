from django import forms

TIME_SCOPES = [
    ('annually', 'Annually'),
    ('monthly', 'Monthly'),
    ]
    
TLDS = [
    ('global', 'None specified'),
    ('com', '.com'),
    ('net', '.net'),
    ('fr', '.fr'),
    ('org', '.org'),
    ('de', '.de'),
    ('nl', '.nl'),
    ('uk', '.uk'),
    ('ru', '.ru'),
    ('be', '.be'),
    ('it', '.it'),
]

class StatFilterForm(forms.Form):
    time_scope = forms.CharField(label='Time scope', widget=forms.Select(choices=TIME_SCOPES, attrs={'class': 'px-6 py-3 w-full rounded-md bg-gray-100 border-transparent focus:border-gray-500 focus:bg-white focus:ring-0 text-sm'}))
    tld = forms.CharField(label='Top-Level Domain', widget=forms.Select(choices=TLDS, attrs={'class': 'px-6 py-3 w-full rounded-md bg-gray-100 border-transparent focus:border-gray-500 focus:bg-white focus:ring-0 text-sm'}))

    