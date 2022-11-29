from zion.database import Database, User
import bcrypt

from typing import List
import re


class users(Database):
    def __init__(self, database):
        self.session = database.session
        self.engine = database.engine

        # Add user to database
    def add_user(self, username: str, password: str, email: str = None,
                 author: bool = False, admin: bool = False,
                 moderator: bool = False, avatar: str = None) -> bool:
        # check if username is already taken
        if (self._exists_in_table(User.username, username)):
            return False

        # Hashing password
        password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())
        password = password.decode('UTF-8')

        user = User(username=username, password=password, email=email,
                    author=author, admin=admin, moderator=moderator,
                    avatar=avatar)
        return self._add_to_db(user)

    # Delete user from database
    def del_user(self, user: User) -> bool:
        return self._del_from_db(user)

    # Get user by id or by username
    def get_user(self, user_id: int = None,
                 username: str = None) -> User | bool:
        # Check if either user_id or username are passed
        if (user_id == username):
            return False

        # Get user either from user_id or from username
        if user_id is not None:
            return self._get_from_db(User.id, user_id)
        else:
            return self._get_from_db(User.username, username)

    # Change user password
    def change_password(self, user: User, password: str) -> bool:
        # Hashing passwoord and adding it to statement
        password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())
        return self._alt_in_db(User, {"password": password.decode('UTF-8')},
                               user.id)

    # Check user credentials
    def validate_user(self, username: str, password: str) -> bool:
        hashed = self._get_from_db(User.username, username)

        # Check if we get any password
        if not hashed:
            return False

        # Encoding passwords
        password = password.encode('UTF-8')
        hashed = hashed.password.encode('UTF-8')

        # Checking password hash
        return bcrypt.checkpw(password, hashed)

    # Get all users from db
    def get_users(self) -> List[User] | List:
        return self._get_all_from_db(User)

    # Change privilege from false to true and vice versa
    def swap_permission(self, user: User, permission: str) -> bool:
        try:
            previous = getattr(user, permission)
        except AttributeError:
            return False

        if not isinstance(previous, bool):
            return False

        return self._alt_in_db(User, {permission: not previous}, user.id)

    # Update user profile
    def update_profile(self, _id: int,  username: str,
                       avatar: str = None, email: str = None) -> bool:

        # Get basic infomation
        _info = {"username": username}

        # Only change avatar if passed
        if avatar is not None:
            _info["avatar"] = avatar

        if email is not None:
            _info["email"] = email

        return self._alt_in_db(User, _info,  _id)

    # Validate received mail address
    def validate_mail(self, email: str) -> bool:
        regex = "^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@" +\
                "[a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*$"

        if re.search(regex, email):
            return True
        return False

    # Validate received username
    def validate_username(self, username: str,
                          check_exists=False) -> bool | str:
        # Check username length
        if not 6 < len(username) < 20:
            return "Username length should be from 6 to 20 chars!"

        # Check that username doesn't contain badchars
        if not username.isalnum():
            return "Username can contain only alphanumeric chars!"

        # Check if username is already taken
        if check_exists:
            if (self._exists_in_table(User.username, username)):
                return "Username already taken!"

        return True
