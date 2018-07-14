import json

from tests.test_base import BaseTest


class TestQuestionView(BaseTest):

    def test_call(self):
        resp = self.app.get('/api/questions/')
        assert resp.status == '200 OK'
        assert json.loads(resp.data) == []
