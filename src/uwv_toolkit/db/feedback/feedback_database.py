from uwv_toolkit.db.database import Database
from uwv_toolkit.utils import persistent_path


class FeedbackDatabase(Database):
    def __init__(self):
        db_path = persistent_path("feedback", force_create=True)
        db_name = f"{db_path}/feedback.db"
        super().__init__(db_name)
