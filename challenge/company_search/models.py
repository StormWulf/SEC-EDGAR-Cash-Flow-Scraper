from django.db import models

# Create your models here.


class Ticker(models.Model):
    """
    Model for each of the company ticker symbols
    """
    ticker = models.CharField(max_length=4, primary_key=True)
    cik = models.PositiveIntegerField(default=None, null=True, blank=True)

    def __str__(self):
        return self.ticker

    def __int__(self):
        return self.cik


class Filing(models.Model):
    """
    Model for tracking the SEC accession numbers
    """
    company = models.ForeignKey(
        Ticker, to_field='ticker', on_delete=models.CASCADE
    )
    accession = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.accession


class Report(models.Model):
    """
    Model for each row of a 10-k form, linked to an SEC accession number
    """
    accession = models.ForeignKey(
        Filing, to_field='accession', on_delete=models.CASCADE
    )
    field = models.CharField(max_length=10000)
    period_1 = models.FloatField(null=True)
    period_1_name = models.CharField(max_length=100)
    period_2 = models.FloatField(null=True)
    period_2_name = models.CharField(max_length=100)
    period_3 = models.FloatField(null=True)
    period_3_name = models.CharField(max_length=100)
