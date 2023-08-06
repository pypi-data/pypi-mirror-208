import json
import uuid
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
from datetime import datetime
from .store import CodeStorage
from .utils import extract_dict_keys
import os


def setup_handlers(web_app):
    code_storage = CodeStorage(os.environ.get(
        "CODEPEERS_DB", '/tmp/codepeers.db'))

    class CodeQueryHandler(APIHandler):
        # The following decorator should be present on all verb methods (head, get, post,
        # patch, put, delete, options) to ensure only authorized user can request the
        # Jupyter server
        @ tornado.web.authenticated
        def get(self):
            topic_id = self.get_query_argument("topic_id", None)
            if topic_id is None:
                self.set_status(400)
                self.finish(json.dumps({"error": "Missing required fields"}))
            submissions = code_storage.query_submissions_by_group(topic_id)
            self.finish(json.dumps(submissions))

    class CodeSubmitHandler(APIHandler):
        @ tornado.web.authenticated
        def post(self):
            # input_data is a dictionary with a key "name"
            input_data = self.get_json_body()
            if input_data is None or not all(
                    k in input_data for k in ('document_id', 'user_id', 'topic_id', 'code', 'user_name')):
                self.set_status(400)
                self.finish(json.dumps({"error": "Missing required fields"}))
                return
            submit_id = str(uuid.uuid4())
            submit_timestamp = int(datetime.now().timestamp() * 1000)
            code_storage.handle_submission(
                extract_dict_keys(input_data, 'document_id',
                                  'user_id', 'topic_id', 'code')
                | {"submission_id": submit_id, "timestamp": submit_timestamp, "author": input_data['user_name']})
            self.finish(json.dumps({"submission_id": submit_id}))

    host_pattern = ".*$"
    app_url_prefix = url_path_join(web_app.settings["base_url"], "codepeers")
    handlers = [
        (url_path_join(app_url_prefix, "query_code"), CodeQueryHandler),
        (url_path_join(app_url_prefix, "submit_code"), CodeSubmitHandler)]
    web_app.add_handlers(host_pattern, handlers)
