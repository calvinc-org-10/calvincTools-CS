from typing import Any, Mapping, Callable
from .misctools import is_hashable

def str2(
    s: Any, 
    TypeTransforms: Mapping[type[Any], Callable[[], str]] | None = None,
    ValueTransforms: Mapping[Any, Callable[[], str]] | None = None,
    ) -> str:
    """
    Convert input to string, handling special values or types.
    
    Precedence: ValueTransforms is checked first for specific values, 
    then TypeTransforms is checked for type-based conversions.
    By default, None is converted to an empty string.
    
    :param s: Input value.
    :param TypeTransforms: Dict mapping types to callable functions that return strings.
    :param ValueTransforms: Dict mapping specific hashable values to callable functions that return strings.
                           Only applied to hashable types (not list, set, dict, bytearray).
    :return: String representation of input.
    """
    # Initialize default transforms if not provided
    if TypeTransforms is None:
        TypeTransforms = {type(None): lambda: ''}
    if ValueTransforms is None:
        ValueTransforms = {None: lambda: ''}
    
    # Check ValueTransforms first (higher priority for specific values)
    # Only check hashable types as dict keys (exclude list, set, dict, bytearray)
    if is_hashable(s):
        if s in ValueTransforms:
            return ValueTransforms[s]()
    
    # Check TypeTransforms (for type-based conversions)
    if type(s) in TypeTransforms:
        return TypeTransforms[type(s)]()
    
    # Default: use built-in str()
    return str(s)
# str2

def WrapInQuotes(strg, openquotechar = '"', closequotechar = '"'):
    return openquotechar + strg + closequotechar
# WrapInQuotes
def UnWrapQuotes(strg, quotechar = '"'):
    if strg.startswith(quotechar) and strg.endswith(quotechar):
        return strg[1:-1]
    return strg
# UnWrapQuotes

def IsWrappedInQuotes(strg, quotechar = '"'):
    return strg.startswith(quotechar) and strg.endswith(quotechar)
# IsWrappedInQuotes

