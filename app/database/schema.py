from marshmallow import Schema


class BaseSchema(Schema):
    def __init__(self, field_filter_fn=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if field_filter_fn:
            super_exclude = self.exclude or ()
            if not (isinstance(super_exclude, tuple)):
                super_exclude = tuple(super_exclude)
            internal_exclude = tuple(
                field_name for field_name, field in self.fields.items()
                if field_filter_fn(field)
            )
            self.exclude = set(super_exclude + internal_exclude)
