# callableabc

This package implements a metaclass and convenience instance of it that works like `abc.ABC`, but allows you to customize what happens when the class object gets called by implementing a `_class_call()` classmethod.

Inherit from the convenience class `CallableABC` to get this behavior,
or use the metaclass `CallableABCMeta` directly.

The metaclass uses the `CallableABCMetaDict` dictionary subclass to keep track of the `_class_call()` method.
