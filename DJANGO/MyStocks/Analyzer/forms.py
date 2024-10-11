from django import forms

class StockDataForm(forms.Form):
    ticker = forms.CharField(max_length=10, label='Ticker Symbol')
    start_date = forms.DateField(widget=forms.SelectDateWidget, label='Start Date')