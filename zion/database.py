from sqlalchemy.orm import (Session,
                            declarative_base)
import sqlalchemy.exc
from sqlalchemy import (create_engine,
                        Column,
                        Integer,
                        String,
                        TIMESTAMP,
                        select,
                        or_,
                        update,
                        func,
                        text)
from sys import exit
import logging
import bcrypt

# Used to create table
Base = declarative_base()


class Database:

    def __init__(self, host,  user, passwd, name):
        # Getting logger from main file
        self.__logger = logging.getLogger(__name__)

        func.binary = str()

        self.host = host
        self.user = user
        self.passwd = passwd
        self.name = name

        try:
            URI = f"mariadb+mariadbconnector://{user}:{passwd}@{host}/{name}"

            self.engine = create_engine(URI, future=True)
            Base.metadata.create_all(self.engine)

        except sqlalchemy.exc.OperationalError:
            self.__logger.critical("Failed to connect to database!")
            exit(1)

    # Function wrapper to start and close sessions correctly
    def session_action(function):
        def inner(self, *args, **kwargs):
            # Making it work with sqlite
            # TODO: possibly fix this workaround
            if self.engine.name == "sqlite":
                func.binary = str

            # Creating engine and running function
            self.session = Session(self.engine)
            result = function(self, *args, **kwargs)

            # Closing session and returning result
            self.session.close()
            return result
        return inner

    # Check if there is an entry in database with specifide value
    @session_action
    def exists_in_table(self, column, value):
        statement = select(column).where(column == func.binary(value))
        return self.session.scalar(statement) is not None

    # Add new user to database
    @session_action
    def add_user(self, username, password):
        # check if username is already taken
        if (self.exists_in_table(User.username, username)):
            return False

        # Hashing password
        password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())
        password = password.decode('UTF-8')

        user = User(username=username, password=password)

        self.session.add(user)
        self.session.commit()
        return True

    # Delete user from database
    @session_action
    def del_user(self, user):
        # Check if user is in database
        if not self.exists_in_table(User.username, user.username):
            return False

        self.session.delete(user)
        self.session.commit()
        return True

    # Get user by id or by username
    @session_action
    def get_user(self, user_id=None, username=None):
        # Check if either user_id or username are passed
        if (user_id is None and username is None):
            return False

        statement = select(User).where(
            or_(User.id == user_id, User.username == func.binary(username)))

        # Check if anything is found. Return false if user is not found
        result = self.session.scalar(statement)
        if result is None:
            return False

        return result

    # Change user password
    @session_action
    def change_password(self, user, password):
        # Check if exists in table
        if not self.exists_in_table(User.id, user.id):
            return False

        # Hashing passwoord and adding it to statement
        password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())
        statement = update(User).values(
            password=password.decode('UTF-8')).where(User.id == user.id)

        self.session.execute(statement)
        self.session.commit()

        return True

    # Check user credentials
    @session_action
    def validate_user(self, username, password):
        statement = select(User.password).where(
            User.username == func.binary(username))

        # Getting password and password hash
        hashed = self.session.scalar(statement)

        # Check if we could get password from database
        if hashed is None:
            return False

        # Encoding passwords
        password = password.encode('UTF-8')
        hashed = hashed.encode('UTF-8')

        # Checking password hash
        return bcrypt.checkpw(password, hashed)


class Restricted(Base):
    __tablename__ = "restricted"

    id = Column(Integer, primary_key=True, nullable=False)
    ip = Column(String(16), nullable=False)
    reason = Column(String(255))
    timestamp = Column(TIMESTAMP, default=text(
        "CURRENT_TIMESTAMP"), nullable=False)
    expire = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "<Banned(id='%s',ip='%s',reason='%s',timestamp='%s')>" % (
            self.id, self.ip, self.reason, self.timestamp)


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, nullable=False)
    header = Column(String(255), nullable=False)
    article = Column(String(2048), nullable=False)
    author = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, default=text(
        "CURRENT_TIMESTAMP"), nullable=False)

    def __repr__(self):
        return "<Post(post_id='%s',header='%s',article='%s',author='%s',timestamp='%s')>" % (
            self.post_id, self.header, self.article, self.author, self.timestamp)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(20), nullable=False)
    password = Column(String(64), nullable=False)
    email = Column(String(256))
    timestamp = Column(TIMESTAMP, default=text(
        "CURRENT_TIMESTAMP"), nullable=False)

    def __repr__(self):
        return "<User(id='%s',username='%s',password='%s',email='%s',timestamp='%s')>" % (
            self.id, self.username, self.password, self.email, self.timestamp)
