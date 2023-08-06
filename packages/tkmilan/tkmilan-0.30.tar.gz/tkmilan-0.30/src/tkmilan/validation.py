'''Validation objects for `Spec <var.Spec>` variables.

All validation representations should be defined here, as standalone objects
that can be tested directly, without ``Tk`` dependencies.
:py:mod:`tkmilan.var` includes the ``Tk`` interfaces.
'''
import typing
import warnings
from dataclasses import dataclass, field as dc_field, InitVar
from collections import UserDict
from abc import ABCMeta
import operator
from numbers import Number

# Limit String
LIMIT_ISTRING: typing.Mapping[bool, str] = {
    True: '[',
    False: ']',
}
'''Mapping between inclusion boolean, and boundary representation.'''
LIMIT_INFINITE: str = '∞'
'''String representation of infinite boundary.'''


limT = typing.TypeVar('limT', bound=Number)
'''Generic Type for `var.Limit`.

This is a `typing.TypeVar`, to be used only when typechecking. See `typing`.
'''
smvT = typing.TypeVar('smvT')
'''Generic Type-Checking variable type for `SpecParsed`.

This is a `typing.TypeVar`, to be used only when typechecking. See `typing`.
'''


class VSpec(metaclass=ABCMeta):
    '''Abstract parent class for all validation representations.'''
    pass


class StaticList(typing.Tuple[str, ...], VSpec):
    '''Represent a static list of labels, therefore a :py:class:`tuple` of
    `str`.

    The default label must be explicitely given, either directly as
    ``default``, or indirectly as ``defaultIndex``. Either way is validated to
    verify the default is a valid label.

    Arguments:
        values: Values to construct the list.
        default: Default label. Optional.
        defaultIndex: Index for the default label, in the ``values`` sequence.
            Optional.
    '''
    ldefault: str
    '''The default label'''

    def __new__(cls, values: typing.Iterable[str], *,
                default: typing.Optional[str] = None,
                defaultIndex: typing.Optional[int] = None,
                ):
        self = super().__new__(cls, values)  # type: ignore[type-var,arg-type]
        assert default is not None or defaultIndex is not None, f'{self.__class__.__qualname__}: Missing default'
        if default is None:
            if defaultIndex is None or defaultIndex < 0 or defaultIndex >= len(self):
                raise ValueError(f'{self.__class__.__qualname__}: Invalid defaultIndex: {defaultIndex}')
            ldefault = self[defaultIndex]
        else:
            ldefault = default
        assert ldefault is not None, f'{self.__class__.__qualname__}: Missing default label'
        self.ldefault = ldefault
        if self.ldefault not in self:
            raise ValueError(f'{self.__class__.__qualname__}: Invalid Default Label: {self.ldefault!r}')
        return self


class StaticMap(UserDict, typing.Mapping[str, smvT], typing.Generic[smvT], VSpec):
    '''Represent a static mapping between labels and its corresponding values.

    The ``mapping`` parameter matches labels to values. This must be
    bi-injective, that is, there cannot be values corresponding to multiple
    labels.

    The default label must be explicitely given, either directly as
    ``defaultLabel``, or indirectly as ``defaultValue``. Either way is
    validated to verify the default is a valid label.

    Args:
        mapping: Mapping between labels and values.
        defaultLabel: Default label. Optional.
        defaultValue: Default value, to derive the default label. Optional.
    '''
    ldefault: str
    '''The default label'''

    def __init__(self, mapping: typing.Mapping[str, smvT], *,
                 defaultLabel: typing.Optional[str] = None,
                 defaultValue: typing.Optional[smvT] = None,
                 ):
        super().__init__(mapping)
        assert all(isinstance(lbl, str) for lbl in self.keys()), f'{self.__class__.__qualname__}: Mapping Keys must all be strings'
        rlabels: typing.Mapping[smvT, str] = {val: lbl for lbl, val in self.items()}
        if len(self) != len(rlabels):
            raise ValueError(f'{self.__class__.__qualname__}: Mapping is not bi-injective')
        assert defaultValue is not None or defaultLabel is not None, f'{self.__class__.__qualname__}: Missing default'
        # Setup the "other" default
        if defaultValue is None:
            if defaultLabel not in self:
                raise ValueError(f'{self.__class__.__qualname__}: Label {defaultLabel!r} not in mapping')
            assert defaultLabel is not None
            defaultValue = self[defaultLabel]
        if defaultLabel is None:
            if defaultValue not in rlabels:
                raise ValueError(f'{self.__class__.__qualname__}: Value {defaultValue!r} not in mapping')
            defaultLabel = rlabels[defaultValue]
        assert defaultValue is not None and defaultValue in rlabels
        assert defaultLabel is not None and defaultLabel in self
        self.rlabels = rlabels
        self.ldefault = defaultLabel
        self.vdefault = defaultValue


def StaticMapLabels(fn: typing.Callable[[str], smvT], lst: typing.Sequence[str], *, defaultIndex: typing.Optional[int] = None, **kwargs) -> StaticMap[smvT]:
    '''Turn a list of labels into a mapping, by applying a function to get the value.

    Wrapper for `StaticMap`.
    '''
    if defaultIndex is not None:
        kwargs['defaultLabel'] = lst[defaultIndex]
    return StaticMap({e: fn(e) for e in lst}, **kwargs)


def StaticMapValues(fn: typing.Callable[[smvT], str], lst: typing.Sequence[smvT], *, defaultIndex: typing.Optional[int] = None, **kwargs) -> StaticMap[smvT]:
    '''Turn a list of values into a mapping, by applying a function to get the label.

    Wrapper for `StaticMap`.
    '''
    if defaultIndex is not None:
        kwargs['defaultValue'] = lst[defaultIndex]
    return StaticMap({fn(e): e for e in lst}, **kwargs)


@dataclass
class LimitBounded(typing.Mapping[str, limT], typing.Generic[limT], VSpec):
    '''Represent a bounded range to limit a value, generic for any `number
    <numbers.Number>` type.

    The range can be made to remove the limits themselves with ``imin`` and
    ``imax``. The default is the limit being closed on both sides.

    The range is bounded, no there are no infinite limits.

    The following arguments are not available on the final object:

    Arguments:
        min_entry: Minumum value, as string or number.
        max_entry: Maximum value, as string or number.
        default: Default value to be set, as string, number, or `None` to
            choose a valid value (the default).
            When `None`, a sane value is chosen. If both ``imin`` and ``imax``
            as `False`, ``0`` is chosen, which might not be included on the
            range.
            Configures the default label.

    The following parameters are available on the final object:

    Arguments:
        fn: A function that turns a string into `number <numbers.Number>`.
            Usually some kind of parser.
        imin: Include the limit on the minumum value itself.
            Defaults to `True`.
        imax: Include the limit on the maximum value itself.
            Defaults to `True`.

    The following parameters are available on the final object, calculated from the arguments:

    Parameters:
        min: Minimum value, as number.
        min_value: Minimum value, as string. Good for showing to the user.
        max: Maximum value, as number.
        max_value: Maximum value, as string. Good for showing to the user.
        rrange: The `range` object implementing this object.
        ldefault: The default label to be shown to the user.

    .. automethod:: __len__
    .. automethod:: __getitem__
    .. automethod:: __iter__
    .. automethod:: __contains__
    '''
    min_entry: InitVar[typing.Union[limT, str]]
    max_entry: InitVar[typing.Union[limT, str]]
    fn: typing.Callable[[str], typing.Optional[limT]]
    imin: bool = True
    imax: bool = True
    # Calculations
    min: limT = dc_field(init=False)
    max: limT = dc_field(init=False)
    min_value: str = dc_field(init=False)
    max_value: str = dc_field(init=False)
    rrange: typing.Tuple[typing.SupportsIndex, typing.SupportsIndex, typing.SupportsIndex] = dc_field(init=False)
    # step: typing.Optional[limT] = None  # TODO: Support
    ldefault: str = dc_field(init=False)
    # __init__ variable
    default: InitVar[typing.Union[limT, str, None]] = None

    def __post_init__(self, min_entry: typing.Union[limT, str], max_entry: typing.Union[limT, str],
                      default: typing.Union[limT, str, None] = None):
        if isinstance(min_entry, str):
            self.min_value = min_entry
            min_obj = self.fn(self.min_value)
            if min_obj is None:
                raise ValueError(f'Invalid Minimum: {min_entry!r}')
            self.min = min_obj
        else:  # isinstance(min_entry, limT)
            self.min = min_entry
            self.min_value = str(self.min)
        if isinstance(max_entry, str):
            self.max_value = max_entry
            max_obj = self.fn(self.max_value)
            if max_obj is None:
                raise ValueError(f'Invalid Maximum: {max_entry!r}')
            self.max = max_obj
        else:  # isinstance(min_entry, limT)
            self.max = max_entry
            self.max_value = str(self.max)
        # Range
        step: limT = typing.cast(limT, 1)  # TODO: Support "step"
        imin: limT = typing.cast(limT, 0) if self.imin else step
        imax: limT = step if self.imax else typing.cast(limT, 0)
        assert isinstance(self.min, int) and isinstance(self.max, int), f'Unsupported Limit type: {self.min!r}/{self.max!r}'
        rfrom, rto = self.min + imin, self.max + imax
        assert rto > rfrom
        if step != typing.cast(Number, 1):
            # TODO: Support "step"
            raise ValueError(f'{self}: Unsupported step: {step!r}')
        self.rrange = range(rfrom, rto, step)
        assert len(self.rrange) > 0
        # Default
        if default is None:
            self.ldefault = {
                (True, True): self.min_value,
                (True, False): self.min_value,
                (False, True): self.max_value,
                (False, False): '0',  # `]x,y[`, just choose something
            }[(self.imin, self.imax)]
        elif isinstance(default, str):
            self.ldefault = default
        else:  # isinstance(default, limT)
            self.ldefault = str(default)
            default_roundtrip = self.fn(self.ldefault)
            if default_roundtrip is None or default != default_roundtrip:
                raise ValueError(f'{self}: Invalid Default Roundtrip: {default!r} != {default_roundtrip!r}')
        if self.ldefault not in self:
            raise ValueError(f'{self}: Invalid Default Label: {self.ldefault!r}')
        if __debug__:
            if self.fn in (int,):
                warnings.warn('Bad `fn`, throws exception on error, use `fn.valNumber`', stacklevel=3)
            if '' in self:
                warnings.warn('The empty string should be invalid', stacklevel=3)

    def __str__(self):
        lrange = LIMIT_ISTRING[self.imin]
        rrange = LIMIT_ISTRING[not self.imax]
        return '%s%s, %s%s' % (
            lrange,
            self.min_value,
            self.max_value,
            rrange,
        )

    def __len__(self) -> int:
        '''Count the amount of valid values.

        Should be used as ``len(LimitBounded)``.
        '''
        return len(self.rrange)

    def __iter__(self) -> typing.Iterator[str]:
        '''Iterate through all valid labels.

        Should be used as:

        .. code:: python

            for label in LimitBounded:
                print(label)
        '''
        for n in self.rrange:
            yield str(n)

    def __getitem__(self, label: str) -> limT:
        '''Get the value corresponding to the label.

        If the value is invalid, `KeyError` is raised.

        Should be used as ``LimitBounded[label]``.
        '''
        value = self.fn(label)
        if value is not None and value in self.rrange:
            return value
        else:
            raise KeyError

    def __contains__(self, label: object) -> bool:
        '''Check if the label is valid. Must be a `str`.

        Should be used as ``label in LimitBounded``.
        '''
        if isinstance(label, str):
            return self.get(label, None) is not None
        else:
            return False

    def get_label(self, value: typing.Optional[limT], *, invalid: str = '') -> str:
        '''Get a label that produces the given value.

        Args:
            value: The value object, or `None` to produce an invalid label.
            invalid: The invalid label. Make sure this is really invalid, this
            is not enforced.
        '''
        label = str(value)
        if value is not None and label in self:
            return label
        else:
            assert invalid not in self, 'Valid "invalid" value: {invalid}'
            return invalid


@dataclass
class LimitUnbounded(typing.Mapping[str, limT], typing.Generic[limT], VSpec):
    '''Represent an unbounded range to limit a value, generic for any `number
    <numbers.Number>` type.

    The range can be made to remove the limits themselves with ``imin`` and
    ``imax``. The default is the limit being closed on both sides.

    The range is unbounded, which mean some limits might be infinite.
    If both limits are infinite and this is intended, set ``infinite`` to avoid
    warnings.

    The following arguments are not available on the final object:

    Arguments:
        min_entry: Minumum value, as string or number.
            `None` represents an infinite value.
        max_entry: Maximum value, as string or number.
            `None` represents an infinite value.
        default: Default value to be set, as string, number, or `None` to
            choose a valid value (the default).
            When `None`, a sane value is chosen. If both ``imin`` and ``imax``
            as `False`, ``0`` is chosen, which might not be included on the
            range.
            Configures the default label.
        infinite: Do not warn about completely unbounded min and max.

    The following parameters are available on the final object:

    Arguments:
        fn: A function that turns a string into `number <numbers.Number>`.
            Usually some kind of parser.
        imin: Include the limit on the minumum value itself.
            Defaults to `True`.
        imax: Include the limit on the maximum value itself.
            Defaults to `True`.

    The following parameters are available on the final object, calculated from the arguments:

    Parameters:
        min: Minimum value, as number. `None` if infinite.
        min_value: Minimum value, as string. Good for showing to the user.
        max: Maximum value, as number. `None` if infinite.
        max_value: Maximum value, as string. Good for showing to the user.
        ldefault: The default label to be shown to the user.

    .. automethod:: __getitem__
    .. automethod:: __contains__
    '''
    min_entry: InitVar[typing.Union[limT, str, None]]
    max_entry: InitVar[typing.Union[limT, str, None]]
    fn: typing.Callable[[str], typing.Optional[limT]]
    imin: bool = True
    imax: bool = True
    # Calculations
    min: typing.Optional[limT] = dc_field(init=False)
    max: typing.Optional[limT] = dc_field(init=False)
    min_value: str = dc_field(init=False)
    max_value: str = dc_field(init=False)
    # step: typing.Optional[limT] = None  # TODO: Support
    ldefault: str = dc_field(init=False)
    # __init__ variable
    default: InitVar[typing.Union[limT, str, None]] = None
    infinite: InitVar[bool] = False

    def __post_init__(self, min_entry: typing.Union[limT, str, None], max_entry: typing.Union[limT, str, None],
                      default: typing.Union[limT, str, None],
                      infinite: bool):
        if min_entry is None:
            self.min = None
            self.min_value = f'-{LIMIT_INFINITE}'
            self.imin = False
        elif isinstance(min_entry, str):
            self.min_value = min_entry
            min_obj = self.fn(self.min_value)
            if min_obj is None:
                raise ValueError(f'Invalid Minimum: {min_entry!r}')
            self.min = min_obj
        else:  # isinstance(min_entry, limT)
            self.min = min_entry
            self.min_value = str(self.min)
        if max_entry is None:
            self.max = None
            self.max_value = f'+{LIMIT_INFINITE}'
            self.imax = False
        elif isinstance(max_entry, str):
            self.max_value = max_entry
            max_obj = self.fn(self.max_value)
            if max_obj is None:
                raise ValueError(f'Invalid Maximum: {max_entry!r}')
            self.max = max_obj
        else:  # isinstance(min_entry, limT)
            self.max = max_entry
            self.max_value = str(self.max)
        # Default
        if default is None:
            self.ldefault = {
                (True, True): self.min_value,
                (True, False): self.min_value,
                (False, True): self.max_value,
                (False, False): '0',  # Any number is valid (or `]x,y[`, just choose something)
            }[(self.min is not None and self.imin, self.max is not None and self.imax)]
        elif isinstance(default, str):
            self.ldefault = default
        else:  # isinstance(default, limT)
            self.ldefault = str(default)
            default_roundtrip = self.fn(self.ldefault)
            if default_roundtrip is None or default != default_roundtrip:
                raise ValueError(f'{self}: Invalid Default Roundtrip: {default!r} != {default_roundtrip!r}')
        if self.ldefault not in self:
            raise ValueError(f'{self}: Invalid Default Label: {self.ldefault!r}')
        if __debug__:
            if self.fn in (int,):
                warnings.warn('Bad `fn`, throws exception on error, use `fn.valNumber`', stacklevel=3)
            if not infinite and (self.min is None and self.max is None):
                warnings.warn('No limit to possible values', stacklevel=3)
            if '' in self:
                warnings.warn('The empty string should be invalid', stacklevel=3)

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __str__(self):
        lrange = LIMIT_ISTRING[self.imin]
        rrange = LIMIT_ISTRING[not self.imax]
        return '%s%s, %s%s' % (
            lrange,
            self.min_value,
            self.max_value,
            rrange,
        )

    def __getitem__(self, label: str) -> limT:
        '''Get the value corresponding to the label.

        If the value is invalid, `KeyError` is raised.

        Should be used as ``LimitUnbounded[label]``.
        '''
        value = self.fn(label)
        if value is None:
            raise KeyError
        else:
            OPERATOR: typing.Mapping[bool, typing.Callable[..., bool]] = {True: operator.le, False: operator.lt}
            omin = OPERATOR[self.imin]
            omax = OPERATOR[self.imax]
            if all((
                (omin(self.min, value) if self.min is not None else True),  # vmin
                (omax(value, self.max) if self.max is not None else True),  # vmax
                # TODO: Support "step"
                # ((value - self.min) % self.step == 0 if self.step is not None else True)  # step
            )):
                return value
            else:
                raise KeyError

    def __contains__(self, label: object) -> bool:
        '''Check if the label is valid. Must be a `str`.

        Should be used as ``label in LimitUnbounded``.
        '''
        if isinstance(label, str):
            return self.get(label, None) is not None
        else:
            return False

    def get_label(self, value: typing.Optional[limT], *, invalid: str = '') -> str:
        '''Get a label that produces the given value.

        Args:
            value: The value object, or `None` to produce an invalid label.
            invalid: The invalid label. Make sure this is really invalid, this
            is not enforced.
        '''
        label = str(value)
        if value is not None and label in self:
            return label
        else:
            assert invalid not in self, 'Valid "invalid" value: {invalid}'
            return invalid

    def as_bounded(self) -> 'LimitBounded':
        '''Create a `LimitBounded` with the same parameters.

        Raises `ValueError` if this is impossible.
        '''
        if self.min is None or self.max is None:
            raise ValueError(f'{self}: Not bounded, impossible to convert')
        return LimitBounded(self.min, self.max, fn=self.fn,
                            imin=self.imin, imax=self.imax,
                            default=self.ldefault,
                            )
