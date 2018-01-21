def requires_argument(argument_name="_id"):
    def requires_id_decorator(fn):
        def wrapper_fn(*args, **kwargs):
            val = kwargs.get(argument_name)
            if not val:
                raise TypeError("%s is required")
            return fn(*args, **kwargs)

        return wrapper_fn

    return requires_id_decorator
