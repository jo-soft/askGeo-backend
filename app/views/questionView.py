from flask import Blueprint

from models.question import QuestionModel
from views.LocationModelView import LocationModelView

questions_bp = Blueprint('/questions', __name__)
questions_bp.record(lambda _: register())


def register():
    QuestionList.register(questions_bp, '/questions/', '/questions/<string:_id>')


class QuestionList(LocationModelView):

    def __init__(self):
        super().__init__(QuestionModel)
        self.field_name = "question"
