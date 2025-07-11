# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.asset import Asset  # noqa: E501
from swagger_server.models.category import Category  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.tag import Tag  # noqa: E501
from swagger_server.models.user import User  # noqa: E501
from swagger_server.test import BaseTestCase


class TestUserController(BaseTestCase):
    """UserController integration test stubs"""

    def test_create_user(self):
        """Test case for create_user

        Create user.
        """
        body = Asset()
        data = dict(id=789,
                    name='name_example',
                    category=Category(),
                    photo_urls='photo_urls_example',
                    tags=Tag(),
                    status='status_example')
        response = self.client.open(
            '/api/v3/users',
            method='POST',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_create_users_with_list_input(self):
        """Test case for create_users_with_list_input

        Creates list of users with given input array.
        """
        body = [Asset()]
        response = self.client.open(
            '/api/v3/users/createWithList',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_user(self):
        """Test case for delete_user

        Delete user resource.
        """
        response = self.client.open(
            '/api/v3/user/{username}'.format(username='username_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_user_by_name(self):
        """Test case for get_user_by_name

        Get user by user name.
        """
        response = self.client.open(
            '/api/v3/user/{username}'.format(username='username_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_login_user(self):
        """Test case for login_user

        Logs user into the system.
        """
        query_string = [('username', 'username_example'),
                        ('password', 'password_example')]
        response = self.client.open(
            '/api/v3/user/login',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_logout_user(self):
        """Test case for logout_user

        Logs out current logged in user session.
        """
        response = self.client.open(
            '/api/v3/user/logout',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_user(self):
        """Test case for update_user

        Update user resource.
        """
        body = User()
        data = dict(id=789,
                    username='username_example',
                    first_name='first_name_example',
                    last_name='last_name_example',
                    email='email_example',
                    password='password_example',
                    phone='phone_example',
                    user_status=56)
        response = self.client.open(
            '/api/v3/user/{username}'.format(username='username_example'),
            method='PUT',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
