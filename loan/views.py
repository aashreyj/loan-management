from datetime import datetime, timedelta

from django.contrib.auth.models import User
from loan_management.permission import IsAdmin, IsAgent
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from .models import Loan, State
from .serializers import LoanRequestSerializer, LoanSerializer
from .utils import set_if_not_none


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
        creation = data.get('created_at', datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
        tenure = data['tenure']

        creation_date = datetime.strptime(creation, '%Y-%m-%dT%H:%M:%S').date()
        completion_date = creation_date + timedelta(days=30)

        data['date_of_completion'] = completion_date.strftime('%Y-%m-%d')

        user = User.objects.get(id=data['customer'])
        
        # create new loan object with given params
        loan_request = Loan.objects.create(amount=data['amount'],
                                            interest_rate=data['interest_rate'],
                                            tenure=data['tenure'],
                                            created_at=creation,
                                            state=data['state'],
                                            customer=user,
                                            date_of_completion=data['date_of_completion'])
        if loan_request is None:
            return Response({'message': "Something went wrong", 'error': True}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        loan_request.save()
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


#viewset for returning issue managements filtered by request parameters
class FilterLoanViewSet(ViewSet):

    def get_queryset(self, request):
        #getting request parameters and setting None for those that are missing
        tenure = self.request.data.get('tenure', None)
        create_date = self.request.data.get('created_at', None)
        status = self.request.data.get('state', None)
        
        #empty dictionary to contain the final filter parameters
        data = {}

        #set filter parameters if they are not None in the request body
        set_if_not_none(data, 'tenure', tenure)
        set_if_not_none(data, 'created_at', create_date)
        set_if_not_none(data, 'state', status)
        
        #apply filter to queryset and sort in order of latest first
        loan = Loan.objects.filter(**data)

        # customer can only see their own loans
        if request.user.groups.filter(name='customer').exists():
            loan = loan.filter(customer=request.user)
        
        # return queryset
        return loan

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        serializer = LoanSerializer(queryset, many=True)
        permission_classes = [IsAuthenticated,]
    
        #if serialized data is empty
        if len(serializer.data) == 0:
            return Response({'message': "No data matched given filters", 'error': True}, status=status.HTTP_404_NOT_FOUND)
        
        #create response object and send to client as response
        response_data = dict()
        response_data['message'] = "Data Collected"
        response_data['error'] = False
        response_data['data'] = serializer.data

        return Response(response_data, status=status.HTTP_200_OK)
