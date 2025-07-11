# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.cs_sidentifier import CSSidentifier  # noqa: E501
from swagger_server.models.category import Category  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.skill import Skill  # noqa: E501
from swagger_server.models.skill_parameter import SkillParameter  # noqa: E501
from swagger_server.models.tag import Tag  # noqa: E501
from swagger_server.test import BaseTestCase


class TestSkillAPIController(BaseTestCase):
    """SkillAPIController integration test stubs"""

    def test_delete_skill_by_id(self):
        """Test case for delete_skill_by_id

        Deletes a skill related to the SMIA-CSS model.
        """
        headers = [('api_key', 'api_key_example')]
        response = self.client.open(
            '/api/v3/skills/{skillIdentifier}'.format(skill_identifier=789),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_skill_parameter_by_skill_id(self):
        """Test case for delete_skill_parameter_by_skill_id

        Deletes a skill related to the SMIA-CSS model.
        """
        headers = [('api_key', 'api_key_example')]
        response = self.client.open(
            '/api/v3/skills/{skillIdentifier}/parameters/{skillParameterIdentifier}'.format(skill_parameter_identifier='skill_parameter_identifier_example', skill_identifier=789),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_smi_ainstance_by_id(self):
        """Test case for delete_smi_ainstance_by_id

        Deletes a SMIA instance within the SMIA KB.
        """
        headers = [('api_key', 'api_key_example')]
        response = self.client.open(
            '/api/v3/smiaInstances/{smiaInstanceIdentifier}'.format(smia_instance_identifier=789),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_skill_identifiers(self):
        """Test case for get_all_skill_identifiers

        Returns all skills identifiers related to the SMIA-CSS model.
        """
        response = self.client.open(
            '/api/v3/skills/$identifiers',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_skill_parameters_by_skill_id(self):
        """Test case for get_all_skill_parameters_by_skill_id

        Returns all skill parameters related to a specific SMIA-CSS skill.
        """
        response = self.client.open(
            '/api/v3/skills/{skillIdentifier}/parameters'.format(skill_identifier='skill_identifier_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_skills(self):
        """Test case for get_all_skills

        Returns all skills related to the SMIA-CSS model.
        """
        response = self.client.open(
            '/api/v3/skills',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_skill_by_id(self):
        """Test case for get_skill_by_id

        Returns a specific skill related to the SMIA-CSS model.
        """
        response = self.client.open(
            '/api/v3/skills/{skillIdentifier}'.format(skill_identifier='skill_identifier_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_skill_parameters_by_skill_id(self):
        """Test case for get_skill_parameters_by_skill_id

        Returns a specific skill parameter related to the SMIA-CSS model.
        """
        response = self.client.open(
            '/api/v3/skills/{skillIdentifier}/parameters/{skillParameterIdentifier}'.format(skill_identifier='skill_identifier_example', skill_parameter_identifier='skill_parameter_identifier_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_skill(self):
        """Test case for post_skill

        Add a new Skill to the SMIA KB.
        """
        body = Skill()
        data = dict(id=789,
                    name=CSSidentifier(),
                    category=Category(),
                    photo_urls='photo_urls_example',
                    tags=Tag(),
                    status='status_example')
        response = self.client.open(
            '/api/v3/skills',
            method='POST',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_skill_parameter_by_skill_id(self):
        """Test case for post_skill_parameter_by_skill_id

        Add a new Skill to the SMIA KB.
        """
        body = Skill()
        data = dict(id=789,
                    name=CSSidentifier(),
                    category=Category(),
                    photo_urls='photo_urls_example',
                    tags=Tag(),
                    status='status_example')
        response = self.client.open(
            '/api/v3/skills/{skillIdentifier}/parameters'.format(skill_identifier='skill_identifier_example'),
            method='POST',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_put_skill_by_id(self):
        """Test case for put_skill_by_id

        Updates an existing skill related to the SMIA-CSS model.
        """
        body = Skill()
        data = dict(id=789,
                    name=CSSidentifier(),
                    category=Category(),
                    photo_urls='photo_urls_example',
                    tags=Tag(),
                    status='status_example')
        response = self.client.open(
            '/api/v3/skills/{skillIdentifier}'.format(skill_identifier='skill_identifier_example'),
            method='PUT',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_put_skill_parameter_by_skill_id(self):
        """Test case for put_skill_parameter_by_skill_id

        Updates an existing skill related to the SMIA-CSS model.
        """
        body = Skill()
        data = dict(id=789,
                    name=CSSidentifier(),
                    category=Category(),
                    photo_urls='photo_urls_example',
                    tags=Tag(),
                    status='status_example')
        response = self.client.open(
            '/api/v3/skills/{skillIdentifier}/parameters/{skillParameterIdentifier}'.format(skill_identifier='skill_identifier_example', skill_parameter_identifier='skill_parameter_identifier_example'),
            method='PUT',
            data=json.dumps(body),
            data=data,
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
