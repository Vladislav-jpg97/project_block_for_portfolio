from backend.models import Comment


def build_comment_tree(comments: list[Comment]) -> list[Comment]:
    comment_map: dict[int, Comment] = {}
    for comment in comments:
        comment.replies = []
        comment_map[comment.id] = comment

    roots = []
    for comment in comments:
        if comment.parent_id is None:
            roots.append(comment)
        else:
            parent = comment_map.get(comment.parent_id)
            if parent:
                parent.replies.append(comment)

    return roots
