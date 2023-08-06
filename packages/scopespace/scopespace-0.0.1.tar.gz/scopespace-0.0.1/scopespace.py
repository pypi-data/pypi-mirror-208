import types
import inspect
from typing import Any, Dict, Optional, Type

class ScopeSpace:
    """
    A scoped namespace. A context manager, inside of which all new declarations
    are locally scoped, like a function that only runs once. But, after the `with`
    block, all those declarations are accessible through the namespace you created.

    In a way, it's like a portable module within your module.

    This is great for working in notebooks, where you might define many versions
    or iterations of a dataframe but you're sick of coming up with new names each time.
    Now, you can always use `df`, and just organize each iteration into its own
    namespace.
    
    Or, declare a new ScopeSpace at the beginning of each notebook cell, and have the
    work you do in that cell be locally scoped.

    Example:

        with ScopeSpace() as version1:
            df = pd.DataFrame()
            def some_func():
                pass
            class Test:
                pass

        print(df)  # NameError: name 'df' is not defined
        print(version1.df)  # Works!

    "Namespaces are one honking great idea -- let's do more of those!"
        - Tim Peters, 'The Zen of Python'
    """
    namespace: types.SimpleNamespace
    context_backup: Dict[str, Any]

    def __enter__(self) -> types.SimpleNamespace:
        self.namespace = types.SimpleNamespace()
        frame = inspect.currentframe().f_back  # type:ignore
        is_function_frame = frame.f_code.co_name != "<module>"  # type:ignore
        if is_function_frame:
            raise ValueError("ScopeSpace cannot be used inside functions.")
        self.context_backup = {k: v for k, v in globals().items()}
        return self.namespace

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        """
        For each NEW key in globals, add it to the namespace.
        For each key that was already in globals, check if it's current value is the same object as
        the one we backed up. If it's a new object, then this means the user RE-declared it within their
        namespace. In this case, we mimic the behavior of functions and replace the modified
        global variable with its original backed up version, and add the new version to the namespace.
        """
        new_context = {k: v for k, v in globals().items()}
        for key, val in new_context.items():
            if val is self.namespace:
                continue
            if key not in self.context_backup:
                setattr(self.namespace, key, val)
                del globals()[key]
            elif key in self.context_backup and val is not self.context_backup[key]:
                setattr(self.namespace, key, val)
                # Restore the original version of the variable
                globals()[key] = self.context_backup[key]


if __name__ == '__main__':
    x = [1, 2, 3]
    with ScopeSpace() as test:
        x.append(4)

    print(x)  # [1, 2, 3, 4]
    # print(test.x)  # AttributeError

    x2 = [1, 2, 3]
    with ScopeSpace() as test2:
        x2.append(99)
        x2 = x2 + [4]
        b = 10

    print(x2)  # [1, 2, 3, 99]
    print(test2.x2)  # [1, 2, 3, 99, 4]
    print(test2.b)  # 10
    # print(b) # NameError

