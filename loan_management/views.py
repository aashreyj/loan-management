from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .permission import IsAdmin, IsAgent

from .serializers import UserSerializer

# handle new user creation requests
class RegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        
        #extract request data and validate all fields
        
        #username should not be blank
        username = request.data.get('username', None)
        if username is None:
            return Response({'message': "Blank username field", 'error': True}, status=status.HTTP_400_BAD_REQUEST)
        
        #password1 should not be blank
        password = request.data.get('password', None)
        if password is None:
            return Response({'message': "Blank password field", 'error': True}, status=status.HTTP_400_BAD_REQUEST)

        #first_name should not be blank
        first_name = request.data.get('first_name', None)
        if first_name is None:
            return Response({'message': "Blank first_name field", 'error': True}, status=status.HTTP_400_BAD_REQUEST)

        #last_name should not be blank
        last_name = request.data.get('last_name', None)
        if last_name is None:
            return Response({'message': "Blank last_name field", 'error': True}, status=status.HTTP_400_BAD_REQUEST)

        #password should be at least 6 characters long
        if len(password) < 6:
            return Response({'message': "Password must be at least 6 characters long", 'error': True}, status=status.HTTP_411_LENGTH_REQUIRED)

        #username should not already exist in the database
        if User.objects.filter(username=username).exists():
            return Response({'message': "Username is already taken", 'error': True}, status=status.HTTP_409_CONFLICT)
        
        #role should not be blank
        group = request.data.get('role', None)
        if group is None:
            return Response({'message': "Blank role field", 'error': True}, status=status.HTTP_400_BAD_REQUEST)
        
        # role should be present in the database
        if not Group.objects.filter(name=group).exists():
            return Response({'message': "Specified role does not exist", 'error': True}, status=status.HTTP_404_NOT_FOUND)
        else:
            group = Group.objects.get(name=group)
        
        # all checks are complete and the user can be created
        user = User.objects.create_user(username=username)
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name

        # add user to desired group
        group.user_set.add(user)

        # save newly created user
        user.save()

        # serialize user data
        serialized_user_data = UserSerializer(instance=user)

        # generate token for new user
        token = Token.objects.create(user=user)

        # response object
        response = {
            'user': serialized_user_data.data,
            'token': token.key
        }

        # send success response for new user creation
        return Response({'message': "New User Created Successfully", 'error': False, 'data': response}, status=status.HTTP_201_CREATED)


# handle user list, retrieve and edit requests
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated & (IsAdmin | IsAgent)]
