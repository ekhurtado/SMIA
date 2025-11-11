import connexion

from swagger_server.models.asset import Asset  # noqa: E501
from swagger_server.models.category import Category  # noqa: E501
from swagger_server.models.tag import Tag  # noqa: E501
from swagger_server.models.user import User  # noqa: E501


def create_user(body=None):  # noqa: E501
    """Create user.

    This can only be done by the logged in user. # noqa: E501

    :param body: Created user object
    :type body: dict | bytes

    :rtype: Asset
    """
    if connexion.request.is_json:
        body = Asset.from_dict(connexion.request.get_json())  # noqa: E501
        print(body)
    return 'do some magic!'


def create_user(id=None, name=None, category=None, photo_urls=None, tags=None, status=None):  # noqa: E501
    """Create user.

    This can only be done by the logged in user. # noqa: E501

    :param id: 
    :type id: int
    :param name: 
    :type name: str
    :param category: 
    :type category: dict | bytes
    :param photo_urls: 
    :type photo_urls: List[str]
    :param tags: 
    :type tags: list | bytes
    :param status: 
    :type status: str

    :rtype: Asset
    """
    if connexion.request.is_json:
        category = Category.from_dict(connexion.request.get_json())  # noqa: E501
        print(category)
    if connexion.request.is_json:
        tags = [Tag.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
        print(tags)
    return 'do some magic!'


def create_users_with_list_input(body=None):  # noqa: E501
    """Creates list of users with given input array.

    Creates list of users with given input array. # noqa: E501

    :param body: 
    :type body: list | bytes

    :rtype: Asset
    """
    if connexion.request.is_json:
        body = [Asset.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
        print(body)
    return 'do some magic!'


def delete_user(username):  # noqa: E501
    """Delete user resource.

    This can only be done by the logged in user. # noqa: E501

    :param username: The name that needs to be deleted
    :type username: str

    :rtype: None
    """
    return 'do some magic!'


def get_user_by_name(username):  # noqa: E501
    """Get user by user name.

    Get user detail based on username. # noqa: E501

    :param username: The name that needs to be fetched. Use user1 for testing
    :type username: str

    :rtype: User
    """
    return 'do some magic!'


def login_user(username=None, password=None):  # noqa: E501
    """Logs user into the system.

    Log into the system. # noqa: E501

    :param username: The user name for login
    :type username: str
    :param password: The password for login in clear text
    :type password: str

    :rtype: str
    """
    return 'do some magic!'


def logout_user():  # noqa: E501
    """Logs out current logged in user session.

    Log user out of the system. # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def update_user(username, body=None):  # noqa: E501
    """Update user resource.

    This can only be done by the logged in user. # noqa: E501

    :param username: name that need to be deleted
    :type username: str
    :param body: Update an existent user in the store
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = User.from_dict(connexion.request.get_json())  # noqa: E501
        print(body)
    return 'do some magic!'


def update_user(username, id=None, username2=None, first_name=None, last_name=None, email=None, password=None, phone=None, user_status=None):  # noqa: E501
    """Update user resource.

    This can only be done by the logged in user. # noqa: E501

    :param username: name that need to be deleted
    :type username: str
    :param id: 
    :type id: int
    :param username2: 
    :type username2: str
    :param first_name: 
    :type first_name: str
    :param last_name: 
    :type last_name: str
    :param email: 
    :type email: str
    :param password: 
    :type password: str
    :param phone: 
    :type phone: str
    :param user_status: 
    :type user_status: int

    :rtype: None
    """
    return 'do some magic!'
