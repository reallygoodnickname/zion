from sys import exit
from hashlib import sha256
import logging

from sqlalchemy import (create_engine,
                        Column,
                        Integer,
                        String,
                        TIMESTAMP,
                        select)

from sqlalchemy.orm import (Session,
                            declarative_base)

# Used to create table
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(20), nullable=False)
    password = Column(String(64), nullable=False)
    email = Column(String(256))
    timestamp = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "<User(id='%s',username='%s','password'='%s','email=%s')>" % (
            self.id, self.username, self.password, self.email)


class Database:

    def __init__(self, host,  user, passwd, name):
        # Getting logger from zion file
        self.__logger = logging.getLogger(__name__)

        self.host = host
        self.user = user
        self.passwd = passwd
        self.name = name

        try:
            # Create URI to make engine creation line shorter
            URI = f"mariadb+mariadbconnector://{user}:{passwd}@{host}/{name}"
            self.engine = create_engine(URI, echo=True, future=True)
            Base.metadata.create_all(self.engine)

        # TODO: add exceptions support
        except Exception as E:
            self.__logger.critical(E)
            exit(1)

    def registerUser(self, username, password):
        # TODO: make it work, add credentials validation
        session = Session(self.engine)

        # Hashing password to make it secure
        password = sha256(password.encode('UTF-8')).hexdigest()

        # Creating user
        user = User(username=username, password=password)

        # Commiting changes and closing session
        session.add(user)
        session.commit()
        session.close()

    def deleteUser(self, username):
        pass

    def validateUser(self, username, password):
        # Getting password hash
        password = sha256(password.encode('UTF-8')).hexdigest()
        session = Session(self.engine)

        # Get user pass
        statement = select(User.password).where(User.username == username)
        user_pass = session.scalars(statement).one()

        # Validate user password
        if (user_pass == password):
            return True

        return False
