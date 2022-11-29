from sqlalchemy.orm import (Session,
                            relationship,
                            declarative_base)

import logging

import sqlalchemy.exc
from sqlalchemy import (create_engine,
                        exists,
                        update,
                        Boolean,
                        desc,
                        inspect,
                        Column,
                        Integer,
                        String,
                        TIMESTAMP,
                        ForeignKey,
                        func)

from sys import exit

from typing import Any, List, NewType

# Used to create table
Base = declarative_base()

# Defining some common types
AttributeType = NewType(
    "AttributeType", sqlalchemy.orm.attributes.InstrumentedAttribute)
DeclarativeMetaType = NewType(
    "DeclarativeMetaType", sqlalchemy.orm.decl_api.DeclarativeMeta)


class Database:

    def __init__(self, host: str,  user: str, passwd: str, name: str) -> None:

        self.host = host
        self.user = user
        self.passwd = passwd
        self.name = name

        try:
            URI = f"mysql+mysqldb://{user}:{passwd}@{host}/{name}"

            self.engine = create_engine(URI, future=True)
            self.session = Session(self.engine)

            # Check if table "settings" exists
            self.configured = inspect(self.engine).has_table("settings")

            # Create all tables, even if they don't exist
            Base.metadata.create_all(self.engine)

        except sqlalchemy.exc.OperationalError:
            logging.critical("Failed to connect to database!")
            exit(1)

    # Get all objects from database
    def _get_all_from_db(self, obj: Any) -> List:
        return self.session.query(obj).all()

    # Get literally anything from database
    def _get_from_db(self, param: AttributeType, target: str) -> Any:
        q = self.session.query(param.class_).where(
            param == func.binary(target)).first()

        return q if q is not None else False

    # Check if object actually exists in table
    def _validate_object(self, obj: Any) -> bool:
        if obj is False:
            return False

        # Get object class
        obj_class = obj.__mapper__.class_

        # Return session result
        return self.session.query(self.session.query(
            obj.id).filter(obj_class.id == obj.id).exists()).scalar()

    # Delete literally anything from database
    def _del_from_db(self, obj: Any) -> bool:
        # Check if object is valid
        if not self._validate_object(obj):
            return False

        # Delete from table and commit changes
        self.session.delete(obj)
        self.session.commit()

        return True

    # Add literally anything to database
    def _add_to_db(self, obj: Any) -> bool:
        # Check if object is valid
        if self._validate_object(obj):
            return False

        # Add to table and commit changes
        self.session.add(obj)
        self.session.commit()

        return True

    # Alter literally anything in database
    def _alt_in_db(self, param_class: DeclarativeMetaType,
                   values: tuple[str, str],  _id: int) -> bool:
        if not self._exists_in_table(param_class.id, _id):
            return False

        _primary_key = param_class.id

        self.session.execute(update(param_class).
                             values(values).
                             where(_primary_key == _id))
        self.session.commit()

        return True

    # Check if there is an entry in database with specifide value
    def _exists_in_table(self, column: AttributeType, value: str) -> bool:
        _res = self.session.query(exists().where(
            column == func.binary(value))).scalar()
        return _res

    # Get item that goes before specified id
    def _get_previous(self, param_class: DeclarativeMetaType, _id: int) -> Any:
        _res = (self.session.query(param_class).
                where(param_class.id < _id).
                order_by(desc(param_class.id)).
                limit(1).first())

        return False if _res is None else _res

    # Get item that goes after specified id
    def _get_next(self, param_class: DeclarativeMetaType, _id: int) -> Any:
        _res = self.session.query(param_class).where(
            param_class.id > _id).limit(1).first()

        return False if _res is None else _res


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)

    # Postheader and body itself
    header = Column(String(120), nullable=False)
    article = Column(String(10000), nullable=False)

    # Post author's id
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Post creation date
    timestamp = Column(TIMESTAMP, server_default=func.now())

    # Relationship, access all comments and post author
    comments = relationship("Comment", cascade="all,delete", lazy="joined")
    author = relationship("User", back_populates="posts", lazy="joined")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    # Comment content
    content = Column(String(255), nullable=False)

    # Comment level, defines indentation that will be used when displaying
    level = Column(Integer, nullable=False, default=0)

    # Comment creation timestamp
    timestamp = Column(TIMESTAMP, server_default=func.now())

    # Parent comment and child comments
    parent = relationship("Comment", remote_side=[id], lazy="joined")
    child = relationship("Comment", cascade="all,delete",
                         back_populates="parent", lazy="joined")

    # Author of the comment and post that this comment belongs to
    author = relationship("User", back_populates="comments", lazy="joined")
    post = relationship("Post", back_populates="comments", lazy="joined")


class User(Base):
    __tablename__ = "users"

    # Some default creds
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(20), nullable=False)
    password = Column(String(64), nullable=False)
    email = Column(String(256), nullable=True)

    # User privileges
    author = Column(Boolean, unique=False, default=False)
    moderator = Column(Boolean, unique=False, default=False)
    admin = Column(Boolean, unique=False, default=False)

    # User avatar filename
    avatar = Column(String(20), nullable=True)

    # User creation timestamp
    timestamp = Column(TIMESTAMP, server_default=func.now())

    # Replationships
    posts = relationship("Post", back_populates="author",
                         cascade="all,delete", lazy="joined")
    comments = relationship("Comment", back_populates="author",
                            cascade="all,delete", lazy="joined")


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, nullable=False)
    setting_name = Column(String(60), nullable=False)
    setting_value = Column(String(255), nullable=True)
    setting_desc = Column(String(255), nullable=False)
    setting_type = Column(String(20), nullable=False)
