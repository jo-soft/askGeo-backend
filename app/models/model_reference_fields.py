from database.exceptions import NotFoundError
from models.misc import CachedObj
from models.model_fields import BaseModelField


class ReferenceTargetField(BaseModelField):
    @property
    def target_cls(self):
        return self.target_cls_fn()

    def __init__(self,
                 target_cls,
                 target_field="_id",
                 value_transformer=lambda x: x,
                 validate_exists=True,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not callable(target_cls):
            target_cls = lambda: target_cls()
        self.target_cls_fn = target_cls
        self.target_field = target_field
        self.transform_value = value_transformer
        self.validate_exits = validate_exists

    def _validate_exists(self, val):
        if not self.target_cls.manager().exists({
            self.target_field: val
        }):
            raise NotFoundError(self.target_cls.manager().collection, val)

    def _serialize(self, value, attr=None, obj=None):
        transformed_value = self.transform_value(value)
        if self.validate_exits:
            self._validate_exists(transformed_value)
        return transformed_value

    def _load(self, value, attr=None, src_obj=None):
        cached = CachedObj(
            lambda: next(iter(self.target_cls.manager().get({
                self.target_field: value
            })
            ), None)
        )
        return cached


class ReferenceField(BaseModelField):
    @property
    def target_cls(self):
        return self.target_cls_fn()

    def __init__(self, target_cls,
                 filter_conditions=None,
                 reference_field=None,
                 reference_getter=None,
                 cache=True,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not callable(target_cls):
            target_cls = lambda: target_cls()
        self.target_cls_fn = target_cls
        if filter_conditions and reference_field:
            raise TypeError("specify either 'filter_conditions' or 'reference_field'")

        self.single_value_condition = bool(filter_conditions)
        if filter_conditions:
            self.filter_conditions = filter_conditions
        else:
            self.reference_field = reference_field
            id_getter = lambda data: getattr(data, '_id')
            self.reference_getter = reference_getter or id_getter
            self.filter_conditions = {
                reference_field: self.reference_getter
            }
            self.cache = cache
            self.cached = {}

    def _get_concrete_conditions(self, obj):
        return {
            condition_field: condition_fn(obj) for condition_field, condition_fn in self.filter_conditions.items()
        }

    def _load(self, value, attr, src_obj):
        cache_key = id(value)
        if cache_key not in self.cached:
            conditions = self._get_concrete_conditions(src_obj)

            obj = CachedObj(lambda: self.target_cls.manager().get(conditions))
            if self.cache:
                self.cached[cache_key] = obj
            else:
                return obj
        return self.cached[cache_key]

    def _serialize(self, cached_value, attr, obj):
        if not self.single_value_condition:
            return [
                _value.serialize() for _value in cached_value.value
            ]
        return cached_value.value.serialize()
