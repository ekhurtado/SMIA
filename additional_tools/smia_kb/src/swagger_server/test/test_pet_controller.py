# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.api_response import ApiResponse  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.pet import Pet  # noqa: E501
from swagger_server.test import BaseTestCase


class TestPetController(BaseTestCase):
    """PetController integration test stubs"""

    def test_delete_pet(self):
        """Test case for delete_pet

        Deletes a pet.
        """
        headers = [('api_key', 'api_key_example')]
        response = self.client.open(
            '/api/v3/pet/{petId}'.format(pet_id=789),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_find_petinstances(self):
        """Test case for find_petinstances

        Finds Pets by tags.
        """
        query_string = [('tags', 'tags_example')]
        response = self.client.open(
            '/api/v3/pets',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_find_pets_by_status(self):
        """Test case for find_pets_by_status

        Finds Pets by status.
        """
        query_string = [('status', 'available')]
        response = self.client.open(
            '/api/v3/pet/findByStatus',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_find_pets_by_tags(self):
        """Test case for find_pets_by_tags

        Finds Pets by tags.
        """
        query_string = [('tags', 'tags_example')]
        response = self.client.open(
            '/api/v3/pet/findByTags',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_pet_by_id(self):
        """Test case for get_pet_by_id

        Find pet by ID.
        """
        response = self.client.open(
            '/api/v3/pet/{petId}'.format(pet_id=789),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_pet_with_form(self):
        """Test case for update_pet_with_form

        Updates a pet in the store with form data.
        """
        query_string = [('name', 'name_example'),
                        ('status', 'status_example')]
        response = self.client.open(
            '/api/v3/pet/{petId}'.format(pet_id=789),
            method='POST',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_upload_file(self):
        """Test case for upload_file

        Uploads an image.
        """
        body = Object()
        query_string = [('additional_metadata', 'additional_metadata_example')]
        response = self.client.open(
            '/api/v3/pet/{petId}/uploadImage'.format(pet_id=789),
            method='POST',
            data=json.dumps(body),
            content_type='application/octet-stream',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
