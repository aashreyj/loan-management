from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class State(models.Model):
    name = models.CharField(max_length=10)
    description = models.CharField(max_length=100, blank=True, null=True)


class Loan(models.Model):
    amount = models.IntegerField()
    interest_rate = models.IntegerField(default=10)
    tenure = models.IntegerField()
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    expected_date_of_completion = models.DateField()