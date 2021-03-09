from django.urls import path
from .views import *

urlpatterns = [
    path('create-request', CreateLoanView.as_view()),
    path('approve/<id>', ApproveLoanView.as_view()),
    path('edit/<id>', EditLoanView.as_view()),
    path('filter', FilterLoanView.as_view()),
]
