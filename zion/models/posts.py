from zion.database import Database, Post
from typing import List


class posts(Database):
    def __init__(self, database):
        self.session = database.session
        self.engine = database.engine

    # Add new post
    def add_post(self, header: str, article: str, author: int) -> bool:
        # Check if post with the same header already exists in database
        if (self._exists_in_table(Post.header, header)):
            return False

        # TODO: add post text and header sanitization
        post = Post(header=header, article=article, author_id=author)
        return self._add_to_db(post)

    # Del post
    def del_post(self, post: Post) -> bool:
        return self._del_from_db(post)

    # Get post
    def get_post(self, post_id: int = None, header: str = None) -> Post | bool:
        # Return false if both are None
        if post_id == header:
            return False

        # Use either post id or header
        if post_id is not None:
            return self._get_from_db(Post.id, post_id)
        else:
            return self._get_from_db(Post.header, header)

    # Get all posts in a list from database
    def get_posts(self) -> List[Post] | List:
        return self._get_all_from_db(Post)

    # Update post entries
    def update_post(self, _post: Post) -> bool:
        return self._alt_in_db(Post, {"header": _post.header,
                                      "article": _post.article,
                                      "author_id": _post.author_id,
                                      "timestamp": _post.timestamp}, _post.id)

    # Return list used for navigation
    def get_post_nav(self, post_id: int) -> List:
        return [self._get_previous(Post, post_id),
                self._get_next(Post, post_id), ]
