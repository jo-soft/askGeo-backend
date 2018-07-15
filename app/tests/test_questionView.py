import json
from random import randrange
from unittest import mock

from database import utils
from tests.test_base import BaseTest


class TestQuestionViewGet(BaseTest):

    def test_get_list(self):
        resp = self.app.get('/api/questions/')
        assert resp.status == '200 OK'
        assert json.loads(resp.data) == []


class TestQuestionViewPost(BaseTest):

    def setUp(self):
        super().setUp()
        self.question_mongo_mock = mock.Mock(name='questoin collection mock')
        answer_mongo_mock = mock.Mock(name='answer collection mock')

        self.insert_result_mock = mock.Mock(name='insert_result_mock')
        self.insert_result_mock.inserted_id = utils.int_to_id_obj(randrange(30000))
        self.question_mongo_mock.insert_one = mock.Mock(name='insert_one', return_value=self.insert_result_mock)
        answer_mongo_mock.find = mock.Mock(name="answer.find", return_value=[])
        self.get_db_mock.return_value = {
            'QuestionModel': self.question_mongo_mock,
            'AnswerModel': answer_mongo_mock
        }

    def test_posting_an_item(self):
        data = {
                'question': {
                    'topic': 'some question',
                    'question': 'content',
                    'loc': {
                        'type': 'Point',
                        'coordinates': [
                            20.21, 40.764
                        ]
                    }
                }
            }
        resp = self.app.post(
            '/api/questions/',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert self.question_mongo_mock.insert_one.call_count == 1
        assert resp.status == '201 CREATED'
        expected_data = dict(
            data['question'],
            _id=utils.id_obj_to_hex_str(self.insert_result_mock.inserted_id),
            answers=[],
            deleted=False,
            score=0
        )
        response_data = json.loads(resp.data)
        assert response_data == expected_data
