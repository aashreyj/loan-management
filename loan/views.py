from django.contrib.auth.models import User
from loan_management.permission import IsAdmin, IsAgent
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Loan, State
from .serializers import LoanSerializer, LoanRequestSerializer


# handle new loan request creation processing
class CreateLoanView(APIView):
    permission_classes = [IsAuthenticated & IsAgent]

    def post(self, request, *args, **kwargs):
        # validate incoming request
        serialized_data = LoanRequestSerializer(data=request.data)
        data = dict()

        # if request is valid, save data
        if serialized_data.is_valid():
            data = serialized_data.data
        else:
            return Response({'message': serialized_data.errors, 'error': True}, status=status.HTTP_400_BAD_REQUEST)
        
        # new request always has NEW state
        new_state = State.objects.get(name='new')
        data['state'] = new_state

        # calculate expected date of completion
        creation = data['created_at']
        tenure = data['tenure']
        
        # create new loan object with given params
        loan_request = Loan.objects.create(data)
        if loan_request is None:
            return Response({'message': "Something went wrong", 'error': True}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = LoanSerializer(instance=loan_request)

        # return response
        return Response({'message': "Loan Request Created", 'error': False, 'data': response.data}, status=status.HTTP_201_CREATED)


# handle approve loan requests
class ApproveLoanView(APIView):
    permission_classes = [IsAuthenticated & IsAdmin]

    def get(self, request, id, *args, **kwargs):
        # get id of the loan that is to be approved
        if not Loan.objects.filter(id=id).exists():
            return Response({'message': "No or Invalid Loan ID Given", 'error': True}, status=status.HTTP_400_BAD_REQUEST)
        
        # get loan from id
        loan_object = Loan.objects.get(id=id)
        approved_state = State.objects.get(name='approved')
        rejected_state = State.objects.get(name='rejected')
        
        # check if loan was rejected
        if loan_object.state == rejected_state:
            return Response({'message': "Loan was Rejected", 'error': True}, status=status.HTTP_400_BAD_REQUEST)

        # otherwise change state of the loan to APPROVED
        loan_object.state = approved_state
        loan_object.save()
        serialized = LoanSerializer(instance=loan_object)

        # return response
        return Response({'message': "Loan was Approved", 'error': False, 'data': serialized.data}, status=status.HTTP_200_OK)


# handle edit loan requests
class EditLoanView(APIView):
    permission_classes = [IsAuthenticated & IsAgent]

    def patch(self, request, id, *args, **kwargs):
        # check if loan with given id exists
        if not Loan.objects.filter(id=id).exists():
            return Response({'message': "Loan with given id not found", 'error': True}, status=status.HTTP_400_BAD_REQUEST)
        
        # get loan object that is to be updated
        loan_object = Loan.objects.get(id=id)
        approved_state = State.objects.get(name='approved')
        rejected_state = State.objects.get(name='rejected')

        # approved or rejected loans cannot be updated
        if loan_object.state == approved_state or loan_object.state == rejected_state:
            return Response({'message': "Loan was Approved or Rejected and cannot be modified", 'error': True}, status=status.HTTP_400_BAD_REQUEST)
        
        # validate incoming params
        serialized = LoanSerializer(loan_object, data=request.data, partial=True)
        
        # if request is valid, save changes and return successful response
        if serialized.is_valid():
            serialized.save()
            return Response({'message': "Changes made", 'error': False, 'data': serialized.data}, status=status.HTTP_202_ACCEPTED)
        
        # else return error response
        return Response({'message': serialized.errors, 'error': True}, status=status.HTTP_400_BAD_REQUEST)


# view to handle filtering requests
class FilterLoanView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request, *args, **kwargs):
        # get request params for filtering
        serialized_data = LoanSerializer(data=request.data)

        # if serializer data is not valid, return error
        if not serialized_data.is_valid():
            return Response({'message': serialized_data.errors, 'error': True}, status=status.HTTP_400_BAD_REQUEST)

        # response object
        response_data = dict()
        response_data['message'] = "Data Retrieved"
        response_data['error'] = False
        response_data['data'] = list()

        # filter loans on the basis of request data
        loans = Loan.objects.filter(serialized_data.data)

        # if user is a customer then he can only see his own loans
        if request.user.groups.filter(name='customer').exists():
            loans = loans.filter(user=request.user)
        
        # collect all loans after filtering
        for loan in loans:
            response_data['data'].append(loan)
        
        return Response(response_data, status=status.HTTP_200_OK)