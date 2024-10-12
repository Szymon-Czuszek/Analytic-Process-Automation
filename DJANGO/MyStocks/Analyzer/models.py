from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class DataSet(models.Model):
    ticker = models.CharField(max_length=10)  # Ticker symbol (e.g., 'AAPL')
    start_date = models.DateField()            # Start date for the data
    end_date = models.DateField()              # End date for the data (optional)
    filename = models.CharField(max_length=255) # Name of the file
    created_at = models.DateTimeField(auto_now_add=True) # Timestamp of creation

    def __str__(self):
        return f"{self.ticker} - {self.start_date} to {self.end_date}"

class SASAccount(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    username = models.CharField(max_length = 100)
    email = models.EmailField()

    def __str__(self):
        return self.username