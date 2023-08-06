from abc import ABCMeta


def make_callable_abc_meta(class_call_name: str, /) -> type:
    class CallableABCMeta(ABCMeta):
        def __init__(
            self, name: str, bases: tuple[type, ...], namespace: dict[str, object]
        ) -> None:
            if class_call_name not in namespace:
                namespace[class_call_name] = None
            super().__init__(name, bases, namespace)

        def __call__(self, *args: object, **kwargs: object) -> object:
            class_call = getattr(self, class_call_name, None)
            if class_call is not None and callable(class_call):
                return getattr(self, class_call_name)(*args, **kwargs)
            return super().__call__(*args, **kwargs)

    CallableABCMeta.__qualname__ = "CallableABCMeta"
    return CallableABCMeta


def make_callable_abc(class_call_name: str = "class_call", /) -> type:
    callable_abc = make_callable_abc_meta(class_call_name)(
        "CallableABC", (), {class_call_name: staticmethod(make_callable_abc)}
    )
    callable_abc.__qualname__ = "CallableABC"
    callable_abc.__module__ = "callableabc.callableabc"
    return callable_abc


CallableABC: type = make_callable_abc()
