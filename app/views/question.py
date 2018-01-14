from flask import Blueprint

from models.question import QuestionModel
from views.model_base_view import BaseModelView

questions_bp = Blueprint('/questions', __name__)
questions_bp.record(lambda _: register())


def register():
    QuestionList.register(questions_bp, '/questions/', '/questions/<_id>')


class QuestionList(BaseModelView):

    def __init__(self):
        super().__init__(QuestionModel)