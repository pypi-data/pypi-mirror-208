'''All the mixin classes, to be reused internally.
'''
import logging
import warnings
import typing
from dataclasses import dataclass
import collections
from functools import cached_property, partial

from . import fn
from . import model
from . import var as tkmilan_var  # Possible name alias
from . import autolayout
from . import exception
from . import validation

import tkinter as tk

ProxyWidgetT = typing.TypeVar('ProxyWidgetT', bound='MixinWidget')
if typing.TYPE_CHECKING:
    from . import RootWindow

logger = logging.getLogger(__name__)
logger_traces = logging.getLogger('%s.traces' % __name__)
logger_valid = logging.getLogger('%s.valid' % __name__)
logger_grid = logging.getLogger('%s.grid' % __name__)

WEIRD_WIDGET_NAME = (  # Weird Widget `dir` names, these cause trouble
    '_last_child_ids',
    'wroot',
)
WIDGET_VALIDATION_CFG = (
    'validate',
    'validatecommand',
    'invalidcommand',
)


# Technically a model, but internal
@dataclass
class ContainerState:
    '''Full container state.

    Arguments:
        swidgets: Single Widgets
        cwidgets: Container Widgets
        variables: Attached Variables
        wvariables: Mapping VariableID -> Variable object
        vwidgets: Mapping VariableID -> Widget Name list
        vid_upstream: Set of upstream VariableID
        hswidgets: Helper Single Widgets.
            Technically not considered as "state", only matters for tracing
            purposes.
            Includes widgets that might be ignored using `ignoreContainerState
            <MixinWidget.ignoreContainerState>`, check this when using if this
            is not intended.
        hcwidgets: Helper Container Widgets.
            Technically not considered as "state", only matters for tracing
            purposes.
    '''
    swidgets: 'typing.Mapping[str, SingleWidget]'
    cwidgets: 'typing.Mapping[str, ContainerWidget]'
    variables: 'typing.Mapping[str, tkmilan_var.Variable]'
    wvariables: 'typing.Mapping[str, tkmilan_var.Variable]'
    vwidgets: typing.Mapping[str, typing.Sequence[str]]
    vid_upstream: typing.Set[str]
    hswidgets: 'typing.Set[SingleWidget]'
    hcwidgets: 'typing.Set[ContainerWidget]'


class MixinState:
    '''Mixin for all stateful widgets.'''

    wstate_static: bool = True
    '''
    Define if the `MixinState.setup_state` cache is static. or a callable for dynamic
    calculations.

    See `stateSetup`.
    '''

    isNoneable: typing.Optional[bool] = None
    '''Define if a `None` result leads to skipping this widget on the state result.

    This applies to both static and dynamic state calculations. Defaults to
    `None`, so that it can be overriden by subclasses.

    For dynamic calculations, the results for some widgets might vary depending
    on where the root state starts, so they will be unpredictable. When the
    state is taken as a whole (the simple usage), it is predictable.

    Note:
        The default `None` value for this variable is invalid. The subclass
        **must** define this.
    '''

    def setup_state(self):
        '''Define an object that will be cached forever.

        This can have a static object, or a dynamic `callable`.

        See `MixinState.wstate_static`, `stateSetup`.
        '''
        raise NotImplementedError

    @cached_property
    def stateSetup(self):
        '''Obtain the state setup.

        This takes into account the `wstate_static` flag, producing a static object
        or a callable.

        This should always be used, `MixinState.setup_state` is only a definition.
        '''
        assert self.isNoneable is not None, f'{self} needs `isNoneable` choice'
        if self.wstate_static is True:
            return self.setup_state()
        else:
            return self.setup_state

    def state_get(self, *args, **kwargs):
        '''Define how to get the widget state.

        The kwargs are only passed for Dynamic State widgets
        '''
        raise NotImplementedError

    '''
    Define how to set the widget state.

    The kwargs are only passed for Dynamic State widgets
    '''
    def state_set(self, state, substate: bool, **kwargs):
        raise NotImplementedError

    # Wrapper functions for the property
    def wstate_get(self, *args, **kwargs):
        return self.state_get(*args, **kwargs)

    def wstate_set(self, state, *args, substate=False, **kwargs):
        return self.state_set(state, *args, substate=substate, **kwargs)

    wstate = property(wstate_get, wstate_set, doc='Widget State')


class MixinStateSingle(MixinState):
    '''
    Mixin class for single widgets.

    Note:
        When subclassing this, define `MixinState.setup_state` to return the
        variable containing the widget state.
    '''
    wstate_static: bool = True

    def state_get(self):
        return self.stateSetup.get()

    def state_set(self, state, substate):
        if __debug__:
            if substate is True:  # Just skip it silently?
                warnings.warn("`substate` doesn't apply here", stacklevel=3)
        self.stateSetup.set(state)


class MixinStateContainer(MixinState):
    '''Mixin class for container widgets.

    To ignore a container state, define this on the subclass:

    .. code:: python

        def setup_state(self, **kwargs):
            return {}

    Note:
        When subclassing this, define `MixinState.setup_state` to return a
        dictionary mapping subwidget identifier to `WidgetDynamicState`.
    '''
    wstate_static: bool = False
    wstate_single: typing.Optional[str] = None
    '''
    Mark the container state as "single", including only the state for this child.

    Should only be enabled where there is a single child element, this is
    verified when getting the value. Use `MixinWidget.ignoreContainerState` to
    ignore other widgets.

    This creates no performance improvements, it is only useful to simplify the
    state.
    '''

    def state_get(self, **kwargs):
        state = {}
        for identifier, wds in self.stateSetup(**kwargs).items():
            result = wds.getter()
            if wds.noneable and result is None:
                pass  # Skip
            else:
                state[identifier] = result
        if self.wstate_single is None:
            # - Multiple WState
            if len(state) == 0:
                return None
            else:
                if __debug__:
                    wid0 = list(state)[0]
                    if len(state) == 1 and ':' not in wid0:
                        # TODO: Use `warnings.warn`, but this is used from an `after` function, the trace is lost.
                        logger.warning('%s: This widget can be marked "wstate_single": `%s`', self, wid0)
                return state
        else:
            # - Single WState (wstate_single)
            assert len(state) == 1, f'{self}: Invalid "wstate_single" marking, {len(state)} elements'
            return state[self.wstate_single]

    def state_set(self, state, substate, **kwargs) -> None:
        # # Debug container state flow
        # self_names = None
        # if __debug__:
        #     self_names = str(self).split('.')[1:]
        #     logger.debug('%s: %s%s',
        #                  '>' * len(self_names),
        #                  self,
        #                  '' if self.wstate_single is None else f' [{self.wstate_single}]',
        #                  )
        for identifier, wds in self.stateSetup(**kwargs).items():
            # Skip State Setup:
            # - "noneable" and the state is None
            if wds.noneable and state is None:
                skip = True
            else:
                if self.wstate_single is None:
                    # - Multiple WState
                    #   - Check for "noneable"
                    #   - Check for (substate=True)
                    skip = (substate or wds.noneable) and identifier not in state
                else:
                    # - Single WState (wstate_single)
                    skip = self.wstate_single != identifier
            if skip:
                # if __debug__:
                #     logger.debug('%s|> Skip "%s"', ' ' * len(self_names), identifier)
                pass
            else:
                # if __debug__:
                #     logger.debug('%s|>  Set "%s"', ' ' * len(self_names), identifier)
                if self.wstate_single:
                    widget_state = state
                else:
                    widget_state = state[identifier]
                if wds.container:
                    wds.setter(widget_state, substate, **kwargs)
                else:
                    wds.setter(widget_state)


class MixinWidget:
    '''Parent class of all widgets.

    Args:
        gkeys: Append widget-specific `model.GuiState` keys to common list
            `model.GUI_STATES_common`.

    .. autoattribute:: _bindings
    .. autoattribute:: _tidles
    '''

    wparent: 'typing.Optional[MixinWidget]' = None
    '''A reference to the parent widget.'''
    gkeys: typing.FrozenSet[str]
    '''The supported `model.GuiState` keys.'''
    isAuto: typing.Optional[bool]
    '''Marker that tracks the automatic state setup.

    One of the following values:

    - `True`: Include on automatic widget and GUI states. Default.
    - `False`: No automatic widget state, but keep in on the GUI state. This
      makes the widget stateless, but it still participates in the automatic
      GUI state changes.
      Very useful for helper containers.
    - `None`: No automatic widget nor GUI states. This makes the widget
      basically invisible.

    .. note::

        This was called ``isHelper`` in older versions.
        Turn all ``isHelper=False`` into ``isAuto=False`` (unless you have a
        good reason to isolate GUI state).
    '''
    ignoreContainerState: bool = False
    '''Ignore this widget's state when included on a container.'''
    styleID: typing.Optional[str] = None
    '''StyleID for this widget. See `RootWindow.styleIDs`.'''
    wproxy: 'typing.Optional[MixinWidget]' = None
    '''Link to the corresponding proxy widget, if exists.

    See Also:
        The base `ProxyWidget` class.
    '''
    proxee: 'typing.Optional[MixinWidget]' = None
    '''Link to the corresponding proxied widget, if exists.

    See Also:
        The base `ProxyWidget` class.
    '''
    _bindings: typing.MutableMapping[str, model.Binding]
    '''Store all widget `Binding` objects, keyed by name (see `binding`).'''
    _tidles: typing.MutableMapping[str, model.TimeoutIdle]
    '''Store some widget `TimeoutIdle` objects, keyed by name (see `tidle`).'''

    def __init__(self, *,
                 gkeys: typing.Optional[typing.Iterable[str]] = None,
                 ):
        assert not hasattr(self, 'isHelper'), f'{self.__class__.__qualname__}: Invalid "isHelper" marker, migrate to "isAuto"'
        self.isAuto: typing.Optional[bool] = getattr(self, 'isAuto', True)
        self._bindings = {}
        self._tidles = {}
        gk = set(model.GUI_STATES_common)
        if gkeys is not None:
            gk.update(gkeys)
        self.gkeys = frozenset(gk)

    @cached_property
    def wroot(self) -> 'RootWindow':
        '''Get the root widget, directly.

        Does not use the ``wparent`` property to crawl the widget tree to the
        top, so that it might be called before that setup is done (during setup
        of lower widgets, for example).
        '''
        assert isinstance(self, (tk.Widget, tk.Tk)), f'{self} is not a valid widget'
        widget = self.nametowidget('.')
        if __debug__:
            from . import RootWindow  # For typechecking
        assert isinstance(widget, RootWindow)
        return widget

    def wroot_search(self) -> 'RootWindow':
        '''Alternative to `wroot` that crawls the widget tree.

        Use the `wparent` proprety.

        See Also:
            `wroot`: Simpler alternative to this function, crawling the widget
            tree. Requires all widgets to be stable.
        '''
        if self.wparent is None:
            # This might be triggered if called before all widgets are stable
            if __debug__:
                from . import RootWindow  # For typechecking
            assert isinstance(self, RootWindow), f'Invalid "root" widget: {self!r}'
            return self
        else:
            return self.wparent.wroot_search()

    def binding(self, sequence: str, *args, key: typing.Optional[str] = None, immediate: bool = True, **kwargs) -> model.Binding:
        '''Create a `model.Binding` for this widget.

        Stores all widget bindings on a per-instance dictionary, for later
        usage. Note that all dictionary keys must be different. For the same
        bindings on a single widget, this requires passing the ``key``
        argument.

        See the ``Tk`` `bind <https://www.tcl.tk/man/tcl/TkCmd/bind.html>`_ documentation.

        Args:
            key: Optional. Defaults to the ``sequence`` itself. Useful to
                support multiple bindings on the same sequence.
            immediate: Passed to the upstream object, default to enabling the
                binding on creation. This is the opposite from upstream.

        All other arguments are passed to the `model.Binding` object.
        '''
        name = key or sequence
        if name in self._bindings:
            raise ValueError(f'Repeated Binding for "{sequence}" in {self!r}. Change the "key" parameter.')
        self._bindings[name] = model.Binding(self, sequence, *args, immediate=immediate, **kwargs)
        return self._bindings[name]

    def tidle(self, action: typing.Callable, *args, key: typing.Optional[str] = None, **kwargs) -> model.TimeoutIdle:
        '''Create a `model.TimeoutIdle` for this widget.

        Stores all idle timeouts created using this function on a per-instance
        dictionary, for later usage. If the ``action`` is not a "real"
        function, this requires passing the ``key`` argument.

        Args:
            key: Optional. Defaults to the ``action`` name.

        All other arguments are passed to `model.Binding` object.
        '''
        name = key or action.__name__
        if name in self._tidles:
            raise ValueError(f'Repeated TimeoutIdle for "{name}" in {self!r}.')
        self._tidles[name] = model.TimeoutIdle(self, action, *args, *kwargs)
        return self._tidles[name]

    @property
    def size_vroot(self) -> 'model.PixelSize':
        '''The VirtualRoot size.

        This is a global property, but it's available in every widget.
        '''
        assert isinstance(self, (tk.Widget, tk.Tk)), f'{self} is not a valid tkinter.Widget'
        return model.PixelSize(
            width=self.winfo_vrootwidth(),
            height=self.winfo_vrootheight(),
        )

    @property
    def size_screen(self) -> 'model.PixelSize':
        '''The screen size.

        This is a global property, but it's available in every widget.
        '''
        assert isinstance(self, (tk.Widget, tk.Tk)), f'{self} is not a valid tkinter.Widget'
        return model.PixelSize(
            width=self.winfo_screenwidth(),
            height=self.winfo_screenheight(),
        )

    def setup_grid(self, fmt: typing.Union[str, model.GridCoordinates], **kwargs) -> None:
        '''Configure the grid for the current widget.

        ``fmt`` can be given as a `model.GridCoordinates`, or as a single
        `str`, to be parsed by `model.GridCoordinates.parse`.

        Args:
            fmt: The grid configuration format. Specified above.
            kwargs: Passed upstream

        See Also:
            `wgrid`: Get the current widget grid coordinates.
        '''
        assert isinstance(self, (tk.Widget, tk.Tk)), f'{self} is not a valid tkinter.Widget'
        if isinstance(fmt, str):
            fmt = model.GridCoordinates.parse(fmt)
        kwargs.update(fmt.dict())
        self.grid(**kwargs)

    @property
    def wgrid(self) -> typing.Optional[model.GridCoordinates]:
        '''Get the widget grid coordinates, if the widget is visible.

        Returns:
            Return a `model.GridCoordinates` object with the widget information. If
            the wiget was hidden, return `None`.

            This is also available for the root widget (`wroot`) for
            completeness, but that doesn't really correspond to any grid,
            return `None`.

        See Also:
            `setup_grid`: Change the widget grid coordinates.
        '''
        if self == self.wroot:
            assert isinstance(self, tk.Tk)
            return None
        else:
            assert isinstance(self, tk.Widget), f'{self} is not a valid tkinter.Widget'
            # If the grid information doesn't exist, default to a single frame
            # Force elements to integer, on tcl v8.5 they are returned as strings
            ginfo = self.grid_info()
            if ginfo:
                return model.GridCoordinates(
                    row=int(ginfo.get('row', 0)),
                    rowspan=int(ginfo.get('rowspan', 1)),
                    column=int(ginfo.get('column', 0)),
                    columnspan=int(ginfo.get('columnspan', 1)),
                )
            else:
                return None

    def get_gui_state(self) -> model.GuiState:
        if __debug__:
            from . import RootWindow  # For typechecking
        assert isinstance(self, (tk.ttk.Widget, RootWindow)), f'{self} is not a valid tkinter.ttk.Widget'
        state: typing.MutableMapping[str, typing.Optional[bool]] = {}
        for estr in self.gkeys:
            itk = model.GUI_STATES[estr]
            state[estr] = self.instate([itk.gstr()])
            # logger.debug('  [%s] » %s', itk.gstr(), state[estr])
        rval = model.GuiState(**state)
        # if __debug__:
        #     logger.debug('State > %r', rval)
        return rval

    def set_gui_state(self, state: typing.Optional[model.GuiState] = None, **kwargs) -> model.GuiState:
        assert isinstance(self, tk.ttk.Widget), f'{self} is not a valid tkinter.ttk.Widget'
        if state is None:
            state = model.GuiState(**kwargs)
        states = []
        # if __debug__:
        #     logger.debug('State < %r', state)
        for estr, sval, itk in state.items_tk():
            if sval is not None:
                assert estr in self.gkeys, f'{self.__class__.__qualname__}| Invalid GuiState: {estr}'
                # Invert `sval` when `itk.invert` == `sval XOR itk.invert`
                if sval is not itk.invert:
                    tkstr = '%s' % itk.string
                else:
                    tkstr = '!%s' % itk.string
                # if __debug__:
                #     logger.debug('  [%s %s] » %s', sval, itk.invert, tkstr)
                states.append(tkstr)
        self.state(states)
        assert state is not None
        if self.wproxy:
            # if __debug__:
            #     logger.debug('  Set Widget Proxy State')
            self.wproxy.gstate = state
        return state

    # Wrapper functions for the property
    def gstate_get(self):
        return self.get_gui_state()

    def gstate_set(self, state: model.GuiState):
        # Don't store the return object
        self.set_gui_state(state)

    # TODO: This can be even better
    # Support `widget.gstate.enabled = NEW_VALUE`
    # Not a property, but a class that changes `self`
    gstate = property(gstate_get, gstate_set, doc='GUI State')

    def putHelper(self, value: bool = True) -> 'MixinWidget':
        '''DEPRECATED. See `putAuto`.'''
        # raise NotImplementedError('DEPRECATED')  # TODO: Include on v0.25
        return self.putAuto(False if value else True)

    # TODO: On Python 3.11:: -> typing.Self
    def putAuto(self, value: typing.Optional[bool] = False) -> 'MixinWidget':
        '''Set the `isAuto` marker on itself.

        See `MixinWidget.isAuto` for more information on the possible values.
        Defaults to `False`.

        This is designed to be used inside the `setup_widgets
        <ContainerWidget.setup_widgets>` function, like this:

        .. code:: python

            def setup_widgets(self, ...):
                self.w1 = Widget(self, ...).putAuto()      # No GUI  No State
                self.w1 = Widget(self, ...).putAuto(None)  # No GUI Yes State

        This is usually called "method chaining", or "fluent interface".
        '''
        if value is True:
            warnings.warn(f'Redundant `putAuto` @ {self!r}')
        self.isAuto = value
        return self

    # TODO: On Python 3.11:: -> typing.Self
    def putIgnoreState(self, value: bool = True) -> 'MixinWidget':
        '''Set the `ignoreContainerState` marker on itself.

        This is designed to be used inside the `setup_widgets
        <ContainerWidget.setup_widgets>` function, like this:

        .. code:: python

            def setup_widgets(self, ...):
                self.w1 = Widget(self, ...).putIgnoreState()

        This is usually called "method chaining", or "fluent interface".
        '''
        # TODO: Move this "method chaining" to a common document.
        self.ignoreContainerState = value
        return self


class MixinTraces:
    '''Mixin class for variable traces.'''
    def init_traces(self) -> None:
        self._traces: typing.MutableMapping[str, str] = {}
        assert isinstance(self, (SingleWidget, ContainerWidget)), f'{self.__class__.__qualname__}: Unsupported tracing for this Widget'
        assert self.variable is not None, f'{self}: Widget untraceable'

    def trace(self, function: typing.Callable, *, trace_name: typing.Optional[str] = None, **kwargs: typing.Any) -> str:
        '''Trace the variable associated to the current widget.

        The underlying function is `tkmilan.var.trace`, check it for more
        detailed documentation.

        Args:
            function: The callback function.
            trace_name: A name for the trace reference. Must be unique for the
                widget. Optional, uses an automatic name otherwise.
            kwargs: Passed to the `tkmilan.var.trace` function.
        '''
        assert isinstance(self, (SingleWidget, ContainerWidget)), f'{self.__class__.__qualname__}: Unsupported tracing for this Widget'
        assert self.variable is not None, f'{self}: Widget untraceable'
        function_name = tkmilan_var.trace(self.variable, function, **kwargs)
        key = trace_name or function_name
        assert key not in self._traces, f'{self}: Repeated trace name: {key}'
        self._traces[key] = function_name
        logger_traces.debug('%s: New Trace "%s"', self.variable, key)
        return function_name


# TODO: Add this on SingleWidget? Support containers too?
# TODO: Leverage synergies with specValues
class MixinValidation:
    '''Mixin class for widget validation.'''
    vsettings: typing.Optional[model.VSettings]

    def init_validation(self, validation: typing.Union[model.VSettings, bool, None] = None) -> model.VSettings:
        assert isinstance(self, (tk.Widget, tk.Tk)), f'{self} is not a valid tkinter.Widget'
        assert isinstance(self, MixinWidget), f'{self} is not a valid tkmilan widget'
        assert isinstance(self, SingleWidget), f'{self.__class__.__qualname__}: Unsupported validation for this Widget'
        assert isinstance(self.variable, tkmilan_var.Spec), f'{self.__class__.__qualname__}: Non-Spec variable type'   # TODO
        if __debug__:
            cfg_defaults = {'validate': 'none', 'validatecommand': '', 'invalidcommand': ''}
            assert set(cfg_defaults) == set(WIDGET_VALIDATION_CFG)
            for cfg, cfg_default in cfg_defaults.items():
                assert self.configure(cfg)[4] == cfg_default, f'{self}: Invalid validation setting "{cfg}": Use `validation` only'
        if validation is True:
            if __debug__:
                logger_valid.debug('%s: Setup Default Validation', self)
            valobj = model.VSettings(fnSimple=True)
        elif validation in (False, None):
            valobj = None
        else:
            assert isinstance(validation, model.VSettings)
            valobj = validation
        if valobj is None:
            if __debug__:
                logger_valid.debug('%s: Setup Validation: None', self)
            self.vsettings = None
        else:
            valobj.fn = valobj.fn or self.setup_validation  # Configure the "natural" validation
            if __debug__:
                logger_valid.debug('%s: Setup Validation: %s', self, valobj)
            self.vsettings = valobj
            if valobj.postInitial:
                # No need for a `TimeoutIdle` here
                self.after_idle(lambda var=self.variable: self.__validPost(var, None, vtype='initial'))
            if valobj.postVar:
                self.trace(self.__validPost, vtype='self',
                           trace_name='__:valid:postVar')
            self.__validCommand: typing.Callable[
                [str, model.ValidateWhyT, model.ValidateST],
                typing.Union[bool, typing.Literal['break']],
            ]
            if valobj.fnSimple:
                self.__validCommand = self.__validCommandSimple
            else:
                self.__validCommand = self.__validCommandComplex
            self.configure(
                validate=valobj.tkWhen,
                validatecommand=(self.register(self.__validCommand), '%P', '%V', '%d'),
                invalidcommand='',  # TODO: Support something like this?
            )
        return valobj

    def setup_validation(self, vstate: model.VState, vwhy: typing.Optional[model.VWhy] = None) -> typing.Optional[bool]:
        '''Define the "natural" widget validation, checking the state validation.

        Some widgets might have a different "natural" widget validation function.

        When this does not apply, use `fn.validation_pass`.
        '''
        if __debug__:
            if isinstance(vstate, str):
                logger.warning('%s: Old and Busted Validation [%s]', self, self.__class__.__qualname__)
        return vstate.valid

    def doValidation(self, n=None, i=None, t=None) -> None:
        '''Force widget Post-Validation.

        Wraps the upstream function with optional arguments, to be used
        directly on `trace <MixinTraces.trace>`, `Binding`, etc.

        All arguments are ignored.
        '''
        assert isinstance(self, SingleWidget), f'{self.__class__.__qualname__}: Unsupported validation for this Widget'
        # assert isinstance(self, (tk.ttk.Entry)), f'{self} is not a valid Entry'
        # Reimplement `self.validate`
        self.__validPost(self.variable, None, vtype='forced')

    def __validCommandSimple(self,
                             vstate: typing.Union[str, model.VState],
                             why: model.ValidateWhyT,
                             whyNum: model.ValidateST,
                             ) -> typing.Union[bool, typing.Literal['break']]:
        assert isinstance(self, SingleWidget), f'{self.__class__.__qualname__}: Unsupported validation for this Widget'
        always_vstate: model.VState
        if isinstance(vstate, str):
            always_vstate = self.variable.get()
            assert always_vstate.label == vstate, f'Weird vstate mismatch:: {always_vstate} != vstate'
        else:
            always_vstate = vstate
        # Upstream Validation Command, do not calculate `vwhy`
        assert self.vsettings is not None
        assert self.vsettings.fn is not None
        assert self.vsettings.fnSimple is True
        rval = self.vsettings.fn(always_vstate, None)
        logger_valid.debug('%s: validation=%s', self, rval)
        return 'break' if rval is None else rval

    def __validCommandComplex(self,
                              vstate: typing.Union[str, model.VState],
                              why: model.ValidateWhyT,
                              whyNum: model.ValidateST,
                              ) -> typing.Union[bool, typing.Literal['break']]:
        assert isinstance(self, SingleWidget), f'{self.__class__.__qualname__}: Unsupported validation for this Widget'
        always_vstate: model.VState
        if isinstance(vstate, str):
            always_vstate = self.variable.get()
            assert always_vstate.label == vstate
        else:
            always_vstate = vstate
        # Upstream Validation Command, calculate `vwhy`
        assert isinstance(self, MixinWidget), f'{self} is not a valid tkmilan widget'
        assert self.vsettings is not None
        assert self.vsettings.fn is not None
        assert self.vsettings.fnSimple is False
        vwhy = model.VWhy(vstate=always_vstate, widget=self, why=why, t=whyNum)
        rval = self.vsettings.fn(always_vstate, vwhy)
        logger_valid.debug('%s: validation=%s why=%s', self, rval, vwhy)
        return 'break' if rval is None else rval

    def __validPost(self, var, etype, *, vtype: model.ValidateWhyT):
        assert isinstance(self, MixinWidget), f'{self} is not a valid tkmilan widget'
        # Keep the GUI "valid" state up to date
        self.set_gui_state(valid=self.__validCommand(var.get(), vtype, -1))

    def setDefault(self) -> None:
        '''Set the current state to the default label.'''
        assert isinstance(self, SingleWidget), f'{self.__class__.__qualname__}: Unsupported validation for this Widget'
        assert isinstance(self.variable, tkmilan_var.Spec), f'{self.__class__.__qualname__}: Non-`Spec` variable type'
        self.wstate = self.variable.ldefault

    def eSet(self, label: str) -> typing.Callable[..., None]:
        '''Return an event function to set the state a certain label.

        Returns:
            Return a function that can be attached to a `Binding`, `trace
            <MixinTraces.trace>`, or even called directly.
        '''
        assert isinstance(self, SingleWidget), f'{self.__class__.__qualname__}: Unsupported validation for this Widget'
        assert isinstance(self.variable, tkmilan_var.Spec), f'{self.__class__.__qualname__}: Non-`Spec` variable type'
        if label not in self.variable:
            raise exception.InvalidCallbackDefinition(f'Setting an invalid label: {label}')

        def eSet(n=None, i=None, t=None):
            self.wstate = label
        return eSet

    def eSetValue(self, value: typing.Any) -> typing.Callable[..., None]:
        '''Wraper for `eSet`, to set a value instead.

        Requires the widget to have a `specificed variable <SpecParsed>`.
        '''
        assert isinstance(self, SingleWidget), f'{self.__class__.__qualname__}: Unsupported validation for this Widget'
        assert isinstance(self.variable, tkmilan_var.SpecParsed), f'{self.__class__.__qualname__}: Non-`SpecParsed` variable type'
        return self.eSet(self.variable.getLabel(value))


# High-Level Mixins


class SingleWidget(MixinWidget, MixinStateSingle, MixinTraces):
    '''Parent class of all single widgets.'''
    variable: typing.Optional[tkmilan_var.Variable] = None
    state_type: typing.Optional[typing.Type[tkmilan_var.Variable]] = None

    def init_single(self,
                    vspec: typing.Union[None, tkmilan_var.Variable, validation.VSpec] = None,
                    gkeys: typing.Optional[typing.Iterable[str]] = None,
                    ) -> None:
        '''Setup all single widget stuff.

        Includes:

        - Variable settings (Supports creating new variables)
        - `tkmilan.mixin.MixinState.isNoneable` calculation
        '''
        MixinWidget.__init__(self, gkeys=gkeys)
        self.variable = self.setup_variable(vspec)
        MixinTraces.init_traces(self)
        if self.isNoneable is None:
            # Calculate isNoneable option
            self.isNoneable = self.state_type is tkmilan_var.nothing

    def setup_variable(self, vspec: typing.Union[None, tkmilan_var.Variable, validation.VSpec]) -> tkmilan_var.Variable:
        assert self.state_type is not None, f'{self.__class__.__qualname__}: Missing `state_type`'
        if vspec is None:
            variable = self.state_type()
        elif isinstance(vspec, validation.VSpec):
            assert issubclass(self.state_type, tkmilan_var.Spec), f'{self.__class__.__qualname__}: Invalid `state_type`, not a `Spec`'
            variable = self.state_type(vspec)
        else:
            assert isinstance(vspec, tkmilan_var.Variable)
            variable = vspec
        assert isinstance(variable, self.state_type), f'Incompatible variable type: {type(variable).__qualname__} not {self.state_type.__qualname__}'
        return variable

    def setup_state(self):
        return self.variable

    def wimage(self, key: str) -> typing.Optional[tk.Image]:
        '''Wraper for `RootWindow.wimage`.'''
        return self.wroot.wimage(key)


class ProxyWidget(SingleWidget):
    '''Parent class of all proxy widgets. Special case of `SingleWidget`.

    This is implemented as a class initializer that sets up the `wproxy
    <MixinWidget.wproxy>`/`proxee <MixinWidget.proxee>` references, and returns
    the child instance.

    Note that creating an instance of this type will return the child widget
    instance, not the proxy object. The rest of the library is aware of this.
    The `ProxyWidget` object is available on the `wproxy <MixinWidget.wproxy>`
    value.

    See Also:
        Check the Python documentation for the difference between
        `object.__new__` and `object.__init__`.
    '''
    def __new__(cls: typing.Type[ProxyWidgetT], *args, **kwargs) -> ProxyWidgetT:
        assert issubclass(cls, ProxyWidget)
        proxy = super(ProxyWidget, cls).__new__(cls)
        # Manually call the __init__ method (required since the class changes)
        cls.__init__(proxy, *args, **kwargs)
        proxee = proxy.proxee
        assert proxee is not None
        # Save a reference to the proxy object
        proxee.wproxy = proxy
        # Return a different type from `cls`:
        return typing.cast(ProxyWidgetT, proxee)


class ContainerWidget(MixinWidget, MixinStateContainer, MixinTraces):
    '''Parent class of all containers.'''
    layout: typing.Optional[str] = ''  # Automatic AUTO
    layout_expand: bool = True
    '''Should this container expand to fill the space on the parent widget.

    Note this affects the **parent** grid, not the child grid on this container.
    '''
    layout_autogrow: bool = True
    '''Should this container have its child columns and rows grow automatically.

    This is equivalent to configuring the grid with the option ``weight=1``.
    '''
    variable: typing.Optional[tkmilan_var.aggregator] = None

    def init_container(self, *args,
                       layout: typing.Optional[str] = '',
                       **kwargs) -> None:
        '''
        Setup all the container stuff.

        Includes:
        - Variable settings
        - Sub-Widget settings
        - Layout
        - Traces (from `MixinTraces`)
        - Defaults
        '''
        assert isinstance(self, (tk.Widget, tk.Tk)), f'{self} is not a valid tkinter.Widget'
        MixinWidget.__init__(self)
        self._variables: typing.MutableMapping[str, tk.Variable] = {}  # Allow attaching variables to containers
        # Calculate child widgets
        _existing_names = set(dir(self))
        _existing_ids = None
        if __debug__:
            _existing_ids = {
                name: id(self.__dict__.get(name, None))
                for name in _existing_names
                if name not in WEIRD_WIDGET_NAME
            }
        widgets = self.setup_widgets(*args, **kwargs)
        widgets_gui = set()
        if __debug__:
            assert _existing_ids is not None
            overriden_names = [name for name, eid in _existing_ids.items() if id(self.__dict__.get(name, None)) != eid]
            assert len(overriden_names) == 0, f'{self}: Overriden Names: {" ".join(overriden_names)}'
        _new_names = set(dir(self)) - _existing_names
        if widgets is None:
            children = [w for _, w in self.children.items()]
            # logger.debug('tk C: %r', self.children)
            widgets = {}
            dir_names = {id(getattr(self, name, None)): name for name in _new_names}
            for widget_raw in children:
                assert isinstance(widget_raw, MixinWidget), f'{widget_raw} is not a valid tkmilan widget'
                widget = widget_raw.proxee or widget_raw  # Save the child widget
                # `isAuto`: See `MixinWidget.isAuto`
                if widget.isAuto is True:  # State and GUI
                    wid = id(widget)
                    assert wid in dir_names, f'{self}: Missing "{widget}"[{widget!r}]'
                    name = dir_names[wid]
                    widgets[name] = widget
                elif widget.isAuto is False:  # GUI
                    widgets_gui.add(widget)
                elif widget.isAuto is None:  # Nothing
                    pass
        # logger.debug('Widgets: %r', widgets)
        self.widgets: typing.Mapping[str, MixinWidget] = widgets
        self._widgetsGUI: typing.Set[MixinWidget] = widgets_gui
        for w in self.widgets.values():
            w.wparent = self
        if self.isNoneable is None:
            # Calculate isNoneable option: containers are always noneable
            self.isNoneable = True

        if layout is None or self.layout is None:
            # Allow for explicit `None` layouts
            chosen_layout = None
        elif layout != '':
            # Use the per-instance setting
            chosen_layout = layout
        elif self.layout != '':
            # Use the class setting
            chosen_layout = self.layout
        else:
            # Fallback
            chosen_layout = autolayout.AUTO
        self.layout_container(chosen_layout)
        # Traces (synthetic)
        self.variable = self.setup_variable(None)
        MixinTraces.init_traces(self)
        # Defaults
        self.setup_defaults()
        self.after_idle(lambda: self.setup_adefaults())  # No need for a `TimeoutIdle` here
        # Error Checking
        assert hasattr(self, 'grid'), f'{self!r} should have a grid method'
        if __debug__:
            aliases = set(self._variables.keys()).intersection(set(self.widgets.keys()))
            assert len(aliases) == 0, f'{self!r}: Aliased var/widgets: {" ".join(aliases)}'

    def setup_variable(self, variable: typing.Optional[tkmilan_var.Variable]) -> tkmilan_var.aggregator:
        assert variable is None  # Containers don't have much choice here
        return tkmilan_var.aggregator(cwidget=self)

    def setup_traces(self, trace_vupstream: typing.Optional[typing.Set[str]] = None) -> tkmilan_var.Variable:
        assert self.variable is not None, f'{self!r}: Missing variable'
        assert not self.variable.ready, f'{self}: Repeated setup for synthetic trace'
        if __debug__:
            logger_traces.debug('%s<%s>: Tracing Children ...', self.variable, self)
        tnames = []
        vid_upstream: typing.Set[str] = set()
        container_state = self.state_c(vid_upstream=vid_upstream)
        for wc in container_state.cwidgets.values():
            function_name = wc.trace(self.__trace_trigger, what=wc,
                                     trace_name=f'__:{self.variable}',
                                     trace_vupstream=container_state.vid_upstream)
            if __debug__:
                logger_traces.debug('%s<%s>:: %15s <%s> @ %s', self.variable, self, 'Container', wc, function_name)
            tnames.append(function_name)
        for whc in container_state.hcwidgets:
            function_name = whc.trace(self.__trace_trigger, what=whc,
                                      trace_name=f'__:{self.variable}',
                                      trace_vupstream=container_state.vid_upstream)
            if __debug__:
                logger_traces.debug('%s<%s>:: %15s <%s> @ %s', self.variable, self, 'Helper Container', whc, function_name)
            tnames.append(function_name)
        for ws in container_state.swidgets.values():
            if isinstance(ws.variable, tkmilan_var.nothing):
                if __debug__:
                    logger_traces.debug('%s<%s>:: SKIP %15s <%s>', self.variable, self, 'Single', ws)
            else:
                function_name = ws.trace(self.__trace_trigger, what=ws,
                                         trace_name=f'__:{self.variable}')
                if __debug__:
                    logger_traces.debug('%s<%s>:: %15s <%s> @ %s', self.variable, self, 'Single', ws, function_name)
                tnames.append(function_name)
        for whs in container_state.hswidgets:
            if isinstance(whs.variable, tkmilan_var.nothing) or whs.ignoreContainerState:
                if __debug__:
                    logger_traces.debug('%s<%s>:: SKIP %15s <%s>', self.variable, self, 'Helper Single', whs)
            else:
                function_name = whs.trace(self.__trace_trigger, what=whs,
                                          trace_name=f'__:{self.variable}')
                if __debug__:
                    logger_traces.debug('%s<%s>:: %15s <%s> @ %s', self.variable, self, 'Helper Single', whs, function_name)
                tnames.append(function_name)
        for wvar in container_state.variables.values():
            if isinstance(wvar, tkmilan_var.nothing):
                if __debug__:
                    logger_traces.debug('%s<%s>:: SKIP %15s <%s>', self.variable, self, 'Var', wvar)
            else:
                function_name = tkmilan_var.trace(wvar, self.__trace_trigger)
                if __debug__:
                    logger_traces.debug('%s<%s>:: %15s <%s> @ %s', self.variable, self, 'Var', wvar, function_name)
                tnames.append(function_name)
        if __debug__:
            logger_traces.debug('%s<%s>: Traced %d Children!', self.variable, self, len(tnames))

        self.variable.tout = model.TimeoutIdle(self, self.variable.set,
                                               immediate=False)
        assert self.variable.ready, f'{self}: Error on setup for synthetic trace'
        if __debug__:
            logger_traces.debug('%s<%s>: TO: %s', self.variable, self, self.variable.tout)
        return self.variable

    def __trace_trigger(self, var, etype, *, what: typing.Optional[MixinWidget] = None):
        assert self.variable is not None, f'{self!r}: Missing variable'
        assert self.variable.ready and self.variable.tout is not None, f'{self}: Unprepared synthetic trace'
        self.variable.tout.reschedule()
        if __debug__:
            what_str = '' if what is None else f' « {what}'
            logger_traces.debug('%s « %s: Trigger @ %s%s',
                                self.variable, var,
                                self, what_str)

    def trace(self, *args,
              trace_vupstream: typing.Optional[typing.Set[str]] = None,
              **kwargs: typing.Any) -> str:
        assert self.variable is not None, f'{self!r}: Missing variable'
        if __debug__:
            # Do not warn about internal traces, even if the problem persists
            if self.variable.ready and not kwargs.get('trace_name', '').startswith('__'):
                # TODO: Need one container variable per trace, `trace_vupstream` might be different
                warnings.warn('Multiple Nested Container Traces, this might not work correctly', stacklevel=2)
                # Works fine for straight widget trees, but fails for complex states
        if not self.variable.ready:
            self.setup_traces(trace_vupstream)
        return super().trace(*args, **kwargs)

    def setup_gstate_valid(self, *,
                           nowarn: bool = False,
                           childMatch: typing.Iterable[SingleWidget] = tuple(),
                           childSkip: typing.Iterable[SingleWidget] = tuple(),
                           ) -> None:
        '''Configure setting the `model.GuiState` ``valid`` parameter for this
        GUI.

        Since this is still a "hack", it's not enabled automatically nor in a
        nice declarative way. This might interact with other features, it is
        only a preview for now.

        This is not recursive, child containers **DO NOT** inherit this
        setting. There's no support for child containers anyway, make sure to
        use this only for simple containers, no nesting.

        To setup this, call this function inside the widgets' `setup_defaults`
        function, before other widget state changes. This uses `trace`
        internally, so that's another feature that might not work perfectly.

        Use the ``nowarn`` parameter if you confirmed it works properly, to
        avoid a spurious warning. This is not the default, make sure you really
        test this properly.

        Use the ``childMatch`` parameter to "tie" the container valid state to
        those child single widgets. This should include any child labels, that
        should be ignored when calculating the new state, but set with the
        container state. ``childSkip`` will avoid setting the state on those
        widgets.

        .. warning::
            This is not fully baked, but can be used carefully, with extra
            testing.
        '''
        if __debug__:
            if not nowarn:
                warnings.warn('HACK: This is not fully supported on complex containers', stacklevel=2)
        self.trace(self.__valid_trigger, childMatch=set(childMatch), childSkip=set(childSkip),
                   trace_name='__:gstate:valid', trace_initial=True)

    def __valid_trigger(self, var, etype, *,
                        childMatch: typing.Set[SingleWidget],
                        childSkip: typing.Set[SingleWidget]):
        # See `setup_gstate_valid`
        assert all(w.gstate.valid is not None for w in self.widgets.values() if w not in childMatch)
        assert all(w not in childMatch for w in childSkip), f'{self}: Confusing Match/Skip orders'
        assert all(w.wparent == self for w in (*childMatch, *childSkip)), f'{self}: Non-Children widgets given in "child*"'
        vstate = all(w.gstate.valid for w in self.widgets.values() if w not in childMatch)
        # Container Widget (no recursion)
        self.set_gui_state(valid=vstate, _sub=False)
        # Child Widgets
        for w in childMatch - childSkip:
            assert isinstance(w, SingleWidget)
            w.set_gui_state(valid=vstate)
        return vstate

    def setup_widgets(self, *args, **kwargs) -> typing.Optional[typing.Mapping[str, MixinWidget]]:
        '''Define the sub widgets here.

        Return a :py:class:`dict` for a custom mapping, or `None` for automatic mapping.
        '''
        raise NotImplementedError

    def var(self, cls: typing.Type[tkmilan_var.Variable], *,
            value: typing.Optional[typing.Any] = None,
            name: typing.Optional[str] = None,
            ) -> 'tkmilan_var.Variable':
        '''"Attach" a new variable to this container.

        Args:
            cls: The variable class.

            name: The variable name. Optional, defaults to an autogenerated name.
            value: The default value. Optional, defaults to `None`.

        See Also:
            - `varSpec`: Attach a `Spec` variable to this container, with a name.
            - `gvar`: Access the variable by name.
        '''
        vobj = cls(name=name)
        if value is not None:
            vobj.set(value)
        assert isinstance(vobj, tkmilan_var.Variable), f'Class "{cls}" is not a "Variable"'
        # Save the variables on the instance object
        vname = name or str(vobj)
        self._variables[vname] = vobj
        return vobj

    def varSpec(self, cls: typing.Type[tkmilan_var.Spec], spec: typing.Any, *,
                name: typing.Optional[str] = None,
                ) -> 'tkmilan_var.Spec':
        '''"Attach" a new `specified variable <var.Spec>` to this container.

        Args:
            cls: The variable class.
            name: The variable name. Optional, defaults to an autogenerated name.

            All other arguments are passed to the class constructor.

        See Also:
            - `var`: Attach a non-`Spec` variable to this container, with a name.
            - `gvar`: Access the variable by name.
        '''
        if __debug__:
            if cls in tkmilan_var.Limit.__subclasses__():
                warnings.warn('No need to use `var.Limit` subclasses, use the parent class', stacklevel=2)
        vobj = cls(spec, name=name)
        assert isinstance(vobj, tkmilan_var.Spec), f'Class "{cls}" is not a "Spec"'
        # Save the variables on the instance object
        vname = name or str(vobj)
        self._variables[vname] = vobj
        return vobj

    def gvar(self, name: str) -> tkmilan_var.Variable:
        '''Get a variable attached to this container, by name.

        Fails if it does not exist.

        Args:
            name: The variable name to search for.

        See Also:
            - `var`: Attach a non-`Spec` variable to this container, with a name.
            - `varSpec`: Attach a `Spec` variable to this container, with a name.
        '''
        return self._variables[name]

    def layout_container(self, layout: typing.Optional[str]):
        assert isinstance(self, (tk.Widget, tk.Tk)), f'{self} is not a valid tkinter.Widget'
        if self.layout_expand:
            assert isinstance(self, tk.ttk.Widget), f'{self} is not a valid tkinter.ttk.Widget'
            self.grid(sticky=tk.NSEW)
        # Automatic Layout
        layout, args = autolayout.do(layout, len(self.widgets))
        if layout:
            # if __debug__:
            #     logger.debug(f'{self}: => {len(self.widgets)} widgets')
            for idx, (arg, widget) in enumerate(zip(args, self.widgets.values())):
                widget_real = widget.wproxy or widget
                assert isinstance(widget_real, tk.Widget)
                widget_real.grid(**arg.dict())  # Change the grid on the proxy widget
        self.layout = layout  # Setup the final layout setting
        if self.layout_autogrow:
            if size := self.gsize:
                fn.configure_grid(self, [1] * size.columns, [1] * size.rows)
        self.setup_layout(layout)  # Custom adjustments, after all automatic changes

    @property
    def gsize(self) -> model.GridSize:
        '''GUI grid size (according to the current child widgets).'''
        return fn.grid_size(*[w.wproxy or w for w in self.widgets.values()])  # Use the proxy widget

    def state_c(self, *, vid_upstream: typing.Optional[typing.Set[str]] = None) -> ContainerState:
        swidgets = {}
        cwidgets = {}
        hswidgets: 'typing.Set[SingleWidget]' = set()
        hcwidgets: 'typing.Set[ContainerWidget]' = set()
        wvariables = {}
        vid_upstream = set(vid_upstream or ())
        vid_variables = set(fn.vname(v) for v in self._variables.values())
        vwidgets = collections.defaultdict(list)
        # logger.debug('%r START | %r', self, vid_upstream)
        for name, widget in self.widgets.items():
            # logger.debug('%s: %r', name, widget)
            if widget.ignoreContainerState:
                # logger.debug('| Skipping Widget')
                continue
            if isinstance(widget, SingleWidget):
                assert widget.variable is not None
                vid = fn.vname(widget.variable)
                # logger.debug('| Variable: %s[%r]', vid, widget.variable)
                if vid in vid_upstream:
                    # logger.debug('  @Upstream, skipping')
                    continue
                elif vid in vid_variables:
                    # logger.debug('  @Container Variables, skipping')
                    continue
                else:
                    swidgets[name] = widget
                    wvariables[vid] = widget.variable
                    vwidgets[vid].append(name)
            elif isinstance(widget, ContainerWidget):
                # logger.debug('| Container: @%s', name)
                cwidgets[name] = widget
            else:
                raise NotImplementedError(f'Unknown Widget Type: {widget}')
        state_widgets = set((*swidgets.values(), *cwidgets.values()))
        assert isinstance(self, (tk.Widget, tk.Tk)), f'{self} is not a valid widget'
        for name, cwidget in self.children.items():
            if cwidget in state_widgets:
                continue
            if isinstance(cwidget, SingleWidget):
                # logger.debug('| Helper Single: %s', name)
                assert cwidget.variable is not None
                vid = fn.vname(cwidget.variable)
                if vid in vid_upstream:
                    # logger.debug('  @Upstream, skipping')
                    continue
                elif vid in vid_variables:
                    # logger.debug('  @Container Variables, skipping')
                    continue
                elif cwidget.wproxy is not None:
                    # logger.debug('  @Proxy Widget, skipping')
                    continue
                else:
                    hswidgets.add(cwidget)
            elif isinstance(cwidget, ContainerWidget):
                # logger.debug('| Helper Container: %s', name)
                hcwidgets.add(cwidget)
            else:
                raise NotImplementedError(f'Unknown Widget Type: {cwidget}')
        vid_upstream.update(wvariables, vid_variables)
        # logger.debug('%r STOP', self)
        return ContainerState(swidgets, cwidgets,
                              variables=self._variables,
                              wvariables=wvariables,
                              vwidgets=dict(vwidgets),
                              vid_upstream=vid_upstream,
                              # Helper Widgets
                              hswidgets=hswidgets, hcwidgets=hcwidgets,
                              )

    def setup_state(self, **kwargs) -> typing.Mapping[str, model.WidgetDynamicState]:
        # Default State:
        # - All the attached variables
        # - All the shared variables
        # - All the single-variable widgets
        # - The container widgets, taking the existing variables into account
        container_state = self.state_c(**kwargs)
        rvalue: typing.MutableMapping[str, model.WidgetDynamicState] = {}
        wids_done: typing.MutableSequence[str] = []
        for vn, vobj in container_state.variables.items():
            rvalue[vn] = model.WidgetDynamicState(vobj.get, vobj.set, noneable=False)
        for vname, ws in container_state.vwidgets.items():
            if vname is not None and len(ws) > 1:
                wv = container_state.wvariables[vname]
                assert vname not in rvalue, f'{self!r}: Aliased vwidgets "{vname}"'
                rvalue[vname] = model.WidgetDynamicState(wv.get, wv.set, noneable=False)
                wids_done.extend(ws)
        for n, w in container_state.swidgets.items():
            if n not in wids_done:
                assert n not in rvalue, f'{self!r}: Aliased swidgets "{n}"'
                rvalue[n] = model.WidgetDynamicState(
                    w.wstate_get,
                    w.wstate_set,
                    noneable=w.isNoneable is True,
                )
        vid_upstream = container_state.vid_upstream
        for n, wc in container_state.cwidgets.items():
            assert n not in rvalue, f'{self!r}: Aliased cwidgets "{n}"'
            rvalue[n] = model.WidgetDynamicState(
                partial(wc.state_get, vid_upstream=vid_upstream),
                partial(wc.state_set, vid_upstream=vid_upstream),
                noneable=wc.isNoneable is True,
                container=True,  # Propagate container data
            )
        return rvalue

    def setup_layout(self, layout: typing.Optional[str]) -> None:
        '''Useful for manual adjustments to the automatic layout.

        This runs after all automatic layout settings are configured.

        Args:
            layout: This is the string passed to the upstream function.

        Note:
            Available for subclass redefinition.
        '''
        pass

    def set_gui_state(self, state: typing.Optional[model.GuiState] = None, _sub: bool = True, **kwargs) -> model.GuiState:
        '''Set GUI State for itself, and optionally, for all sub-widgets.

        .. warning:: Don't use this directly, unless you **really** know what you are doing.

        Args:
            _sub: Automatically run `set_gui_substate` with the same
                `model.GuiState` object. Defaults to `True`.
                Useful only for implementing special containers.

        See Also:
            `MixinWidget.gstate`: Property changed for all sub-widgets.
        '''
        self_state = super().set_gui_state(state, **kwargs)
        if _sub:
            self.set_gui_substate(self_state)
        return self_state

    def set_gui_substate(self, state: model.GuiState) -> None:
        '''Set GUI State for all sub-widgets.

        .. warning:: Don't use this directly, unless you **really** know what you are doing.


        .. note::

            To control the GUI subwidget handling, this function can be
            redefined (using extra care), using something like this:

            .. code:: python

                def set_gui_substate(self, state: tkmilan.model.GuiState):
                    if self.some_condition is True:
                        # Manipulate the `model.GuiState` object
                        state.enabled = False
                    super().set_gui_substate(state)

        See Also:
            `MixinWidget.gstate`: Property changed for all sub-widgets.
        '''
        for _, subwidget in self.widgets.items():
            subwidget.gstate = state
        for subwidget in self._widgetsGUI:
            subwidget.gstate = state

    def setup_defaults(self) -> None:
        '''Runs after the widget is completely setup.

        Note this runs before the parent widget is complete ready.

        Useful to set default values.
        Do not configure layout-related settings here, see `setup_layout
        <ContainerWidget.setup_layout>`.

        Note:
            Available for subclass redefinition.

        See Also:
            `setup_adefaults <ContainerWidget.setup_adefaults>`: Run code after
            all widgets are stable (including parent widgets in the tree).
        '''
        pass

    def setup_adefaults(self) -> None:
        '''Runs after all widgets are stable.

        Avoid changing state on this function.

        Note:
            Available for subclass redefinition.

        See Also:
            `setup_defaults <ContainerWidget.setup_defaults>`: Run code right after this widget is setup, before
            all widgets are stable.
        '''
        pass

    def wimage(self, key: str) -> typing.Optional[tk.Image]:
        '''Wraper for `RootWindow.wimage`.'''
        return self.wroot.wimage(key)

    def pgrid(self, *children: MixinWidget,
              row: bool = True, column: bool = True,
              **arguments: typing.Mapping[str, typing.Any]) -> None:
        '''Configure the grid rows and columns for the given widgets.

        For widgets that span more than one row or column, the settings are changed
        for all rows or columns.

        Args:
            children: Widgets to consider.
                Must all be direct children of this widget.
            row: Configure the rows. Defaults to `True`.
            column: Configure the columns. Defaults to `True`.
            arguments: Arguments passed to the configuration functions:
                `columnconfigure <https://www.tcl.tk/man/tcl/TkCmd/grid.html#M8>`_
                /
                `rowconfigure <https://www.tcl.tk/man/tcl/TkCmd/grid.html#M24>`_.

        .. note::

            To configure only rows or columns, see `pgrid_r` and `pgrid_c` for
            a more ergonomic API.
        '''
        assert row or column, 'Do something, select at least one of row and column'
        assert len(arguments), 'Do something, include some arguments'
        rows: typing.Set[int] = set()
        columns: typing.Set[int] = set()
        for w in children:
            assert w.wparent is self, f'{self}: Not a direct child: {w}'
            wgrid = w.wgrid
            if wgrid is not None:
                rows.update(wgrid.rows())
                columns.update(wgrid.columns())
        assert len(rows) > 0 or len(columns) > 0, f'{self}: Invalid children: {children}'
        if __debug__:
            logger_grid.debug('%s: [%sx%s]: %s', self,
                              ' '.join(str(n) for n in rows) if row else '',
                              ' '.join(str(n) for n in columns) if column else '',
                              ' '.join(f'{k}={v!r}' for k, v in arguments.items()),
                              )
        assert isinstance(self, (tk.Widget, tk.Tk)), f'{self} is not a valid tkinter.Widget'
        if row:
            self.rowconfigure(tuple(rows), **arguments)  # type: ignore  # Invalid Types
        if column:
            self.columnconfigure(tuple(columns), **arguments)  # type: ignore  # Invalid Types

    def pgrid_r(self, *children: MixinWidget,
                **arguments: typing.Mapping[str, typing.Any]):
        '''Wraps `pgrid`, acting only on rows.

        See `pgrid`, sets only ``row`` to `True`.
        '''
        return self.pgrid(*children,
                          row=True, column=False,
                          **arguments)

    def pgrid_c(self, *children: MixinWidget,
                **arguments: typing.Mapping[str, typing.Any]):
        '''Wraps `pgrid`, acting only on columns.

        See `pgrid`, sets only ``column`` to `True`.
        '''
        return self.pgrid(*children,
                          row=False, column=True,
                          **arguments)

    def widgets_class(self, *classes: typing.Type[MixinWidget]) -> typing.Iterable[MixinWidget]:
        '''Filter widgets by type.

        Filter all child widgets by type. Very useful to apply settings to a
        subset of all child widgets.

        Arguments:
            classes: Widget Types, as classes.
        '''
        class_tuple = tuple(classes)
        for w in self.widgets.values():
            if isinstance(w, class_tuple):
                yield w
