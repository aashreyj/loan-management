from django.urls import path
from .views import *

urlpatterns = [
    path('create-request', CreateLoanView.as_view()),
    path('approve/<id>', ApproveLoanView.as_view()),
    path('edit/<id>', EditLoanView.as_view()),
    path('filter', FilterLoanViewSet.as_view({
        'post': 'list',
    })),
]
