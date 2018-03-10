import unittest

from marshmallow.fields import Field

from database.schema import BaseSchema


class TestSchema(unittest.TestCase):
    class Schema(BaseSchema):
        excluded1 = Field()
        excluded2 = Field(exclude_this=True)
        excluded3 = Field(exclude_this=True)
        included = Field()

    def test_fields_matching_exclude_function_are_excluded(self):
        def field_filter_fn(field):
            meta = getattr(field, 'metadata', {})
            return meta.get('exclude_this', False)

        schema = self.Schema(field_filter_fn=field_filter_fn, exclude=['excluded1', 'excluded2'])
        self.assertEqual(schema.exclude, set((
            'excluded1', 'excluded2', 'excluded3'
        )))
