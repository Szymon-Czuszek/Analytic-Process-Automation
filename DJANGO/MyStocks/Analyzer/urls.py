# urls.py for the Analyzer app
from django.urls import path
from . import views

app_name = 'Analyzer'  # Define the namespace

urlpatterns = [
    path("", views.index, name="index"),
    path('download-stock-data/', views.stock_data_view, name='download_stock_data'),
    path('list/', views.dataset_list_view, name='list'),
    path('download-file/<str:filename>/', views.download_file, name='download_file'),
    path("dataset_detail/<int:pk>", views.DataSetDetailView.as_view(), name = "dataset_detail"),
    path("update_dataset/<int:pk>", views.DataSetUpdateView.as_view(), name = "update_dataset"),
    path("delete_dataset/<int:pk>", views.DataSetDeleteView.as_view(), name = "delete_dataset"),
    path("signup/", views.SignUpView.as_view(), name = "signup"),
    path("profile/", views.profile, name = "profile"),
    path('add-sas-account/', views.AddSASAccountView.as_view(), name='add_sas_account'),
    path('sas-accounts/', views.sas_account_list_view, name='sas_account_list'),
    path('sas-account/<int:pk>/', views.SASAccountDetailView.as_view(), name='sas_account_detail'),
    path('run-sas-script/<int:pk>/', views.RunSASScriptView.as_view(), name='run_sas_script'),
] # Path expects a class!
