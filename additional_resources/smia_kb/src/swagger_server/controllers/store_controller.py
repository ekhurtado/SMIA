import connexion
import six

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.order import Order  # noqa: E501
from swagger_server import util


def delete_order(order_id):  # noqa: E501
    """Delete purchase order by identifier.

    For valid response try integer IDs with value &lt; 1000. Anything above 1000 or nonintegers will generate API errors. # noqa: E501

    :param order_id: ID of the order that needs to be deleted
    :type order_id: int

    :rtype: None
    """
    return 'do some magic!'


def get_order_by_id(order_id):  # noqa: E501
    """Find purchase order by ID.

    For valid response try integer IDs with value &lt;&#x3D; 5 or &gt; 10. Other values will generate exceptions. # noqa: E501

    :param order_id: ID of order that needs to be fetched
    :type order_id: int

    :rtype: Order
    """
    return 'do some magic!'
