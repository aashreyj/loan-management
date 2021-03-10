# Minimal Loan Management System
Developed by: Aashrey Jain

### Technologies Used:
1. Python 3
1. Django Rest Framework
2. Docker
3. PostgreSQL (Database)
3. Git (VCS)

### Core Design
1. The project consists of the loan-management Django project in which 'loan' is an app.
2. For hashing the user passwords, Django uses sha5 encryption which it supports out-of-the-box. Different roles of different users can be set using the Group model provided by Django. We can create three groups and have differing permissions for the groups based on the available roles within the organization. In the present scenario, the roles are: 'admin', 'agent', and 'customer'.
3. For the authentication of the APIs, I have used TokenAuthentication. During registration, the response contains a token key that must be saved by the client-side and used for authenticating each and every request that is made. The token key must be passed in the Authorization HTTP header as: "Authorization: Token <token key>" to authenticate the API call.
4. For editing the loan, the code checks if the loan is in Approved or Rejected state. If it is so, then the changes are discarded. This check is performed on the basis of the role of the user as well since only an 'agent' can edit a loan.

### End-points and their Working
1. _'account/register'_: Send POST request containing params: first_name, last_name, username, password and role to create a new user in the database. The response contains error message if something goes wrong. For a successful call, the response contains the details of the newly-created user along with the token key that must be provided to authenticate all further API calls.
2. _'account/users_: 'admin' and 'agent' roles can send GET requests to this endpoint to list all the users that are present in the database.
3. _'account/users/<id>_: 'admin' and 'agent' roles can send GET request to this endpoint to retrieve a particular user. Sending PATCH request to the same endpoint allows the sender to update any particular user instance.
4. _'loan/create-request_: 'agents' can send POST request to this endpoint to create a new loan request on behalf of the customer. The request body must contain all the necessary fields of the Loan object.
5. _'loan/approve/<id>'_: by sending a GET request to this endpoint from a 'admin' user token will result in the loan object with id 'id' to be moved from the 'new' state to the 'approved' state.
6. _'loan/edit/<id>_: 'agents' can send PATCH request to this endpoint to edit fields of an existing Loan object. However, an error is returned if the Loan is in Approved or Rejected state.
7. 'loan/filter': all users can send POST requests to this endpoint, with the request body containing the params on the basis of which the filtering is to be carried out. Customers can only see their own loans due an additional 'customer' filter that is applied by default on all customer requests whereas the admin and agent roles can see all Loans that are present in the Database.

### How To Run
The Dockerfile and the docker-compose files will build the container and create the image that is required to get the system running.
