### Liftsmail API

## Overview
This API built with django rest framework provides a set of RESTFUL endpoints for users to send bulk emails to their contacts. Users can create a group to which an email is to be sent. Sending of emails can be scheduled and the content customized as required.

## Installation and Setup

1. Clone the git repository 

## Running Tests

Tests are organized into different files within the app's `tests` directory. Here's how to run them:

1. To run all the tests, use the following command:

    ```
    python manage.py test
    ```

2. To run a single test file, you can use the following command (replacing `<app_name>` and `<test_file>` with the appropriate values):

    ```
    python manage.py test <app_name>.tests.<test_file>
    ```

## Endpoints

The following endpoints are available in the API

# Authentication Endpoint
JWT token authenytication is used in this application.

- `/accounts/jwt/create/` POST: Log in endpoint to get access and refresh token
- `/accounts/jwt/refresh/` POST: Obatin refresh token
- `/accounts/users/` POST: Create an account
- `/accounts/users/me/` GET: Get account details

# Groups and Contact Endpoint
These set of endpoints enable user create email groups and manage contacts the groups. They all require authentication before they can be accessed

- `/groups/` GET : Get all email groups created by the user
- `/groups/` POST : Create a new email group
- `/groups/<id>/` GET: Get the email group specified by the id
- `/groups/<id>/` DELETE : Delete an email group specified by id
- `/groups/<id>/` PATCH: Partial update of email group
- `/groups/<id>/` PUT: Update an email group details
- `/groups/<group_id>/contacts/` GET : Get all contacts in an email group
- `/groups/<group_id>/contacts/` POST: Create a contact in an email group
- `/groups/<group_id>/contacts/id/` PUT: Update all details of a contact in an email group
- `/groups/<group_id>/contacts/id/` PATCH: Partial update of details in an email group
- `/groups/<group_id>/contacts/id/` DELETE: Delete a contact from an email group

# Email Endpoints
These endpoints are for creating templates and creating sessions to send emails. They all require authentication

- `/email/templates/` GET: List all the templates created by the user. 
- `/email/templates/` POST: Create a new email template
- `/email/templates/<id>/` GET: Get details of a specific email template
- `/email/templates/<id>/` PUT: Update an email template
- `/email/templates/<id>/` PATCH: Partial Update of email template
- `/email/templates/<id>/` DELETE: Delete an email template
- `/email/send/` POST: Send a bulk email to a group. Emails are sent immediately not scheduled. An email session is created in the database
- `/email/schedule/` POST: Create a schedule to send bulk email to a group at a later time. An email session is created in the database
- `/email/schedule/recurring/` POST: Creates a periodic schedule to send emails. Emails are continually sent with the schedule created. An email session is created in the db
- `/email/sessions/` GET: User views all sessions of email created, whether immediate sending,  schedule sending or reccurring sending. 
