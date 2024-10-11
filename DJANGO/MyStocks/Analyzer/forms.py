from django import forms

# forms.py for Analyzer app

class StockDataForm(forms.Form):
    ticker = forms.CharField(max_length = 10, label = 'Ticker Symbol')
    start_date = forms.DateField(widget = forms.SelectDateWidget, label = 'Start Date')

class SASAccountForm(forms.Form):
    sas_username = forms.CharField(label = 'SAS Username', max_length = 255)
    sas_email = forms.EmailField(label = 'SAS Email', max_length = 255)
    sas_password = forms.CharField(label = 'SAS Password', widget = forms.PasswordInput)