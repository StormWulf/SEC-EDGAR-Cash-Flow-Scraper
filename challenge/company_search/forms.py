from django import forms


class TickerRequest(forms.Form):
    tickers = forms.CharField(widget=forms.Textarea, label='Company ticker symbols')
