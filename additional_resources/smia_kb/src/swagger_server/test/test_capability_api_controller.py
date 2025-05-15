# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.cs_sidentifier import CSSidentifier  # noqa: E501
from swagger_server.models.capability import Capability  # noqa: E501
from swagger_server.models.capability_constraint import CapabilityConstraint  # noqa: E501
from swagger_server.models.category import Category  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.skill import Skill  # noqa: E501
from swagger_server.models.tag import Tag  # noqa: E501
from swagger_server.test import BaseTestCase


class TestCapabilityAPIController(BaseTestCase):
    """CapabilityAPIController integration test stubs"""

    def test_delete_capability_by_id(self):
        """Test case for delete_capability_by_id

        Deletes a capability related to the SMIA-CSS model.
        """
        headers = [('api_key', 'api_key_example')]
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}'.format(capability_identifier=789),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_capability_constraint_by_capability_id(self):
        """Test case for delete_capability_constraint_by_capability_id

        Deletes a capability constraint related to the SMIA-CSS model.
        """
        headers = [('api_key', 'api_key_example')]
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}/capabilitiesConstraints/{capabilityConstraintIdentifier}'.format(capability_identifier='capability_identifier_example', capability_constraint_identifier=789),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_assets_by_capability_id(self):
        """Test case for get_all_assets_by_capability_id

        Returns all assets related to the capability of the SMIA-CSS model.
        """
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}/assets'.format(capability_identifier='capability_identifier_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_capabilities(self):
        """Test case for get_all_capabilities

        Returns all capabilities related to the SMIA-CSS model.
        """
        response = self.client.open(
            '/api/v3/capabilities',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_capabilities_constraints_by_capability_id(self):
        """Test case for get_all_capabilities_constraints_by_capability_id

        Returns all capabilities constraints related to the SMIA-CSS model.
        """
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}/capabilitiesConstraints'.format(capability_identifier='capability_identifier_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_capabilities_identifiers(self):
        """Test case for get_all_capabilities_identifiers

        Returns all capabilities identifiers related to the SMIA-CSS model.
        """
        response = self.client.open(
            '/api/v3/capabilities/$identifiers',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_skill_refs_by_capability_id(self):
        """Test case for get_all_skill_refs_by_capability_id

        Returns all references to the skills related to a specific capability of the SMIA KB.
        """
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}/skill-refs'.format(capability_identifier='capability_identifier_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_capability_by_id(self):
        """Test case for get_capability_by_id

        Returns a specific capability related to the SMIA-CSS model.
        """
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}'.format(capability_identifier='capability_identifier_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_capability_constraint_by_capability_id(self):
        """Test case for get_capability_constraint_by_capability_id

        Returns a specific capability constraint related to the SMIA-CSS model.
        """
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}/capabilitiesConstraints/{capabilityConstraintIdentifier}'.format(capability_identifier='capability_identifier_example', capability_constraint_identifier='capability_constraint_identifier_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_asset_to_capability(self):
        """Test case for post_asset_to_capability

        Add a new asset to a specific Capability of the SMIA KB.
        """
        body = 'body_example'
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}/assets'.format(capability_identifier='capability_identifier_example'),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_capability(self):
        """Test case for post_capability

        Add a new Capability to the SMIA KB.
        """
        body = Capability()
        data = dict(id=789,
                    name='name_example',
                    category=Category(),
                    skills=Skill(),
                    constraints=CapabilityConstraint(),
                    tags=Tag(),
                    status='status_example')
        response = self.client.open(
            '/api/v3/capabilities',
            method='POST',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_capability_constraint(self):
        """Test case for post_capability_constraint

        Add a new Capability Constraint to the SMIA KB.
        """
        body = CapabilityConstraint()
        data = dict(id=789,
                    tags=Tag(),
                    status='status_example')
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}/capabilitiesConstraints'.format(capability_identifier='capability_identifier_example'),
            method='POST',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_skill_ref_to_constraint(self):
        """Test case for post_skill_ref_to_constraint

        Add a new skill reference to a specific capability of the SMIA KB.
        """
        body = Capability()
        data = dict(id=789,
                    name='name_example',
                    category=Category(),
                    skills=Skill(),
                    constraints=CapabilityConstraint(),
                    tags=Tag(),
                    status='status_example')
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}/skill-refs'.format(capability_identifier='capability_identifier_example'),
            method='POST',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_put_capability_by_id(self):
        """Test case for put_capability_by_id

        Updates an existing capability related to the SMIA-CSS model.
        """
        body = Capability()
        data = dict(id=789,
                    name='name_example',
                    category=Category(),
                    skills=Skill(),
                    constraints=CapabilityConstraint(),
                    tags=Tag(),
                    status='status_example')
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}'.format(capability_identifier='capability_identifier_example'),
            method='PUT',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_put_capability_constraint_by_capability_id(self):
        """Test case for put_capability_constraint_by_capability_id

        Updates an existing capability related to the SMIA-CSS model.
        """
        body = CapabilityConstraint()
        data = dict(id=789,
                    tags=Tag(),
                    status='status_example')
        response = self.client.open(
            '/api/v3/capabilities/{capabilityIdentifier}/capabilitiesConstraints/{capabilityConstraintIdentifier}'.format(capability_identifier='capability_identifier_example', capability_constraint_identifier='capability_constraint_identifier_example'),
            method='PUT',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
