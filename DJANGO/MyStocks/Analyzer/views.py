from .forms import StockDataForm, SASAccountForm
from .models import DataSet, SASAccount
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import FileResponse, HttpResponseNotFound, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, FormView, CreateView, ListView, DetailView, UpdateView, DeleteView
import keyring
import logging
import os
import yfinance as yf
import subprocess
import shutil

logger = logging.getLogger(__name__)
BASE_DIR = settings.BASE_DIR # Access BASE_DIR from settings

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
        ticker = ticker,
        start_date = start_date,
        end_date = end_date,
        filename = filename,
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
        return FileResponse(open(file_path, 'rb'), as_attachment = True)
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
                username = sas_username,
                email=sas_email
            )
            sas_account.save()  # Save the SAS account to the database

            return redirect('Analyzer:index')  # Redirect after successful form submission
        return render(request, 'Analyzer/add_sas_account.html', {'form': form})

@login_required
def sas_account_list_view(request):
    sas_accounts = SASAccount.objects.filter(user = request.user)
    return render(request, 'Analyzer/sas_account_list.html', {'sas_accounts': sas_accounts})
        
class SASAccountDetailView(DetailView):
    model = SASAccount
    template_name = 'Analyzer/sas_account_detail.html'
    context_object_name = 'sas_account'

class RunSASScriptView(View):
    template_name = 'Analyzer/run_sas_script.html'

    def get(self, request, pk):
        # Get the SAS account for the given user (by primary key)
        sas_account = get_object_or_404(SASAccount, pk=pk)

        # Get the list of .sas files from the SAS directory and its subfolders
        sas_folder = os.path.join(BASE_DIR, "SAS")
        sas_files = []
        for root, dirs, files in os.walk(sas_folder):
            for file in files:
                if file.endswith(".sas"):
                    relative_path = os.path.relpath(os.path.join(root, file), sas_folder)
                    sas_files.append(relative_path)

        # Get the list of .csv files from the DataSets folder
        datasets_folder = os.path.join(BASE_DIR, "DataSets")
        csv_files = []
        for root, dirs, files in os.walk(datasets_folder):
            for file in files:
                if file.endswith(".csv"):
                    relative_path = os.path.relpath(os.path.join(root, file), datasets_folder)
                    csv_files.append(relative_path)

        # Combine the lists
        all_files = sas_files + csv_files

        return render(request, self.template_name, {'sas_account': sas_account, 'all_files': all_files})

    def post(self, request, pk):
        # Get the SAS account for the given user (by primary key)
        sas_account = get_object_or_404(SASAccount, pk=pk)

        # Get the selected filenames from the form (multi-select)
        filenames = request.POST.getlist('filenames')  # Changed to getlist for multiple files

        prefix = "automatedsas"

        # Build the command to run the script via subprocess for each selected file
        command = [
            'python', os.path.join(BASE_DIR, "Python", "interact_sas.py"),  # Full path to the Python script
            prefix,
            sas_account.email  # First argument: SAS email
        ]

        # Append each selected file to the command
        command.extend(filenames)

        try:
            # List to store the prefixed filenames for cleanup
            prefixed_files = []

            # Loop over each file and create a copy with a prefixed name
            for filename in filenames:
                # Determine the folder based on the file extension
                folder = "SAS" if filename.endswith(".sas") else "DataSets"
                # Full original path
                original_file = os.path.join(BASE_DIR, folder, filename)
                
                # Add the prefix and create a new filename
                prefixed_filename = f"{prefix}-{filename}"
                prefixed_file = os.path.join(BASE_DIR, folder, prefixed_filename)
                
                # Copy the original file to the new prefixed file
                shutil.copy(original_file, prefixed_file)
                
                # Store the prefixed file path for later deletion
                prefixed_files.append(prefixed_file)

            # Run the command using subprocess
            result = subprocess.run(command, capture_output = True, text = True)

            # Check if the script was successful
            if result.returncode == 0:
                 # Add a success message with the script output
                messages.success(request, f"SAS script executed successfully. Output: {result.stdout}")
                # Redirect to success page with a success message
                return redirect("/")
            else:
                messages.error(request, f"An error occurred: {result.stderr}")
                return redirect("/")
            
        except Exception as e:
            messages.error(request, f"Failed to run the SAS script: {str(e)}")
            return redirect("/")
        
        finally:
            # Delete the prefixed files
            for prefixed_file in prefixed_files:
                if os.path.exists(prefixed_file):
                    os.remove(prefixed_file)