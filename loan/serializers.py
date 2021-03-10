from rest_framework.serializers import ModelSerializer
from .models import State, Loan
from loan_management.serializers import UserSerializer

class LoanRequestSerializer(ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            'amount',
            'interest_rate',
            'tenure',
            'customer',
        ]

class StateSerializer(ModelSerializer):
    class Meta:
        model = State
        exclude = [
            'description'
        ]

class LoanSerializer(ModelSerializer):
    state = StateSerializer()
    customer = UserSerializer()
    class Meta:
        model = Loan
        fields = '__all__'
