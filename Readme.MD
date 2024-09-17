### Liftsmail API

## Overview
This API built with django rest framework provides a set of RESTFUL endpoints for users to send bulk emails to their contacts. Users can create a group to which an email is to be sent. Sending of emails can be scheduled and the content customized as required.

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
