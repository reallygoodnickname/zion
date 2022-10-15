import unittest

from sqlalchemy import create_engine
# from sqlalchemy.orm import Session

from zion.database import (Database,
                           User,
                           Restricted,
                           Post,
                           Base)

# User credentials used during testing
username = "thisuserdoesexist"
password = "badpassword"


# Dummy database class solely for tests
class DummyDatabase(Database):
    def __init__(self):
        URI = "sqlite:///:memory:"

        self.engine = create_engine(URI, future=True)
        Base.metadata.create_all(self.engine)


class TestDatabase(unittest.TestCase):

    # Setup function to get database object
    def setUp(self):
        self.db = DummyDatabase()

    # Wrapper function to create and delete users
    def user_creation(function):
        def inner(self):
            # Creating user
            self.db.add_user(username, password)
            self.DUMMY_USER = self.db.get_user(username=username)

            # Running wrapped function
            function(self)

            # Deleting test_user
            self.db.del_user(self.DUMMY_USER)
        return inner

    @user_creation
    def test_validate_user(self):
        user = self.DUMMY_USER

        # User exists and everything is fine
        self.assertTrue(self.db.validate_user(
            user.username, password))

        # User exists but password is wrong
        self.assertFalse(self.db.validate_user(
            username, password+"0"))

        # User exists but username is wrong
        self.assertFalse(self.db.validate_user(
            username+"0", password))

    @user_creation
    def test_exists_in_table(self):
        # Adding new user to table
        self.db.add_user(username, password)
        user = self.db.get_user(username=username)

        # User exists
        self.assertTrue(self.db.exists_in_table(User.username, username))

        # User exists but wrong column
        self.assertFalse(self.db.exists_in_table(User.password, username))

        # User doesn't exist
        self.assertFalse(self.db.exists_in_table(User.username, username+"0"))

        # Deleting user
        self.db.del_user(user)

    @user_creation
    def test_add_user(self):
        # Adding new user but username is already taken
        self.assertFalse(self.db.add_user(username, password))

    @user_creation
    def test_del_user(self):
        user = self.DUMMY_USER

        # Deleting user that exists
        self.assertTrue(self.db.del_user(user))

        # Deleting user that doesn't exist
        self.assertFalse(self.db.del_user(user))
    
    # TODO: add get_user checks
    @user_creation
    def test_get_user(self):
        # Getting user with wrong user_id
        # self.

        # Getting user with wrong username

        # Getting user with both wrong username and user_id

        # Getting user with correct username

        # Getting user with correct user_id

        # Getting user with both correct username and user_id
        pass

    @user_creation
    def test_change_password(self):
        # Saving old id and setting new user id to invalid
        old_id = self.DUMMY_USER.id
        self.DUMMY_USER.id = -1

        # Changing password for user with wrong id
        self.assertFalse(self.db.change_password(
            self.DUMMY_USER, password+"0"))

        # Restoring old user id
        self.DUMMY_USER.id = old_id

        # Changing password for existing user
        self.assertTrue(self.db.change_password(
            self.DUMMY_USER, "1230"))

        # Checking if password has changed
        self.assertTrue(self.db.validate_user(
            self.DUMMY_USER.username, "1230"))


# Run all tests
if __name__ == "__main__":
    unittest.main()
