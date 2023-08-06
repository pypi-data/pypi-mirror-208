from pony import orm

db = orm.Database()


class CodeSubmission(db.Entity):
    submission_id = orm.PrimaryKey(str)
    document_id = orm.Required(str)
    user_id = orm.Required(str)
    topic_id = orm.Required(str)
    code = orm.Required(str)
    author = orm.Required(str)
    timestamp = orm.Required(int, size=64)


def serialize_select(func):
    def wrapper(*args, **kwargs):
        query = func(*args, **kwargs)
        return [p.to_dict() for p in query]
    return wrapper


class CodeStorage:
    def __init__(self, db_path: str):
        db.bind(provider='sqlite', filename=db_path, create_db=True)
        db.generate_mapping(create_tables=True)

    @orm.db_session
    def handle_submission(self, submission):
        CodeSubmission(**submission)

    @orm.db_session
    @serialize_select
    def query_submissions_by_group(self, topic_id):
        return orm.select(p for p in CodeSubmission if p.topic_id == topic_id)

    @orm.db_session
    def query_submissions_by_author(self, author):
        return orm.select(p for p in CodeSubmission if p.author == author)
