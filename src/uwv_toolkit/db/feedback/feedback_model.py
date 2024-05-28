from uwv_toolkit.db.base_model import BaseModel
from uwv_toolkit.db.feedback.feedback_database import FeedbackDatabase


class FeedbackModel(BaseModel):
    """
    Represents a feedback entry in the database.

    Attributes:
        db (FeedbackDatabase): The database instance for feedback.
        table_name (str): The name of the table in the database.
        fields (dict): The fields and their corresponding data types for the feedback entry.


    Usage example:
        FeedbackModel.create_table()
        feedback = FeedbackModel(feedback_type=True, authenticated_user=st.session_state.name, feedback_text="This is a test feedback", extra="Test prompt", user_email="steve@apple.com")
    """

    db = FeedbackDatabase()
    table_name = "feedback"
    fields = {
        "feedback_type": "BOOL",
        "ground_truth": "TEXT",
        "remark": "TEXT",
        "context": "TEXT",
        "chat_history": "TEXT",
        "authenticated_user": "TEXT",
        "extra": "TEXT",
        "chat_type": "TEXT",
        "user_email": "TEXT",
        "date_created": "TEXT",
        "date_updated": "TEXT",
    }
