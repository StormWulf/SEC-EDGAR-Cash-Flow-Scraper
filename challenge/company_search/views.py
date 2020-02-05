from django.shortcuts import render
from .company import Company
from .forms import TickerRequest
from .models import Ticker, Filing, Report


def get_tickers(request):
    """
    Handles the GET and POST requests for the company ticker symbol text area
    """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TickerRequest(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            tickers = get_10k(form.cleaned_data['tickers'].split('\n'))

            # redirect to a new URL:
            return render(request, 'detail.html', {'obj': tickers})

    # if a GET (or any other method), we'll create a blank form
    else:
        form = TickerRequest()

    return render(request, 'company_input.html', {'form': form})


def get_10k(tickers):
    """
    Creates a Company object for the requested ticker symbols to obtain and store data from SEC EDGAR

    :param list tickers: list of requested company ticker symbols to query
    :return: list of requested company ticker symbols that users may click to find 10-k forms
    """
    for ticker in tickers:
        # instantiate Company class object for obtaining data from SEC EDGAR database
        company = Company(ticker)

        # create model for company ticker symbol if not already made
        t, _ = Ticker.objects.get_or_create(ticker=company.ticker)

        # iterate through the 10-k forms found for company ticker symbol
        for accession, cash_flow in company.forms.items():
            # store cik value, as it may be helpful to keep
            t.cik = company.cik
            t.save()

            # create model for the accession number if not already made
            filing, _ = Filing.objects.get_or_create(
                company=t, accession=accession
            )

            # iterate through the rows of the 10-k form
            for row in cash_flow.to_dict('records'):
                try:
                    # create model for each row of the 10-k form, passing values from DataFrame
                    report, _ = Report.objects.get_or_create(
                        accession=filing, **row
                    )
                except ValueError:
                    # avoid saving data for a header in the table
                    pass

    # return the list of company ticker symbols requested
    return list(set(str(t).strip() for t in Ticker.objects.all()))


def tickers(request):
    """
    Returns the list of company ticker symbols already saved in the database
    """
    obj = list(set(str(t).strip() for t in Ticker.objects.all()))
    return render(request, 'tickers.html', {'obj': obj})


def filings(request, ticker):
    """
    :param str ticker: the company ticker symbol to query
    :return: list of accession numbers for the user to query from the 10-k forms
    """
    obj = [
        str(filing) for filing in Filing.objects.filter(company__ticker=ticker)
    ]
    return render(request, 'list.html', {'ticker': ticker, 'obj': obj})


def detail(request, ticker, accession):
    """
    :param str ticker: only serves to let the user enter the ticker in the URL
    :param str accession: the SEC accession number for the 10-k form
    :return: the requested 10-k form with the requested accession number
    """
    obj = Report.objects.filter(accession=accession)
    return render(request, 'detail.html', {'obj': obj})
