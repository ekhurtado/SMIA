# # coding: utf-8
#
# from __future__ import absolute_import
#
# from flask import json
# from six import BytesIO
#
# from swagger_server.models.error import Error  # noqa: E501
# from swagger_server.models.order import Order  # noqa: E501
# from swagger_server.test import BaseTestCase
#
#
# class TestStoreController(BaseTestCase):
#     """StoreController integration test stubs"""
#
#     def test_delete_order(self):
#         """Test case for delete_order
#
#         Delete purchase order by identifier.
#         """
#         response = self.client.open(
#             '/api/v3/store/order/{orderId}'.format(order_id=789),
#             method='DELETE')
#         self.assert200(response,
#                        'Response body is : ' + response.data.decode('utf-8'))
#
#     def test_get_order_by_id(self):
#         """Test case for get_order_by_id
#
#         Find purchase order by ID.
#         """
#         response = self.client.open(
#             '/api/v3/store/order/{orderId}'.format(order_id=789),
#             method='GET')
#         self.assert200(response,
#                        'Response body is : ' + response.data.decode('utf-8'))
#
#
# if __name__ == '__main__':
#     import unittest
#     unittest.main()
