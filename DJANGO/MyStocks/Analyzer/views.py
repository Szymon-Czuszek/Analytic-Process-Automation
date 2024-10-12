from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from .forms import StockDataForm
from .models import DataSet
from django.views.generic import TemplateView, FormView, CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
import yfinance as yf
from datetime import datetime
from django.http import FileResponse
import os
from django.shortcuts import render
from .models import SASAccount
# views.py for Analyzer app
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import keyring
from .forms import SASAccountForm
# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import SASAccount

import logging
logger = logging.getLogger(__name__)

from django.conf import settings  # Import settings this way
BASE_DIR = settings.BASE_DIR  # Access BASE_DIR from settings

# Create your views here.
def index(request):

    context = {}

    return render(request, "Analyzer/index.html", context = context)

def profile(request):

    context = {}

    return render(request, "Analyzer/profile.html", context = context)

# Add this function to your views.py
def dataset_list_view(request):
    datasets = DataSet.objects.all()  # Fetch all datasets from the database
    return render(request, 'Analyzer/list.html', {'datasets': datasets})  # Pass the datasets to the template

def download_stock_data(ticker, start_date):
    end_date = datetime.today().strftime('%Y-%m-%d')
    stock_data = yf.download(ticker, start=start_date, end=end_date)

    if stock_data.empty:
        return None, f"No data found for ticker: {ticker}. Please check the ticker symbol and try again."

    filename = f"{ticker}-{start_date}.csv"
    file_path = os.path.join(BASE_DIR, "DataSets", filename)
    stock_data.to_csv(file_path)

    # Save the dataset information in the database
    data_set = DataSet(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        filename=filename,
    )
    data_set.save()  # Save the record to the database

    logger.info(f"DataSet saved with ticker: {ticker} and filename: {filename}")

    return data_set, None  # Return the saved dataset and no error

def stock_data_view(request):
    if request.method == 'POST':
        form = StockDataForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker']
            start_date = form.cleaned_data['start_date']
            data_set, error = download_stock_data(ticker, start_date)

            if error:
                return render(request, 'Analyzer/stock_data.html', {'form': form, 'error': error})
            else:
                # Redirect after success
                return redirect('Analyzer:list')  # Redirect to the list view
    else:
        form = StockDataForm()

    return render(request, 'Analyzer/stock_data.html', {'form': form})

def download_file(request, filename):
    file_path = os.path.join(BASE_DIR, "DataSets", filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        return HttpResponseNotFound("File not found.")

class DataSetDetailView(DetailView):
    model = DataSet

class DataSetUpdateView(UpdateView):
    model = DataSet
    fields = "__all__"
    success_url = reverse_lazy("Analyzer:list")

class DataSetDeleteView(DeleteView):
    model = DataSet
    success_url = reverse_lazy("Analyzer:list")

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "Analyzer/signup.html"

@method_decorator(login_required, name='dispatch')
class AddSASAccountView(View):
    def get(self, request):
        form = SASAccountForm()
        return render(request, 'Analyzer/add_sas_account.html', {'form': form})

    def post(self, request):
        form = SASAccountForm(request.POST)
        if form.is_valid():
            sas_username = form.cleaned_data['sas_username']
            sas_email = form.cleaned_data['sas_email']
            sas_password = form.cleaned_data['sas_password']
            service_id = "SAS"

            # Save the SAS account to keyring using the entered email and username
            keyring.set_password(service_id, sas_email, sas_password)

            # Create a new SASAccount instance and save it to the database
            sas_account = SASAccount(
                user=request.user,  # Link to the logged-in user
                username=sas_username,
                email=sas_email
            )
            sas_account.save()  # Save the SAS account to the database

            return redirect('Analyzer:index')  # Redirect after successful form submission
        return render(request, 'Analyzer/add_sas_account.html', {'form': form})

@login_required
def sas_account_list_view(request):
    sas_accounts = SASAccount.objects.filter(user=request.user)
    return render(request, 'Analyzer/sas_account_list.html', {'sas_accounts': sas_accounts})