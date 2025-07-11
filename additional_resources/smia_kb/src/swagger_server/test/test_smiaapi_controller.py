# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.category import Category  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.smia_instance import SMIAinstance  # noqa: E501
from swagger_server.models.tag import Tag  # noqa: E501
from swagger_server.test import BaseTestCase


class TestSMIAAPIController(BaseTestCase):
    """SMIAAPIController integration test stubs"""

    def test_get_all_smi_ainstances(self):
        """Test case for get_all_smi_ainstances

        Finds all registered SMIA instances.
        """
        response = self.client.open(
            '/api/v3/smiaInstances',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_smi_ainstance_by_id(self):
        """Test case for get_smi_ainstance_by_id

        Returns a specific SMIA instance registered in the SMIA KB.
        """
        response = self.client.open(
            '/api/v3/smiaInstances/{smiaInstanceIdentifier}'.format(smia_instance_identifier='smia_instance_identifier_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_smi_ainstance(self):
        """Test case for post_smi_ainstance

        Add a new SMIA instance to the SMIA KB.
        """
        body = SMIAinstance()
        data = dict(id='id_example',
                    status='status_example',
                    created_time_stamp=789,
                    name='name_example',
                    category=Category(),
                    photo_urls='photo_urls_example',
                    tags=Tag())
        response = self.client.open(
            '/api/v3/smiaInstances',
            method='POST',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_put_smi_ainstance_by_id(self):
        """Test case for put_smi_ainstance_by_id

        Updates an existing SMIA instance registered in the SMIA KB.
        """
        body = SMIAinstance()
        data = dict(id='id_example',
                    status='status_example',
                    created_time_stamp=789,
                    name='name_example',
                    category=Category(),
                    photo_urls='photo_urls_example',
                    tags=Tag())
        response = self.client.open(
            '/api/v3/smiaInstances/{smiaInstanceIdentifier}'.format(smia_instance_identifier='smia_instance_identifier_example'),
            method='PUT',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
