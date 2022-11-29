from zion.database import Database, Comment

from typing import List


class comments(Database):
    def __init__(self, database):
        self.session = database.session
        self.engine = database.engine

    # Add comment to database
    def add_comment(self, post_id: int, author: int,
                    parent_id: int, level: int, content: str) -> bool:
        comment = Comment(post_id=post_id, author_id=author,
                          parent_id=parent_id, level=level, content=content)
        return self._add_to_db(comment)

    # Delete comment from database
    def del_comment(self, comment: Comment) -> bool:
        return self._del_from_db(comment)

    # Get comment from database
    def get_comment(self, _id: int) -> Comment | bool:
        return self._get_from_db(Comment.id, _id)

    # Get all comments from database
    def get_comments(self) -> List[Comment] | List:
        return self._get_all_from_db(Comment)

    # Change comment body
    def change_comment(self, id_: int, content: str) -> bool:
        return self._alt_in_db(Comment, {"content": content}, id_)
