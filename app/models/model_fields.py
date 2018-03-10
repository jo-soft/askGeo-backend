from marshmallow import utils as marshmallow_utils


class ValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors

    def __repr__(self):
        return "{classname}: [{errors}]".format(
            classname=self.__class__.__name__,
            errors=", ".join(self.errors)
        )


class NotNullError(ValidationError):
    def __init__(self, msg):
        super().__init__([msg])


class _MissingValue(object):
    def __bool__(self): return False


class BaseModelField(object):
    def __init__(self, default=_MissingValue(), default_load=None,
                 attribute=None, load_from=None, dump_to=None,
                 many=False, validate=None, required=False, allow_none=None,
                 load_only=False, dump_only=False,
                 missing=_MissingValue(), error_messages=None):
        self.default = default
        self.default_load = default_load
        self.attribute = attribute
        self.load_from = load_from  # this flag is used by Unmarshaller
        self.dump_to = dump_to  # this flag is used by Marshaller
        self.many = many
        if self.default_load is None and self.many:
            self.default_load = []
        self.validate = validate
        if marshmallow_utils.is_iterable_but_not_string(validate):
            if not marshmallow_utils.is_generator(validate):
                self.validators = validate
            else:
                self.validators = list(validate)
        elif callable(validate):
            self.validators = [validate]
        elif validate is None:
            self.validators = []
        else:
            raise ValueError("The 'validate' parameter must be a callable "
                             "or a collection of callables.")

        self.required = required
        # If missing=None, None should be considered valid by default
        if allow_none is None:
            if missing is None:
                self.allow_none = True
            else:
                self.allow_none = False
        else:
            self.allow_none = allow_none
        self.load_only = load_only
        self.dump_only = dump_only
        self.missing = missing

        # Collect default error message from self and parent classes
        messages = {}
        for cls in reversed(self.__class__.__mro__):
            messages.update(getattr(cls, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

    def _validate(self, item):
        validated = [
            validator(item) for validator in self.validators
        ]
        errors = list(filter(lambda err: bool(err), validated))
        if errors:
            raise ValidationError(errors)

    def _serialize(self, value, attr, obj):
        pass

    def _load(self, value, attr, src_obj):
        pass

    def serialize(self, field_name, obj):
        val = getattr(obj, field_name)
        if self.many:
            serialized = [
                self._serialize(_val, field_name, obj) for _val in val
            ]
        else:
            serialized = self._serialize(val, field_name, obj)

        target = self.dump_to or field_name
        setattr(obj, target, serialized)

    def load(self, field_name, obj):
        src = self.load_from or field_name
        val = getattr(obj, src, self.default_load)

        if self.many:
            loaded = [self._load(_val, src, obj) for _val in val]
            map(self._validate, loaded)
        else:
            loaded = self._load(val, src, obj)
            self._validate(loaded)
        if self.default:
            loaded = loaded or self.default

        if not self.allow_none and loaded is None:
            raise NotNullError("{} cannot be null".format(field_name))
        setattr(obj, field_name, loaded)
