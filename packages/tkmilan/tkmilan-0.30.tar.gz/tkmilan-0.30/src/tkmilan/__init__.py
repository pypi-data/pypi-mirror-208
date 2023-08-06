#!/usr/bin/env python
"""
`tkinter`'s evil twin.
"""
import sys
import typing
from importlib.metadata import version as metadata_version, PackageNotFoundError
import logging
import warnings
from contextlib import contextmanager
from functools import wraps, lru_cache
from dataclasses import dataclass
from pathlib import Path

import tkinter as tk
import tkinter.font
from tkinter import ttk
import tkinter.simpledialog  # Implemented in newer typeshed versions

from . import autolayout
from . import model
from . import var
from . import validation
from . import mixin
from . import exception
from . import parser
from . import fn


MODULES_VERBOSE = (
    'autolayout',
    'model.layout',
    'mixin.traces', 'mixin.valid', 'mixin.grid',
)
'''Shows spammy modules, should be silenced by the calling application.

These sub-modules sent enormous amount of logs, bordering on spam, on the
``logging.DEBUG`` setting.

The calling application should use something like this to silence them:

.. code:: python

    if loglevel == logging.DEBUG:
        for dmodule in MODULES_VERBOSE:
            logging.getLogger(f'tkmilan.{dmodule}').setLevel(logging.INFO)
'''

# Store the project version number
__version__: typing.Optional[str]
__version_numeric__: typing.Tuple[int, ...]
try:
    # The "project" name is the same as the package
    __version__ = metadata_version(__package__)
    __version_numeric__ = tuple(int(n) for n in __version__.split('.')[:2])
except PackageNotFoundError:
    __version__ = None
    __version_numeric__ = (-1,)


# TypeChecking
class varTree(var.ObjectList[model.TreeElement]):
    '''Type-Checking variable type for `Tree`.'''
    pass


# Useful models
Binding = model.Binding

# Layouts
# TODO: Transform into a `enum.Enum`?
AUTO = autolayout.AUTO
'''Automatic Layout.
'''
HORIZONTAL = autolayout.HORIZONTAL
'''Horizontal (1 row) Layout.
'''
VERTICAL = autolayout.VERTICAL
'''Vertical (1 column) Layout.
'''

logger = logging.getLogger(__name__)


# Usable Widgets

# # Containers


class RootWindow(tk.Tk, mixin.ContainerWidget):
    '''A root window, the toplevel widget for the entire application.

    Usually there's only one of this in a single application. Multiple root
    windows are unsupported.

    The `setup_images` function can be overriden to load any number of images
    in any way. The common usage of loading all images in a folder is supported
    directly with ``imgfolder``.

    On debug mode, this will sanity check the entire GUI, by reading its state.
    This doesn't happen in production.

    See `tkinter.Tk`.

    Args:
        theme: Theme to use. Default to choosing a tasteful choice depending on
            the OS.
        imgfolder: Folder with images to be loaded (see `setup_images_folder`). Optional.
        cls: Window Class Name. Defaults to ``"tkinter"``, the project name, so
            that it can be distiguished from the upstream default, ``"Tk"``.

    Note:
        Technically, it should be OK to use multiple root windows per-process,
        but this hasn't been tested, there are no test cases where this makes
        sense.
    '''
    isNoneable: bool = False  # Always present, no matter what
    styleIDs: typing.Optional[typing.Mapping[str, typing.Mapping[str, typing.Union[str, model.DStyle]]]] = None
    '''Configure `tkinter.ttk.Style` for registered "styleID".

    See Also:
        Register styleID using `register_styleID` function. This function is
        defined on the root window, use `MixinWidget.wroot` to reach it from
        any widget.
    '''
    layout_expand = False  # Hardcode, `tk.Tk`/`Toplevel` has no parent grid to expand

    @dataclass
    class Style(model.WStyle):
        '''`RootWindow` style object.

        These are the settings:

        Args:
            tool_window: When enabled, marks the window as a tool window, not a
                regular window. The precise meaning of this setting depends on the
                OS.
            toplevel: When enabled, shows the window above all other windows.

        Note:
            To control window fullscreen state, see `rgstate`.
        '''
        # These attributes should remain forever, it doesn't make sense to
        # change them at runtime. Not to be confused with `WindowState` for
        # dynamic state.
        tool_window: bool = False
        toplevel: bool = False

    def __init__(self, *args,
                 theme: typing.Optional[str] = None,
                 imgfolder: typing.Optional[Path] = None,
                 cls: str = 'tkmilan',
                 style: Style = Style(_default=True),
                 **kwargs):
        self.wstyle = style
        self._bindings_global: typing.MutableMapping[str, model.BindingGlobal] = {}
        self.images_cache: typing.MutableMapping[str, model.ImageCache] = {}
        self._styleIDs: typing.MutableSet[str] = set()
        self._styleComplex: typing.MutableMapping[str, typing.Tuple[str, ...]] = {}
        super().__init__(baseName=None, className=cls)  # tk.Tk
        self.setup_images(imgfolder)  # Register all images before the child widgets are setup
        self.init_container(*args, **kwargs)
        self.style = self.setup_style(theme)
        self.after_idle(self.setup_styleID)  # No need for a `TimeoutIdle` here
        # Set window style attributes. See
        # - https://wiki.tcl-lang.org/page/wm+attributes
        if self.wstyle.tool_window:
            if sys.platform == 'win32':
                self.wm_attributes('-toolwindow', True)
            elif sys.platform.startswith('linux'):
                self.wm_attributes('-type', 'dialog')
            else:
                if __debug__:
                    raise ValueError(f'Unsupported Tool Window OS: "{sys.platform}"')
        if self.wstyle.toplevel:
            self.wm_attributes('-topmost', True)
        if __debug__:
            import traceback

            def sanity_check():
                logger.debug('=> Sanity Check GUI State')
                try:
                    self.wstate_get()
                except Exception:
                    traceback.print_exc()
                    sys.exit(100)
            self.after_idle(sanity_check)

    def setup_style(self, theme: typing.Optional[str]) -> ttk.Style:
        style = ttk.Style(self)
        if theme is None:
            if sys.platform == 'win32':
                # On Windows, check: 'winnative', 'vista'
                theme = 'vista'
            elif sys.platform.startswith('linux'):
                # Good for Linux
                theme = 'alt'
        if theme is not None:
            if __debug__:
                all_themes = style.theme_names()
                # logger.debug('Available Themes: %s', ' '.join(all_themes))
                assert theme in all_themes, f'Invalid Theme: {theme}'
            style.theme_use(theme)
        # Calculate Dynamic Styles
        map_root_fg = dict(style.map('.', 'foreground'))
        assert 'disabled' in map_root_fg
        lookup_root_font = style.lookup('.', 'font')
        lookup_root_selectbg = style.lookup('.', 'selectbackground')
        assert None not in [lookup_root_font, lookup_root_selectbg]
        self.styleDynamic: typing.Mapping[model.DStyle, str] = {
            model.DStyle.Color_FG_Disabled: map_root_fg['disabled'],
            model.DStyle.Font_Default: lookup_root_font,
            model.DStyle.Color_BG_Selected: lookup_root_selectbg,
        }
        assert len(self.styleDynamic) == len(model.DStyle), 'Missing Dynamic Style Definitions'
        # if __debug__:
        #     logger.debug('Style Static')
        #     for i, value in model.SStyle.items():
        #         logger.debug('- %s: %s', i, value)
        #     logger.debug('Style Dynamic')
        #     for i, string in self.styleDynamic.items():
        #         logger.debug('- %s: %s', i, string)
        return style

    def setup_styleID(self) -> None:
        widget_sids = self._styleIDs
        wcomplex_sids = self._styleComplex
        self_sids = typing.cast(typing.MutableMapping[str, typing.Mapping[str, typing.Union[str, model.DStyle]]], self.styleIDs or {})
        cfg_sids = set(self_sids.keys())
        if __debug__:
            logger.debug('Set styleID Settings: CFG#%d Widgets#%d WComplex#%d', len(self_sids), len(widget_sids), len(wcomplex_sids))
        if __debug__:
            if not (widget_sids <= cfg_sids):
                logger.critical('Missing styleID configuration for "%s"', " ".join(widget_sids - cfg_sids))
                sys.exit(100)
        for csid, ssids in wcomplex_sids.items():
            if csid in self_sids:
                logger.warning('| %s: Existing settings', csid)
            else:
                sid_options: typing.MutableMapping[str, typing.Union[str, model.DStyle]] = {}
                if __debug__:
                    logger.debug('| %s: %s', csid, ' '.join(ssids))
                for sid in ssids:
                    sid_simple_options = self_sids.get(sid, {})
                    if __debug__:
                        sid_simple_repetitions = set(sid_simple_options).intersection(set(sid_options))
                        if len(sid_simple_repetitions) > 0:
                            logger.critical('Alias on complex styleID "%s": Aliased "%s"', csid, " ".join(sid_simple_repetitions))
                            sys.exit(100)
                    sid_options.update(sid_simple_options)
                self_sids[csid] = sid_options
        for sid, style_rawoptions in self_sids.items():
            style_options: typing.MutableMapping[str, str] = {}
            if __debug__:
                style_showoptions = {}
            for sopt, svalue in style_rawoptions.items():
                srealvalue: str
                sshowvalue: str
                if svalue in self.styleDynamic:
                    assert isinstance(svalue, model.DStyle)
                    srealvalue = self.styleDynamic[svalue]
                    if __debug__:
                        sshowvalue = f'$({svalue.name}={srealvalue})'
                else:
                    assert isinstance(svalue, str)
                    srealvalue = svalue
                    if __debug__:
                        sshowvalue = svalue
                style_options[sopt] = srealvalue
                if __debug__:
                    style_showoptions[sopt] = sshowvalue
            if __debug__:
                logger.debug('- %s: %s', sid, ' '.join('='.join((sopt, svalue)) for sopt, svalue in style_showoptions.items()))
            self.style.configure(sid, **style_options)

    def setup_images(self, imgfolder: typing.Optional[Path]):
        '''Register all images here.

        This is called before the child widgets are defined.

        Lazy loads all images on production, see `__debug__`.

        Args:
            imgfolder: Folder with images to be loaded (using `setup_images_folder`). Optional.
        '''
        if imgfolder:
            self.setup_images_folder(imgfolder, lazy=not __debug__)

    @lru_cache
    def wimage(self, key: str) -> typing.Optional[tk.Image]:
        '''Get image data by key.

        This function will cache the image object, so no extra Python
        references are needed. The cache will store all used image, avoid
        runaway memory consumption by using enormous amounts of images.

        See Python documentation for `images <https://docs.python.org/3/library/tkinter.html#images>`_.

        Args:
            key: The key to find the image data.

        Returns:
            If the key exists, return the ``tkinter.Image`` object, otherwise
            return `None`.
        '''
        iobj = self.images_cache.get(key)
        if iobj is None:
            if __debug__:
                warnings.warn(f'Missing image: {key}', stacklevel=2)
            return None
        else:
            if not iobj.cached:
                img_function = tk.PhotoImage  # Default Function
                img_kwargs: typing.Dict[str, typing.Any] = {}
                if iobj.dtype and iobj.dtype in model.IMAGE_TYPES:
                    img_function = model.IMAGE_TYPES[iobj.dtype]
                    img_kwargs['format'] = iobj.dtype
                # Load the image
                if iobj.fname:
                    if __debug__:
                        logger.debug(f'Load Image "{key}" from file "{iobj.fname}"')
                    iobj.obj = img_function(file=iobj.fname, **img_kwargs)
                elif iobj.data:
                    if __debug__:
                        logger.debug(f'Load Image "{key}" from data')
                    iobj.obj = img_function(data=iobj.data, **img_kwargs)
                    # TODO: Remove the data copy: `iobj.data = None`
                else:
                    raise ValueError(f'Invalid Cache Metadata for Image {key}')
            return iobj.obj

    def instate(self, statespec: typing.Sequence[str], callback: typing.Optional[typing.Callable] = None) -> typing.Optional[bool]:
        ''''''  # Do not document
        # Not applicable to the root window
        return None

    def state(self, statespec):
        ''''''  # Do not document
        # Not applicable to root window
        raise NotImplementedError

    def get_gui_windowstate(self) -> model.WindowState:
        return model.WindowState(
            fullscreen=bool(self.wm_attributes('-fullscreen') == 1)
        )

    def set_gui_windowstate(self, rgstate: model.WindowState) -> None:
        if rgstate.fullscreen is not None:
            self.wm_attributes('-fullscreen', 1 if rgstate.fullscreen is True else 0)

    rgstate = property(get_gui_windowstate, set_gui_windowstate)
    '''Window State

    See `WindowState`.
    '''

    def gbinding(self, *args, immediate: bool = True, **kwargs) -> model.BindingGlobal:
        '''Create a `model.BindingGlobal` for this application.

        Args:
            immediate: Passed to the upstream object, default to enabling the
                binding on creation. This is the opposite from upstream.

        All arguments are passed to the `model.BindingGlobal` object.
        '''
        return model.BindingGlobal(self, *args, immediate=immediate, **kwargs)

    def register_styleID(self, argument: typing.Optional[str], thisClass: str) -> str:
        '''Register a styleID, based on an argument, and the current widget
        style class name.

        The styleID can represent a combination os simpler styles, by using
        ``|`` to separate the corresponding keys.

        Called by each widget type, it must define "thisClass" as mentioned in
        ``Tk`` documentation, a different string for each widget type.

        See Python docs in :external:ref:`TtkStyling`, see ``Tk`` `style
        <https://www.tcl.tk/man/tcl/TkCmd/ttk_style.html>`_ documentation.

        Args:
            argument: The styleID subclasses, separated by ``|``.
                This is defined by the final GUI designer. Optional.
            thisClass: The class for the current widget.

        Returns:
            An empty string indicates no style is applied, see ``Tk``
            `widget style argument
            <https://www.tcl.tk/man/tcl/TkCmd/ttk_widget.html#M-style>`_
            documentation.
        '''
        # TODO: Turn `argument` type into a string or string tuple: `typing.Optional[typing.Union[str, typing.Tuple[str, ...]]]`
        # TODO: Support validating the style options in `setup_styleID`
        styleID = ''  # Equivalent to `None`, no styling is applied
        if argument is not None:
            theseID = set()
            for subclass in argument.split('|'):
                assert '.' not in subclass, f'Invalid StyleID: "{subclass}"'
                styleSubID = f'{subclass}.{thisClass}'
                theseID.add(styleSubID)
            self._styleIDs |= theseID  # .update()
            styleID = f'{argument}.{thisClass}'
            if len(theseID) > 1:
                self._styleComplex[styleID] = tuple(theseID)
        return styleID

    def setup_image_data(self, key: str, data: bytes, dtype: str, *, cache_clear: bool = True, lazy: bool = True) -> None:
        '''Register a single image, from arbitrary data.

        This is useful to avoid external image files and hardcode all image
        data on the binary itself.

        The data can be given as a base64 byte string. This can be computed
        from a file ``$IMAGE`` using the following command

        .. code:: shell

            base64 --wrap=0 <"$IMAGE"

        By default, the image data itself is lazy loaded, that is, only read
        from the files as the images are requested, controlled by the ``lazy``
        parameter.

        Args:
            key: The key to store the image under
            data: The image data, as bytes.
            dtype: The image format. Only `tkinter` supported images.

            cache_clear: Clear the image cache after register these new image.
                Default to `True`.
            lazy: Lazy load image data, on demand as the image is requested.
                Default to `True`.

        See Also:
            - `setup_images_folder`: Register several images from a folder.
            - `wimage`: Get the loaded image data.
        '''
        if key in self.images_cache:
            raise exception.InvalidImageKey(key)
        if dtype not in model.IMAGE_TYPES:
            raise exception.InvalidImageType(dtype)
        if __debug__:
            logger.debug(f'Register {dtype.upper()} Image "{key}"')
        self.images_cache[key] = model.ImageCache(data=data, dtype=dtype)
        if cache_clear:
            self.wimage.cache_clear()
        if not lazy:
            self.wimage(key)

    # TODO: Accept multiple formats (`model.IMAGE_TYPES`), by that order (first wins)
    def setup_images_folder(self, folder: Path, *, cache_clear: bool = True, lazy: bool = True) -> None:
        '''Register all supported images from a folder.

        Registers all supported images on the given folder, does not recurse
        into subfolders. Unsupported file extensions are skipped.

        The key for finding the images is the file name, without the last
        extension. Multiple images with the same key and different extensions
        are unsupported.

        By default, the image data itself is lazy loaded, that is, only read
        from the files as the images are requested. This can be worked around
        by setting ``lazy`` to ``False``, to immediately load all the image
        data. This is mostly useful to detect errors as soon as possible,
        mostly for debug purposes.

        Args:
            folder: The source folder. Optional.
            cache_clear: Clear the image cache after register these new images.
                Default to `True`.
            lazy: Lazy load image data, on demand as the images are requested.
                Default to `True`.

        See Also:
            - `setup_image_data`: Register a single image from raw data.
            - `wimage`: Get the loaded image data.
        '''
        if not folder.is_dir():
            raise ValueError(f'Invalid Folder: {folder}')
        new_images: typing.Optional[typing.Set[str]] = None if lazy else set()
        for imgfile in folder.iterdir():
            imgext = imgfile.suffix
            dtype = None if imgext == '' else imgext[1:].lower()
            if imgfile.is_file() and dtype in model.IMAGE_TYPES:
                imgkey = imgfile.stem
                if __debug__:
                    logger.debug(f'Register {dtype.upper()} Image "{imgkey}": "{imgfile}"')
                if imgkey in self.images_cache:
                    raise exception.InvalidImageKey(imgkey)
                if dtype not in model.IMAGE_TYPES:
                    raise exception.InvalidImageType(dtype)
                self.images_cache[imgkey] = model.ImageCache(fname=imgfile, dtype=dtype)
                if new_images is not None:
                    new_images.add(imgkey)
        if cache_clear:
            self.wimage.cache_clear()
        if new_images is not None:
            logger.debug('Load %d Images', len(new_images))
            for image in new_images:
                self.wimage(image)


class FrameUnlabelled(ttk.Frame, mixin.ContainerWidget):
    '''A simple frame to hold other widgets, visually invisible.

    This is the simplest form of `mixin.ContainerWidget`, just a bunch of
    widgets. There's no separation between the outside and the inside of the
    frame.

    There is no Python documentation, see ``Tk`` `ttk.Frame <https://www.tcl.tk/man/tcl/TkCmd/ttk_frame.html>`_ documentation.

    Args:
        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.

    See Also:
        `FrameLabelled`: Visible version, with a label.
    '''
    def __init__(self, parent: mixin.ContainerWidget, *args,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, style=parent.wroot.register_styleID(styleID, 'TFrame'))  # ttk.Frame
        self.init_container(*args, **kwargs)


class FrameLabelled(ttk.LabelFrame, mixin.ContainerWidget):
    '''A frame to hold other widgets surrounded by a line, including a label.

    This is a frame with a label. It is visually separated from the other
    widgets. You can control the label position.

    There is no Python documentation, see ``Tk`` `ttk.LabelFrame <https://www.tcl.tk/man/tcl/TkCmd/ttk_labelframe.html>`_ documentation.

    Args:
        label: The label to include on the frame separator. Can be given as a class variable.
        labelAnchor: The position of the label on the frame separator.
            Given as one of the cardinal points.
            Defaults to a OS-specific location (`model.CP.default`).

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.

    See Also:
        `FrameUnlabelled`: Invisible version, without a label.

        `FrameStateful`: Support for an embedded `Checkbox` as label.
    '''
    label: typing.Optional[str] = None

    def __init__(self, parent: mixin.ContainerWidget, *args,
                 label: typing.Optional[str] = None,
                 labelAnchor: model.CP = model.CP.default,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        chosen_label = self.label or label
        if chosen_label is None:
            raise exception.InvalidWidgetDefinition('{self!r}: Missing required label')
        # TODO: Improve labelAnchor object
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, text=chosen_label, labelanchor=labelAnchor.value,
                         style=parent.wroot.register_styleID(styleID, 'TLabelframe'),  # Also: TLabelframe.Label
                         )  # ttk.LabelFrame
        if __debug__:
            if 'labelwidget' in kwargs:
                warnings.warn(f'{self}: Unsupported "labelwidget"', stacklevel=2)
        kwargs.pop('labelwidget', None)  # Unsupported
        self.init_container(*args, **kwargs)


# # Simple Widgets


class Label(ttk.Label, mixin.SingleWidget):
    '''A label, can be text, image, or both.

    This is a label, a static-ish widget without interaction.

    This must include at least some text or an image, even though both are optional.

    No state is included.

    There is no Python documentation, see ``Tk`` `ttk.Label <https://www.tcl.tk/man/tcl/TkCmd/ttk_label.html>`_ documentation.

    Args:
        label: The text to show. Optional. Can be given as a class variable.
        anchor: Align the text inside the widget. See below for how the default is calculated.
        justify: The text justification. See below for how the default is calculated.
        labelPosition: Label position, how to combine label and image.
            See `model.CP_Compound` for the possible values.
        image: The image to show. Optional.
            See ``Tk`` `tk.Image <https://www.tcl.tk/man/tcl/TkCmd/image.html>`_ documentation.
        expand: Grow the widget to match the container grid size, horizontally.
            See below for how the default is calculated.

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.

    .. note::

        There are at least 4 align options that might interact in weird ways.

        ``labelPosition`` only concerns how the label and image are aligned.
        This only matters when both are included.

        If only the image is included, ``expand`` defaults to `False`.

        If the label exists, the other 3 options govern its alignment.

        If the label has a single line, the default ``expand`` value depends if
        ``justify`` is given and not `model.Justification.NoJustify`. The
        default is not expanding, but if there's a non-default justification,
        ``expands`` defaults to `True` (otherwise it would have no effect).
        If ``expand`` is `True`, the ``justify`` value is used to calculate the
        ``anchor`` value, and the "real" ``justify`` value defaults to
        `model.Justification.Center`.

        If the label has multiple lines, ``expand`` defaults to `False`,
        ``justify`` defaults to `model.Justification.Center` and ``anchor``
        defaults to `model.CP.center`.

        **In a nutshell**, if the label has a single line, set ``justify``
        only. If it has multiple lines, set both ``align`` and ``justify``.
        The image and ``labelPosition`` options are orthogonal, they do not
        interact with the text alignment.
    '''
    label: typing.Optional[str] = None
    state_type = var.nothing

    def __init__(self, parent: mixin.ContainerWidget, *,
                 label: typing.Optional[str] = None,
                 anchor: typing.Optional[model.CP] = None,
                 justify: typing.Optional[model.Justification] = None,
                 labelPosition: model.compoundT = model.CP.E,
                 image: typing.Optional[tk.Image] = None,
                 expand: typing.Optional[bool] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        chosen_label = self.label or label
        if chosen_label is None and image is None:
            raise exception.InvalidWidgetDefinition('{self!r}: Needs an image or a label')
        self.init_single(vspec=None)  # No state here
        if chosen_label is not None:
            if '\n' in chosen_label:
                # Multi-Line Label
                expand = True if expand is None else expand
                justify = justify or model.Justification.Center
                anchor = anchor or model.CP.center
            else:
                # Single Line Label
                if expand is None:
                    expand = justify is not None and justify is not model.Justification.NoJustify
                justify = justify or model.Justification.Center
                if expand:
                    # - Adjust anchor to mimic justification
                    anchor = anchor or model.Justification_CP[justify]
                else:
                    anchor = anchor or model.CP.center
            assert anchor is not None
            assert justify is not None
            kwargs.update({
                'justify': justify.value,  # TODO: Move to `Style`?
                'anchor': anchor.value,  # TODO: Move to `Style`?
            })
        else:
            expand = False if expand is None else expand
        assert expand is not None
        kwargs.update({
            'image': image or '',
            'text': chosen_label or '',
            'compound': model.CP_Compound[labelPosition],
            'style': parent.wroot.register_styleID(styleID, 'TLabel'),
        })
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, **kwargs)  # ttk.Label
        if expand:
            self.grid(sticky=tk.NSEW)
        if __debug__:
            if 'textvariable' in kwargs:
                warnings.warn(f'{self}: To use a variable as label, see LabelStateful', stacklevel=2)

    def set_label(self, label: str) -> None:
        '''Change the label text.

        Be advised the label text must remain in the same "shape": Single or
        Multiline strings are supported, but not at runtime between them.
        '''
        assert '\n' in label == '\n' in self['text'], 'Cannot change the nature of the Label: Moved between single and multi lines'
        self['text'] = label

    def set_image(self, image: typing.Optional[tk.Image]) -> None:
        '''Change the label image.

        Be advised the label image must remain in the same "shape": Labels
        without image cannot get a new one, and Labels with image cannot lose
        its image.

        The image size (``width`` and ``height``) must also remain the same.
        '''
        if __debug__:
            if image is None:
                assert self['image'] == '', 'Cannot change the nature of the Label: New image'
            else:
                assert self['image'] != '', 'Cannot change the nature of the Label: Missing image'
                old_size = (self['image'].width(), self['image'].height())
                new_size = (image.width(), image.height())
                assert old_size == new_size, f'Cannot change the nature of the Label: Image resized {old_size} => {new_size}'
        self['image'] = image or ''


class LabelStateful(ttk.Label, mixin.SingleWidget):
    '''A stateful `Label`, where the text is controlled by a variable.

    This is an alternative `Label`, where the text is controlled by a variable.
    It's an alternative to manually calling `Label.set_label`, or a read-only
    `EntryRaw`.

    There is no Python documentation, see ``Tk`` `ttk.Label <https://www.tcl.tk/man/tcl/TkCmd/ttk_label.html>`_ documentation.

    Args:
        variable: Use an externally defined variable, instead of creating a new one specific for this widget.
        labelPosition: Label position, how to combine label and image.
            See `model.CP_Compound` for the possible values.
        image: The image to show. Optional.
            See ``Tk`` `tk.Image <https://www.tcl.tk/man/tcl/TkCmd/image.html>`_ documentation.

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.
    '''
    state_type = var.String

    def __init__(self, parent: mixin.ContainerWidget, *,
                 variable: typing.Optional[var.String] = None,
                 labelPosition: model.compoundT = model.CP.E,
                 image: typing.Optional[tk.Image] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        self.init_single(variable)
        kwargs.update({
            'textvariable': self.variable,
            'image': image or '',
            'compound': model.CP_Compound[labelPosition],
            'style': parent.wroot.register_styleID(styleID, 'TLabel'),
        })
        kwargs.pop('text', None)  # Ignore the given text
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, **kwargs)  # ttk.Label


class Button(ttk.Button, mixin.SingleWidget):
    '''A button with a label and/or an image.

    This is a button, with a label and/or an image. The main interaction is being clicked on.

    No state is included.

    There is no Python documentation, see ``Tk`` `ttk.Button <https://www.tcl.tk/man/tcl/TkCmd/ttk_button.html>`_ documentation.

    Args:
        label: The label to include inside the button. Optional.
            Can be given as a class variable.
        labelPosition: Label position, how to combine label and image.
            See `model.CP_Compound` for the possible values.
        image: The image to show. Optional.
            See ``Tk`` `tk.Image <https://www.tcl.tk/man/tcl/TkCmd/image.html>`_ documentation.
        width: The button width, in pixels.
            Defaults to an ad-hoc calculation based on the length of the label.

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.
    '''
    label: typing.Optional[str] = None
    state_type = var.nothing

    def __init__(self, parent: mixin.ContainerWidget, *,
                 label: typing.Optional[str] = None,
                 labelPosition: model.compoundT = model.CP.E,
                 image: typing.Optional[tk.Image] = None,
                 width: typing.Optional[int] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        chosen_label = self.label or label
        if chosen_label is None:
            raise exception.InvalidWidgetDefinition('{self!r}: Missing required label')
        self.init_single(vspec=None)  # No state here
        assert isinstance(chosen_label, str)
        if labelPosition not in model.CP_Compound:
            raise exception.InvalidWidgetDefinition(f'{self!r}: Invalid "labelPosition": {labelPosition}')
        kwargs.update({
            'text': chosen_label,
            'width': width or fn.label_size(len(label or 'M')),
            'command': self.invoke_onClick,
            'image': image or '',
            'compound': model.CP_Compound[labelPosition],
            'style': parent.wroot.register_styleID(styleID, 'TButton'),
        })
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, **kwargs)  # ttk.Button

    def invoke_onClick(self):
        ''''''  # Internal, do not document
        self.onClick()

    def onClick(self):
        """Callback to be called when clicking this widget.

        Defaults to doing nothing.

        Available for subclass redefinition.
        """
        pass


class Checkbox(ttk.Checkbutton, mixin.SingleWidget):
    '''A checkbox, simple boolean choice.

    This is a checkbox with a label. The main interaction is being clicked on,
    which toggles its value.
    Technically, the ``alternate`` GUI state allows for a trinary choice, but
    this is not directly supported as regular state.

    The state is a single `bool` value.

    There is no Python documentation, see ``Tk`` `ttk.Checkbutton <https://www.tcl.tk/man/tcl/TkCmd/ttk_checkbutton.html>`_ documentation.

    Args:
        label: The label to include besides the checkbox. Can be given as a class variable.
            It is included on the right side of the checkbox.
        readonly: Should the widget allow interaction to toggle its value.
            Default to *allowing* interaction.

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.
        variable: Use an externally defined variable, instead of creating a new one specific for this widget.

    .. note::

        The upstream widget does not disable user interaction when ``readonly``
        GUI state is enabled.

        This is worked around when the ``readonly`` argument is used, but this
        is not a dynamic setting like the GUI state.
        The "true" ``enabled`` state is tracked on the ``readonly`` state. This
        only matters for advanced styling uses, `gstate <MixinWidget.gstate>`
        returns the correct values.

        Uses a custom GUI state object, see `GuiState <Checkbox.GuiState>`.
    '''
    label: typing.Optional[str] = None
    state_type = var.Boolean

    class GuiState(model.GuiState):
        '''Custom `GuiState <model.GuiState>` for `Checkbox`.

        Since the ``readonly`` argument changes the semantics for the GUI
        state, in those cases the returned object uses this `GuiState
        <model.GuiState>` subclass.
        '''
        def real(self) -> model.GuiState:
            '''Return the underlying "real" `GuiState <model.GuiState>`.

            This is the state that matters for the Tk capabilites, like style
            mappings.
            '''
            # Reverse the change on `get_gui_state`/`set_gui_state`
            newstate = model.GuiState.new(self)
            newstate.enabled = False
            newstate.readonly = self.enabled
            return newstate

    def __init__(self, parent: mixin.ContainerWidget, *,
                 label: typing.Optional[str] = None,
                 readonly: bool = False,
                 variable: typing.Optional[var.Boolean] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        self.__readonly: bool = readonly
        chosen_label = self.label or label
        if chosen_label is None:
            raise exception.InvalidWidgetDefinition('{self!r}: Missing required label')
        self.init_single(variable, gkeys=['readonly', 'alternate'])
        assert isinstance(chosen_label, str)
        kwargs.update({
            'text': chosen_label,
            'onvalue': True,
            'offvalue': False,
            'variable': self.variable,
            'style': parent.wroot.register_styleID(styleID, 'TCheckbutton'),
        })
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, **kwargs)  # ttk.Checkbutton
        if readonly:
            self.set_gui_state()  # Trigger the readonly state adjustment

    def get_gui_state(self) -> model.GuiState:
        ''''''  # Internal, do not document
        # Wrap `mixin.MixinWidget.get_gui_state`
        state = super().get_gui_state()
        if self.__readonly:
            # if __debug__:
            #     logger.debug('%s: Real State: %s', self, state)
            # Track the "true" enabled state on the readonly option
            newstate = self.__class__.GuiState.new(state)  # New object
            newstate.enabled = state.readonly
            newstate.readonly = True
            state = newstate
        return state

    def set_gui_state(self, state: typing.Optional[model.GuiState] = None, **kwargs) -> model.GuiState:
        ''''''  # Internal, do not document
        # Wrap `mixin.MixinWidget.set_gui_state`
        if state is None:
            state = model.GuiState(**kwargs)
        # Read-only checkboxen are editable, for some reason
        # Make sure readonly checkboxen are always disabled
        if self.__readonly:
            # if __debug__:
            #     logger.debug('%s: Real State: %s', self, state)
            newstate = self.__class__.GuiState.new(state)  # New object
            # Track the "true" enabled state on the readonly state
            if state.enabled is not None:
                newstate.readonly = state.enabled is True
            # Force disable the widget
            newstate.enabled = False
            state = newstate
        return super().set_gui_state(state)

    def toggle(self) -> None:
        '''Switch the variable state to its opposite (`not <not>`).'''
        self.wstate = not self.wstate


class Radio(ttk.Radiobutton, mixin.SingleWidget):
    '''A radio button, a choice between several options.

    This is a radio button with a label. The main interaction is being clicked
    on, which sets its value. The same variable is shared between several
    widgets, each one contributing a single ``value``. When each widget is
    enabled, the variable is set to that value.

    Unlike other widgets, the variable must be created separately and given. It
    does not make much sense to create a variable to be used in a single radio
    button.

    The state is a single `str` value.

    There is no Python documentation, see ``Tk`` `ttk.Radiobutton
    <https://www.tcl.tk/man/tcl/TkCmd/ttk_radiobutton.html>`_ documentation.

    Args:
        label: The label to include besides the widget. Can be given as a class variable.
            It is included on the right side of the radio button.
        variable: The shared `specified variable <var.Spec>` attached to this
            widget. **Mandatory**.
        value: The value for this particular widget. Must be specified by the
            ``variable``, this is checked.
            **Mandatory**.

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.
    '''
    label: typing.Optional[str] = None
    state_type = var.Spec

    def __init__(self, parent: mixin.ContainerWidget, vspec: typing.Union[var.Spec, validation.VSpec], *,
                 value: str,
                 label: typing.Optional[str] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        chosen_label = self.label or label
        if chosen_label is None:
            raise exception.InvalidWidgetDefinition(f'{self!r}: Missing required label')
        self.init_single(vspec, gkeys=['alternate'])
        assert self.variable is not None and isinstance(self.variable, self.state_type)
        if value not in self.variable:
            raise exception.InvalidWidgetDefinition(f'{self}: Value "{value}" outside spec')
        assert isinstance(chosen_label, str)
        kwargs.update({
            'text': chosen_label,
            'value': value,
            'variable': self.variable,
            'style': parent.wroot.register_styleID(styleID, 'TRadiobutton'),
        })
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, **kwargs)  # ttk.Radiobutton
        if __debug__:
            assert self.variable is not None

    def isSelected(self) -> bool:
        '''Check if this specific widget is selected.

        This is equivalent to checking if the ``variable`` is set to the
        ``value`` chosen for this particular widget.
        '''
        return self.instate(['selected']) is True


class EntryRaw(ttk.Entry, mixin.SingleWidget):
    '''An entry widget, single-line text editor.

    This is an entry box, a single-line editor for strings. The main
    interaction is editing the text contained within.

    The state is a single `str` value, there is no validation.

    There is no Python documentation, see ``Tk`` `ttk.Entry <https://www.tcl.tk/man/tcl/TkCmd/ttk_entry.html>`_ documentation.

    Args:
        variable: Use an externally defined variable, instead of creating a new
            one specific for this widget.
        readonly: Should the widget allow interaction to toggle its value.
            Default to *allowing* interaction.
        justify: Justify entry text. Defaults to
            `model.Justification.NoJustify`, the upstream default.
        expand: Grow the widget to match the container grid size, horizontally.
            Defaults to `False`.

        label: The label to include besides the entry. **Not implemented yet**.
        styleID: Set a style identifier. Combined with the widget type in
            `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another
            `mixin.ContainerWidget`.
    '''
    state_type = var.String

    def __init__(self, parent: mixin.ContainerWidget, *,
                 variable: typing.Optional[var.String] = None,
                 readonly: bool = False,
                 justify: model.Justification = model.Justification.NoJustify,
                 expand: bool = False,
                 label: typing.Optional[str] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        self.init_single(variable, gkeys=['readonly'])
        self.label = label or ''  # TODO: Show label somehow?
        kwargs.update({
            'textvariable': self.variable,
            'justify': justify.value,
            'style': parent.wroot.register_styleID(styleID, 'TEntry'),
        })
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, **kwargs)  # ttk.Entry
        if expand:
            self.grid(sticky=tk.EW)
        if readonly:
            self.gstate = model.GuiState(readonly=True)
        if __debug__:
            if label is not None:
                warnings.warn(f'{self}: Labels on entries are still unsupported. Include a Label manually.', stacklevel=2)


# TODO: Rename to `Entry` in v0.40
class EntryN(ttk.Entry, mixin.SingleWidget, mixin.MixinValidation):  # type: ignore[misc]
    state_type = var.Spec

    def __init__(self, parent: mixin.ContainerWidget, vspec: var.Spec, *,
                 readonly: bool = False,
                 validation: typing.Union[model.VSettings, bool, None] = True,
                 justify: model.Justification = model.Justification.Center,
                 expand: bool = False,
                 label: typing.Optional[str] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        self.init_single(vspec, gkeys=['readonly'])
        self.label = label or ''  # TODO: Show label somehow?
        kwargs.update({
            'textvariable': self.variable,
            'justify': justify.value,
            'style': parent.wroot.register_styleID(styleID, 'TEntry'),
        })
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, **kwargs)  # ttk.Entry
        if expand:
            self.grid(sticky=tk.EW)
        if readonly:
            if validation not in (None, False):
                warnings.warn('Weird Widget: ReadOnly but Validated widget, are you sure about this?', stacklevel=3)
            self.gstate = model.GuiState(readonly=True)
        self.vsettings = self.init_validation(validation)
        if __debug__:
            if label is not None:
                warnings.warn(f'{self}: Labels on entries are still unsupported. Include a Label manually.', stacklevel=2)


# TODO: Support `SpinboxString` with values as a list of strings
# TODO: Rename to `SpinboxNum` in v0.40
class SpinboxN(ttk.Spinbox, mixin.SingleWidget, mixin.MixinValidation):    # type: ignore[misc]
    '''A spinbox widget, a numeric entry with buttons to change the value.

    This is spinbox, an `EntryRaw` storing a numeric value. The main
    interaction consists of two extra buttons to increment and decrement the
    value.

    The state changes do no wrap around by default, unless this is requested
    using the ``wrap`` argument.

    The widget state is a `VState`, with the value being specified on the
    variable. A simple `str` label can also be set.

    There is no Python documentation, see ``Tk`` `ttk.Spinbox <https://www.tcl.tk/man/tcl/TkCmd/ttk_spinbox.html>`_ documentation.

    Args:
        variable: The `variable <var.Limit>` attached to this widget. **Mandatory**.
        readonly: Should the widget allow arbitrary state changes, possibly to
            unknown values. Defaults to `True`, the only way to change the state is
            by using the extra buttons.
        validation: Configure widget validation.
            Defaults to validating based on variable state.
        wrap: Wrap changes around the limits. Defaults to `False`.
        variable: Use an externally defined variable, instead of creating a new
            one specific for this widget.
        justify: Justify entry box text. Defaults to `model.Justification.Center`.

        label: The label to include besides the entry. **Not implemented yet**.
        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.
    '''
    state_type = var.Limit
    vsettings: typing.Optional[model.VSettings]

    def __init__(self, parent: mixin.ContainerWidget, vspec: typing.Union[var.Limit, validation.VSpec], *,
                 readonly: bool = True,
                 validation: typing.Union[model.VSettings, bool, None] = True,
                 wrap: bool = False,
                 justify: model.Justification = model.Justification.Center,
                 label: typing.Optional[str] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        self.init_single(vspec, gkeys=['readonly'])
        assert self.variable is not None and isinstance(self.variable, self.state_type)
        sfrom, sto, sincrement = self.variable.get_spinargs()
        kwargs.update({
            'textvariable': self.variable,
            'from': sfrom, 'to': sto, 'increment': sincrement,
            'wrap': wrap,
            'justify': justify.value,
            'style': parent.wroot.register_styleID(styleID, 'TSpinbox'),
        })
        if 'values' in kwargs:
            raise exception.InvalidWidgetDefinition('Invalid `values` setting, unsupported')
        super().__init__(parent, **kwargs)
        if readonly:
            self.gstate = model.GuiState(readonly=True)
        self.vsettings = self.init_validation(validation)
        if __debug__:
            if label is not None:
                warnings.warn(f'{self}: Labels on Spinbox are still unsupported. Include a Label manually.', stacklevel=2)


# TODO: Rename to `Combobox` in v0.40
class ComboboxN(ttk.Combobox, mixin.SingleWidget, mixin.MixinValidation):    # type: ignore[misc]
    '''A combobox widget, combining an entry and a listbox.

    This is a combobox, an `EntryRaw` with a button that shows a pop-up `Listbox`
    with the variable options.

    The entry can be ``readonly``, in which case the only possible values are
    the ones shown on the value list, otherwise the entry is editable with
    arbitrary values, just like any `EntryRaw`.

    The widget state is a `VState`, with the value being specified on the
    variable. A simple `str` label can also be set.

    There is no Python documentation, see ``Tk`` `ttk.Combobox <https://www.tcl.tk/man/tcl/TkCmd/ttk_combobox.html>`_ documentation.

    Args:
        variable: The `variable <var.SpecCountable>` attached to this widget. **Mandatory**.
        readonly: Should the widget allow arbitrary state changes, possibly to
            unknown values. Defaults to `True`, the only way to change the state is
            by using the listbox selection.
        validation: Configure widget validation.
            Defaults to validating based on variable state.
        justify: Justify combobox text.
            Defaults to `model.Justification.Center` if ``readonly`` (the
            default), `model.Justification.NoJustify` otherwise.

        label: The label to include besides the combobox. **Not implemented yet**.
        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.

    .. note::

        Even though this widget is configured as ``readonly``, it's still
        possible to have invalid values if the variable is used on other
        non-``readonly`` widgets, or if it is programatically changed ignoring
        the specification.

        If you want to make sure this is truly read-only (and therefore always
        valid), do not reuse the variable anywhere else.
    '''
    state_type = var.SpecCountable

    def __init__(self, parent: mixin.ContainerWidget, vspec: typing.Union[var.SpecCountable, validation.VSpec], *,
                 readonly: bool = True,
                 validation: typing.Union[model.VSettings, bool, None] = True,
                 label: typing.Optional[str] = None,
                 justify: typing.Optional[model.Justification] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        self.init_single(vspec, gkeys=['readonly'])
        assert self.variable is not None and isinstance(self.variable, self.state_type)
        self.label = label or ''  # TODO: Show label somehow
        if justify is None:
            justify = model.Justification.Center if readonly else model.Justification.NoJustify
        assert justify is not None
        kwargs.update({
            'textvariable': self.variable,
            'justify': justify.value,  # TODO: Move to `Style`?
            'values': list(self.variable.lall()),
            'style': parent.wroot.register_styleID(styleID, 'TCombobox'),  # Also: ComboboxPopdownFrame
        })
        super().__init__(parent, **kwargs)  # ttk.Combobox
        if readonly:
            self.gstate = model.GuiState(readonly=True)
            # Visual cleanup
            self.trace(self.__combobox_rocls, trace_name='__:ro_cls')
        self.vsettings = self.init_validation(validation)
        if __debug__:
            if label is not None:
                warnings.warn(f'{self}: Labels on Combobox are still unsupported. Include a Label manually.', stacklevel=2)
            if len(self.variable) > 30:  # Just an arbitrary heuristic
                warnings.warn(f'{self}: Too many choices ({len(self.variable)}), this has bad UX', stacklevel=2)

    def __combobox_rocls(self, rstate, etype):
        self.selection_clear()


class FrameStateful(ttk.LabelFrame, mixin.ContainerWidget):
    '''A frame to hold other widgets, with a checkbox.

    This is a frame with an embedded checkbox `cstate_widget` as "label". This
    label controls the enabled state of the child widgets. You can control the
    checkbox position.

    There is no Python documentation, see ``Tk`` `ttk.LabelFrame <https://www.tcl.tk/man/tcl/TkCmd/ttk_labelframe.html>`_ documentation.
    Note the ``labelwidget`` option.

    Args:
        label: The label to include on the frame separator. Can be given as a class variable.
        labelAnchor: The position of the label on the frame separator.
            Given as one of the cardinal points.
            Defaults to a OS-specific location (`model.CP.default`).
        cvariable: Use an externally defined `cstate` variable, instead of
            creating a new one specific for the `cstate` widget.
        cvariableDefault: The default value for `cstate`.
            When `None`, the value is not changed at start.
            Defaults to starting enabled, unless ``cvariable`` is given, for
            which the value is not changed.
        cstateArgs: Extra arguments for the `cstate` widget, `cstate_widget`.

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.

    See Also:
        - `FrameLabelled`: A simpler version of this, without the embedded checkbox.
        - `FrameRadio`: A variant of this widget, with a radio button.
    '''
    label: typing.Optional[str] = None

    class __w_cstate(Checkbox):
        isAuto = None  # Isolate from GUI state, taken care in `set_gui_state`

    cstate_widget: __w_cstate
    '''The widget for the embedded `Checkbox`.

    Uses the `cstate` variable.

    Note:
        The widget type is a local `Checkbox` subclass, specific for this widget.
    '''
    cstate: var.Boolean
    '''The variable holding the embedded `Checkbox` state.

    Used on the `cstate_widget`.

    See Also:
        ``cvariable``: This can be configured as an external variable.
    '''

    def __init__(self, parent: mixin.ContainerWidget, *args,
                 label: typing.Optional[str] = None, labelAnchor: model.CP = model.CP.default,
                 cvariable: typing.Optional[var.Boolean] = None, cvariableDefault: typing.Optional[bool] = None,
                 cstateArgs: typing.Optional[typing.Mapping[str, typing.Any]] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        # Create the checkbox widget
        chosen_label = self.label or label
        if chosen_label is None:
            raise exception.InvalidWidgetDefinition('Missing required label')
        cstateArgs = dict(cstateArgs or {})
        cstateArgs.update({  # Override cstate arguments
            'variable': cvariable,
            'label': chosen_label,
            'readonly': False,
        })
        cstate_widget = self.__class__.__w_cstate(parent, **cstateArgs)
        assert isinstance(cstate_widget.variable, var.Boolean), f'{self!r} checkbox widget is not a simple boolean'
        self.cstate = cstate_widget.variable
        # Usual Initialization
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, labelwidget=cstate_widget, labelanchor=labelAnchor.value,
                         style=parent.wroot.register_styleID(styleID, 'TLabelframe'),  # Also: TLabelframe.Label
                         )  # ttk.LabelFrame
        self.init_container(*args, **kwargs)
        # Configure the checkbox widget
        self.cstate_widget = cstate_widget
        self.cstate_widget.trace(self.onChanged_cstate)
        # Setup the default value for that widget
        if __debug__:
            if cvariable is not None and cvariableDefault is not None:
                warnings.warn(f'{self}: cvariable: Setting a default with an external variable')
        if cvariable is None and cvariableDefault is None:
            cvariableDefault = True
        if cvariableDefault is not None:
            self.cstate.set(cvariableDefault)

    def state_get(self, *args, vid_upstream: typing.Optional[typing.Set[str]] = None, **kwargs) -> model.WState[bool, typing.Any]:
        ''''''  # Do not document
        cid = fn.vname(self.cstate)
        if vid_upstream and cid in vid_upstream:
            cstate = None
        else:
            cstate = self.cstate.get()
        return model.WState(
            cstate,
            super().state_get(*args, vid_upstream=vid_upstream, **kwargs),
        )

    def state_set(self, state: model.WState[bool, typing.Any], *args, **kwargs):
        ''''''  # Do not document
        if state.state is not None:
            assert isinstance(state.state, bool), f'Invalid WState: {state!r}'
            self.cstate.set(state.state)
        super().state_set(state.substate, *args, **kwargs)

    def set_gui_state(self, state: typing.Optional[model.GuiState] = None, _sub: bool = False, **kwargs) -> model.GuiState:
        ''''''  # Do not document
        # "Trace" the frame enabled status
        frame_enabled = kwargs.get('enabled', None) if state is None else state.enabled
        self_state = super().set_gui_state(state, _sub=False, **kwargs)
        if frame_enabled is not None:
            state_enabled = self.cstate.get()
            # if __debug__:
            #     logger.debug(f'S| {self}: F={frame_enabled} S={state_enabled}')
            self.cstate_widget.gstate = model.GuiState(enabled=frame_enabled)
            self.set_gui_substate(model.GuiState(enabled=frame_enabled and state_enabled))
            # TODO: unsetOnDisable
            # TODO: setOnEnable
        return self_state

    def onChanged_cstate(self, cstate, etype):
        assert etype == 'write'
        status = cstate.get()
        frame_enabled = self.gstate.enabled
        # if __debug__:
        #     logger.debug(f'{self}: S={status} Fe={frame_enabled}')
        self.set_gui_substate(model.GuiState(enabled=frame_enabled and status))


class FrameRadio(ttk.LabelFrame, mixin.ContainerWidget):
    '''A frame to hold other widgets, with a radio button.

    This is a frame with an embedded radio button `rstate_widget` as "label".
    This label controls the enabled state of the child widgets. You can control
    the radio button position.

    Unlike other widgets, the variable must be created separately and given in
    addition to the value. See `Radio`.

    There is no Python documentation, see ``Tk`` `ttk.LabelFrame
    <https://www.tcl.tk/man/tcl/TkCmd/ttk_labelframe.html>`_ documentation.
    Note the ``labelwidget`` option.

    Args:
        rvariable: The shared variable attached to this widget. Requires a
            specification too, see `var.Spec` for more information.
            **Mandatory**.
        rvalue: The value for this particular widget. Must be specified by the
            ``variable``, this is checked.
            **Mandatory**.
        label: The label to include besides the widget. Can be given as a class variable.
        labelAnchor: The position of the label on the frame separator.
            Given as one of the cardinal points.
            Defaults to a OS-specific location (`model.CP.default`).
        rstateArgs: Extra arguments for the `rstate` widget, `rstate_widget`.

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.

    See Also:
        - `FrameLabelled`: A simpler version of this, without the embedded radio button.
        - `FrameStateful`: A variant of this widget, with a checkbox.
    '''
    label: typing.Optional[str] = None

    class __w_rstate(Radio):
        isAuto = None  # Isolate from GUI state, taken care in `set_gui_state`

    rstate_widget: __w_rstate
    '''The widget for the embedded `Radio`.

    Uses the `rstate` variable.

    Note:
        The widget is a local `Radio` subclass, specific for this widget.
    '''

    rstate: var.Spec
    '''The variable holding the embedded `Radio` state.

    Used on the `rstate_widget`.
    '''

    def __init__(self, parent: mixin.ContainerWidget, *args,
                 rvariable: var.Spec, rvalue: str,
                 label: typing.Optional[str] = None, labelAnchor: model.CP = model.CP.default,
                 rstateArgs: typing.Optional[typing.Mapping[str, typing.Any]] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        chosen_label = self.label or label
        if chosen_label is None:
            raise exception.InvalidWidgetDefinition('Missing required label')
        # Create the "label" widget
        rstateArgs = dict(rstateArgs or {})
        rstateArgs.update({  # Override rstate arguments
            'vspec': rvariable, 'value': rvalue,
            'label': chosen_label,
        })
        rstate_widget = self.__class__.__w_rstate(parent, **rstateArgs)
        assert rvariable == rstate_widget.variable
        self.rstate = rvariable
        # Usual Initialization
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, labelwidget=rstate_widget, labelanchor=labelAnchor.value,
                         style=parent.wroot.register_styleID(styleID, 'TLabelframe'),  # Also: TLabelframe.Label
                         )  # ttk.LabelFrame
        self.init_container(*args, **kwargs)
        # Configure the radio widget
        self.rstate_widget = rstate_widget
        self.rstate_widget.trace(self.__onChanged_rstate(rvalue), trace_name='__:substate')

    def set_gui_state(self, state: typing.Optional[model.GuiState] = None, _sub: bool = False, **kwargs) -> model.GuiState:
        ''''''  # Do not document
        # "Trace" the frame enabled status
        frame_enabled = kwargs.get('enabled', None) if state is None else state.enabled
        self_state = super().set_gui_state(state, _sub=False, **kwargs)
        if frame_enabled is not None:
            state_enabled = self.isSelected()
            # if __debug__:
            #     logger.debug(f'S| {self}: F={frame_enabled} S={state_enabled}')
            self.rstate_widget.gstate = model.GuiState(enabled=frame_enabled)
            self.set_gui_substate(model.GuiState(enabled=frame_enabled and state_enabled))
        return self_state

    def __onChanged_rstate(self, rvalue: str) -> typing.Callable[[var.Variable, str], None]:
        def onChanged_rstate(rstate: var.Variable, etype: str) -> None:
            assert etype == 'write'
            rresult = rstate.get()
            status = rresult.valid and rresult.label == rvalue
            frame_enabled = self.gstate.enabled
            # if __debug__:
            #     logger.debug(f'{self}: S={status} Fe={frame_enabled}')
            self.set_gui_substate(model.GuiState(enabled=frame_enabled and status))
        return onChanged_rstate

    def isSelected(self) -> bool:
        '''Check if this specific widget is selected.'''
        return self.rstate_widget.isSelected()


# TODO: Support "valid", always True
class EntryMultiline(tk.Text, mixin.SingleWidget):
    '''A multiline text widget, supporting `LTML` contents.

    This is a multiline version of the `EntryRaw` widget, with rich text
    capabilities.
    Supports only the readonly state, that is, the widget contents can only be
    edited programatically.

    The state is a single `str` value, internally parsed to `parser.LTML
    <LTML>`.

    There is no Python documentation, see ``Tk`` `tk.Text <https://www.tcl.tk/man/tcl/TkCmd/text.html>`_ documentation.

    Args:
        variable: Use an externally defined variable, instead of creating a new
            one specific for this widget.
        style: Configure the widget style.

        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.

    Note:

        The underlying widget is not part of `ttk <tkinter.ttk>` like most others. All
        efforts are expended to make this an implementation detail, without
        practical effects.
    '''
    state_type = var.String
    _bindings_tag: typing.MutableMapping[typing.Tuple[str, str], model.BindingTag]
    '''Store all widget `BindingTag` objects, keyed by ``(tag, name)`` (see `binding_tag`).'''
    styleSheet: typing.Optional[typing.Mapping[str, typing.Mapping[str, typing.Any]]] = None
    '''Store a style sheet mapping identifiers/classes to styling configuration.

    Identifiers are marked on LTML as ``<span id="something">``, and on the
    style sheet as ``#something``.

    Classes are marked on LTML as ``<span class="something">``, and on the
    style sheet as ``.something``.

    There is no Python documentation, see ``Tk`` `text tags
    <https://www.tcl.tk/man/tcl/TkCmd/text.html#M43>`_ documentation.
    '''

    @dataclass
    class Style(model.WStyle):
        '''`EntryMultiline` style object.

        These are the settings:

        Args:
            font_base: Base Font name, for all the widget.
            colour_bg_on: Widget background, when enabled.
            colour_bg_off: Widget background, when disabled.
            colour_link_normal: Hyperlink foreground colour, normal links.
            colour_link_visited: Hyperlink foreground colour, visited links.
            cursor_link: Hyperlink cursor. Set only when hovering over the links.
                Optional, disabled when set to `None`.
        '''
        font_base: str = 'TkTextFont'  # This font should be used for user text in entry widgets, listboxes etc.
        colour_bg_on: str = 'white'
        colour_bg_off: str = 'lightgrey'
        colour_link_normal: str = 'blue'
        colour_link_visited: str = 'purple'
        cursor_link: typing.Optional[str] = 'hand2'

    def __init__(self, parent: mixin.ContainerWidget, *,
                 variable: typing.Optional[var.String] = None,
                 style: Style = Style(_default=True),
                 **kwargs):
        self.wstyle = style
        self.init_single(variable)
        kwargs.pop('state', None)  # Support only readonly state
        kwargs['font'] = style.font_base  # Override the base font
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, **kwargs)  # tk.Text
        readonly = True  # Support only readonly state, for now...
        # GUI State Tracker
        # - Since this is not a `ttk.Widget`, this need to be emulated
        self.__gstate: model.GuiState = model.GuiState(enabled=True, valid=True)
        # - Set the internal readonly state out-of-the-box
        self.set_gui_state(readonly=readonly, _internal=True)
        assert self.variable is not None, f'{self!r}: Missing variable'
        self.wstate = getattr(self.variable, '_default', '')  # Set the default (before the trace)
        # State Tracker
        self.trace(self._varChanged, trace_name=f'__:{__name__}')
        # StyleSheet
        if self.styleSheet:
            if __debug__:
                def _setupStylesheet():
                    try:
                        self._setupStylesheet()
                    except tk.TclError as e:
                        logger.error('%s:: Invalid StyleSheet: %s', self, e)
                        sys.exit(100)
            else:
                _setupStylesheet = self._setupStylesheet
            self.after_idle(_setupStylesheet)  # No need for a `TimeoutIdle` here

        # Bindings
        self._bindings_tag = {}
        self.binding_tag('a', '<Button-1>', self._onClickTag)
        if self.wstyle.cursor_link is not None:
            self.binding_tag('a', '<Enter>', self._onCursor)
            self.binding_tag('a', '<Leave>', self._onCursor)
        if readonly:
            # Disable Double-Click event, when readonly
            self.binding('<Double-Button-1>', fn.binding_disable)

    def _varChanged(self, var, etype):
        assert etype == 'write'
        # This function is called when the value changes
        # It's the implementation that binds the variable and the widget,
        #  so this should be idempotent
        vs = var.get()
        with self.as_editable():
            # Delete the entire state
            # From: First line, first character
            #   To: End
            self.delete('1.0', 'end')
            # Reset styles
            self.style_reset()
            # Add the current state
            # TODO: Save the parsed LTML state somewhere in this object, with `data`?
            for te in parser.parse_LTML(vs):
                assert isinstance(te, model.TextElement)
                self.insert(tk.END, te.text, te.atags)

    def _setupStylesheet(self) -> None:
        assert self.styleSheet is not None
        if __debug__:
            logger.debug('Set StyleSheet [%s]:', self)
        for sid, skwargs in self.styleSheet.items():
            if __debug__:
                logger.debug('| %s: %s', sid, ' '.join('%s=%r' % tpl for tpl in skwargs.items()))
            self.tag_configure(sid, **skwargs)

    def get_gui_state(self) -> model.GuiState:
        ''''''  # Do not document
        # if __debug__:
        #     logger.debug('State > %r', self.__gstate)
        # return a copy of the object
        return model.GuiState(**dict(self.__gstate.items()))

    def set_gui_state(self, state: typing.Optional[model.GuiState] = None, *, _internal: bool = False, **kwargs) -> model.GuiState:
        ''''''  # Do not document
        if state is None:
            state = model.GuiState(**kwargs)
        # if __debug__:
        #     logger.debug('State < %r', state)
        # Adjust current state
        for sname, svalue in state.items():
            assert sname != '_internal'  # Should be impossible...
            if svalue is not None:
                if sname == 'readonly' and _internal is False:
                    raise ValueError(f'{self}: No support for external readonly state manipulation')
                setattr(self.__gstate, sname, svalue)
        # Adjust widget state
        cfg = {}
        if self.__gstate.enabled is True:
            if self.__gstate.readonly is not None:
                cfg['state'] = tk.NORMAL if not self.__gstate.readonly else tk.DISABLED
            cfg['background'] = self.wstyle.colour_bg_on
        elif self.__gstate.enabled is False:
            cfg['state'] = tk.DISABLED
            cfg['background'] = self.wstyle.colour_bg_off
            self.style_reset()
        # if __debug__:
        #     logger.debug('C %s', self.__gstate)
        #     logger.debug('| %s', cfg)
        self.configure(**cfg)
        # Valid: TBD
        assert state is not None
        return state

    @contextmanager
    def as_editable(self):
        '''Temporarily mark the widget as editable.

        A context manager, used to change the contents of the widget while keep
        it "readonly".
        Technically, this should only be used internally, using the state
        tracker functions, but it might be useful externally.

        This is to be used like this:

        .. code:: python

            # `widget` is readonly
            with widget.as_editable():
                pass  # `widget` is editable
            # `widget` is readonly
        '''
        assert self.__gstate.readonly is True
        self.set_gui_state(readonly=False, _internal=True)
        try:
            yield
        finally:
            self.set_gui_state(readonly=True, _internal=True)

    def binding_tag(self,
                    tag: str, sequence: str,
                    *args,
                    key: typing.Optional[str] = None,
                    immediate: bool = True,
                    **kwargs,
                    ) -> model.BindingTag:
        '''Binds a sequence to a tag.

        Stores all widget tag bindings on a per-instance dictionary, for later
        usage. Note that all dictionary keys must be different. For the same
        bindings on a single widget tag, this requires passing the ``key``
        argument.

        See the ``Tk`` `tag bind <https://www.tcl.tk/man/tcl/TkCmd/text.html#M166>`_ documentation.

        Args:
            key: Optional. Defaults to the ``sequence`` itself. Useful to
                support multiple bindings on the same sequence, for the same tag.

        All other arguments are passed to `model.BindingTag` object.
        '''
        name = (tag, key or sequence)
        if name in self._bindings_tag:
            raise ValueError(f'Repeated binding for "{sequence}" in {self!r}(tag "{tag}"). Change the "key" parameter.')
        if __debug__:
            if len(tag) == 0 or tag[0] == '<':
                warnings.warn(f'{self}: binding_tag requires tag[{tag}] and sequence[{sequence}], by this order', stacklevel=2)
        self._bindings_tag[name] = model.BindingTag(self, tag, sequence, *args, immediate=immediate, **kwargs)
        return self._bindings_tag[name]

    # TODO: use an `lru_cache`?
    def _font(self, fontbase: typing.Optional[tk.font.Font] = None,
              *,
              size: typing.Optional[int] = None,
              bold: typing.Optional[bool] = None,
              italic: typing.Optional[bool] = None,
              ):
        fontbase = fontbase or tk.font.nametofont(self.wstyle.font_base)
        # Start from the base font options
        options = fontbase.actual()
        if size:
            options['size'] = size
        if bold is True:
            options['weight'] = tk.font.BOLD
        if italic is True:
            options['slant'] = tk.font.ITALIC
        return tk.font.Font(**options)

    def _style_a(self, tag: str = 'a', *, visited: bool) -> None:
        fg = self.wstyle.colour_link_visited if visited else self.wstyle.colour_link_normal
        self.tag_configure(tag, foreground=fg, underline=True)

    def style_reset(self, event=None, *, a: bool = True, b: bool = True, i: bool = True) -> None:
        '''Reset the style to the original.

        Args:
            a: Reset ``a`` anchors.
            b: Reset ``b`` bold inline spans.
            i: Reset ``i`` italic inline spans.

            event: Optional, unused. This exists for API compatibility with the
                ``onClick`` functions.
        '''
        # TODO: Why not reset everything always? YAGNI.
        if b:
            self.tag_configure('b', font=self._font(bold=True))
        if i:
            self.tag_configure('i', font=self._font(italic=True))
        for tag in self.tag_names():
            # a
            if a and tag == 'a' or tag.startswith('a::'):
                self._style_a(tag=tag, visited=False)

    def _onClickTag(self, event, *, tag_name: str = 'a'):
        if not self.__gstate.enabled:  # TODO: disable the binding?
            return  # Do nothing when disabled
        dobj = self.dump(f'@{event.x},{event.y}', text=True, tag=True)
        if __debug__:
            logger.debug('D: %r', dobj)
        dwhat = [dinner[0] for dinner in dobj]
        tags_cl = []  # Ignore the "sel" tag
        if 'tagon' in dwhat:
            # Click in the start of the tag
            tags_cl = [lst[1] for lst in dobj if lst[0] == 'tagon' and lst[1] != tk.SEL]
            # For nested tags, this might not be the same as the text method
        if len(tags_cl) == 0 and 'text' in dwhat:
            # Click in the middle of the tag
            click_location = [lst[2] for lst in dobj if lst[0] == 'text'][0]
            tp = self.tag_prevrange(tag_name, click_location)
            if __debug__:
                logger.debug(' | Text @ <%s', tp)
            tags_cl = [lst[1] for lst in self.dump(*tp, tag=True) if lst[1] != tk.SEL]
        if len(tags_cl) == 0:
            raise NotImplementedError
        if __debug__:
            logger.debug(' | Tags %s', tags_cl)
        assert len(tags_cl) >= 2, f'Missing tags: {tags_cl}'
        tags_proc = [t for t in tags_cl if '::' in t]
        assert len(tags_proc) == 1
        tagi = tags_proc[0]
        tag = tagi.split('::')[0]
        assert tag_name == tag, f'Wrong onClickTag: Requested[{tag_name}] != Found[{tag}]'
        assert tag in tags_cl, f'Wrong tag_index: {tag}[{tagi}]'
        tags_other = [t for t in tags_cl if t not in (tag, tagi)]
        if __debug__:
            logger.debug(f' = {tag}[{tagi}]')
        self._style_a(tag=tagi, visited=True)
        self.onClickTag(tag, tagi, tags_other)

    def _onCursor(self, event: typing.Any = None) -> None:
        if not self.__gstate.enabled:  # TODO: disable the binding?
            return  # Do nothing when disabled
        assert event is not None
        assert event.type in (tk.EventType.Enter, tk.EventType.Leave), f'Invalid EventType: {event.type!r}'
        widget = event.widget
        assert self.wstyle.cursor_link is not None, f'{widget!r}: Disabled link hovering'
        hover = event.type == tk.EventType.Enter
        cname: str = self.wstyle.cursor_link if hover else ''
        # if __debug__:
        #     logger.debug('| %s: %s > "%s"', widget, event.type.name, cname)
        widget['cursor'] = cname

    def onClickTag(self, tag: str, tag_index: str, tags_other: typing.Sequence[str]) -> None:
        '''Callback to be called when clicking ``a`` tags in this widget.

        Defaults to doing nothing.

        Available for subclass redefinition.

        Args:
            tag: The main tag type. In this case, it's always ``a``.
            tag_index: The tag index. See `LTML <parser.LTML>` Automatic Counter tags.
            tags_other: List of extra tags attached to the anchor. Might be empty.
        '''
        pass

    def wstateLTML(self) -> typing.Generator[model.TextElement, None, None]:
        '''Return the parsed LTML state, as a generator of `model.TextElement`.

        See Also:
            - `wstate`: Return the LTML string.
            - `wstateText`: Return the underlying text, without any tags.
        '''
        # TODO: Save the parsed LTML state somewhere in this object, with `data`?
        yield from parser.parse_LTML(self.wstate)

    def wstateText(self) -> str:
        '''Strip all LTML tags and return the underlying text.

        See Also:
            - `wstate`: Return the LTML string.
            - `wstateLTML`: Generate a list of LTML parsed objects.
        '''
        # TODO: Save the parsed LTML state somewhere in this object, with `data`?
        return ''.join(
            te.text
            for te in parser.parse_LTML(self.wstate)
        )


class Notebook(ttk.Notebook, mixin.ContainerWidget):
    '''A tabbed interface to hold other containers.

    This is a tabbed interface to show several containers in the same space.

    The individual tabs must all be containers, there's no support for single
    widgets. Use a holder `FrameUnlabelled` to show a single widget for each
    tab.

    There is no Python documentation, see ``Tk`` `ttk.Notebook <https://www.tcl.tk/man/tcl/TkCmd/ttk_notebook.html>`_ documentation.

    Args:
        traversal: Setup tab traversal with special keyboard shortcuts, and
            also with mouse wheel scrolling. See the Tk documentation for the
            keyboard part. Enabled by default.
        traversalWraparound: When ``traversal`` is setup, configure wraparound.
            That is, scrolling to the next tab from the last one should "scroll"
            into the first tab, and vice-versa for the first tab. This only matters
            for the mouse wheel traversal, the keyboard shortcuts always enable
            this traversal.
            Disabled by default.

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        layout: Ignored, it is hardcoded to `None` always.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.

    See Also:
        `NotebookUniform`: A simpler version of this, when each individual tab is the same type
    '''
    Tab = model.NotebookTab  # Alias the notebook tab information  # TODO: Move NotebookTab class here?
    '''Alias for `model.NotebookTab` class.'''
    wtabs: typing.Mapping[str, model.NotebookTab]
    '''Mapping of tab identifiers, and `model.NotebookTab` objects.'''

    def __init__(self, parent: mixin.ContainerWidget, *args,
                 layout: None = None,
                 traversal: bool = True,
                 traversalWraparound: bool = False,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, style=parent.wroot.register_styleID(styleID, 'TNotebook'))
        # No `layout` is used, force it to `None`
        self.init_container(*args, layout=None, **kwargs)
        # Tab Traversal
        self.tWraparound = traversalWraparound
        if traversal:
            # TODO: Re-Implement locally, take `traversalWraparound` into account.
            #       Map:
            #       - `Ctrl-Tab`: _tabScrollUp
            #       - `Ctrl-Shift-Tab`: _tabScrollDown
            self.enable_traversal()
            # Bind mouse wheel: Digital Scrolling
            self._traversal = fn.bind_mousewheel(self, up=self._tabScrollUp, down=self._tabScrollDown, immediate=True)

    def setup_widgets(self, *args, **kwargs):
        '''Define the sub widgets based on the tabs.

        Do not overwrite this unless you know what you are doing.

        To edit the tabs, see `setup_tabs`.
        '''
        self.wtabs = self.setup_tabs(*args, **kwargs)
        # if __debug__:
        #     logger.debug(f'{self}: {len(self.wtabs)} Tabs')
        widgets = {}
        for identifier, ti in self.wtabs.items():
            # if __debug__:
            #     logger.debug('> %s: %r', ti.name, ti.widget)
            assert isinstance(ti.widget, mixin.ContainerWidget), f'{self!r}: Tab Widget [{ti.identifier or identifier}]"{ti.name}" must be a container'
            extra = {
                **ti.extra,
                'text': ti.name,
                'image': ti.image or '',
                'compound': ti.imageCompound,
            }
            self.add(ti.widget, **extra)
            ti.identifier = identifier
            widgets[identifier] = ti.widget
        return widgets

    def setup_tabs(self, *args, **kwargs) -> typing.Mapping[str, model.NotebookTab]:
        '''Define the tabs here.

        Similar to `setup_widgets <mixin.ContainerWidget.setup_widgets>`, but
        defines `model.NotebookTab`, extra information about each widget.
        '''
        raise NotImplementedError

    def wtab(self, idx: str) -> mixin.ContainerWidget:
        '''Get the tab widget by identifier.

        This is just an helper function to get the correct widget value out of
        `wtabs`.

        Args:
            idx: The tab identifier.

        Note:
            In debug mode, this will fail if called with the wrong identifier.
            This check is skipped for performance on optimized mode.
        '''
        wtab = self.wtabs.get(idx, None)
        assert wtab is not None, f'Invalid Selection: {idx}'
        return wtab.widget

    def wselection(self) -> str:
        '''Search for the current selected tab.

        Returns:
            This functions searches for the currently selected tab, and returns its
            identifier (the key on the `wtabs` dictionary).
        '''
        # TODO: Optimise this? Save a dict of indexes or something?
        selected_id = self.select()
        # if __debug__:
        #     logger.debug('S: %r', selected_id)
        #     tabs_id = [str(w) for w in self.tabs()]
        #     logger.debug(' | %s', ' '.join(tabs_id))
        for idx, wtab in self.wtabs.items():
            if str(wtab.widget) == selected_id:
                return idx
        raise ValueError('{self!r}: Invalid current selection: {selected_id!r}')

    def wselect(self, idx: str) -> None:
        '''Select a tab by identifier.

        Args:
            idx: The tab identifier.

        Note:
            In debug mode, this will fail if called with the wrong identifier.
            This check is skipped for performance on optimized mode.
        '''
        wtab = self.wtabs.get(idx, None)
        assert wtab is not None, f'Invalid Selection: {idx}'
        self.select(tab_id=str(wtab.widget))

    def _tabScrollUp(self, event=None):
        keys = list(self.wtabs.keys())
        selected = self.wselection()
        if selected == keys[0]:
            # First Tab
            if self.tWraparound:
                new_selected = keys[-1]
            else:
                new_selected = None
        else:
            # TODO: Optimise this? See `wselection`
            selected_idx = keys.index(selected)
            new_selected = keys[selected_idx - 1]
        if new_selected:
            self.wselect(new_selected)

    def _tabScrollDown(self, event=None):
        keys = list(self.wtabs.keys())
        selected = self.wselection()
        if selected == keys[-1]:
            # Last Tab
            if self.tWraparound:
                new_selected = keys[0]
            else:
                new_selected = None
        else:
            # TODO: Optimise this? See `wselection`
            selected_idx = keys.index(selected)
            new_selected = keys[selected_idx + 1]
        if new_selected:
            self.wselect(new_selected)


class NotebookUniform(Notebook):
    '''A tabbed interface to hold a series of uniform containers.

    This is a variant of the regular `Notebook` specially created to simplify
    the usual case where all the tabs are very similar (usually, they are the
    same underlying class).

    Args:
        tabids: A mapping of tab identifiers and tab titles.

    See Also:
        `Notebook`: A fully generic version of this. Don't try to make the
        `setup_tab` function too complex, move to this widget instead.
    '''
    tabids: typing.Optional[typing.Mapping[str, str]] = None

    def __init__(self, *args, tabids: typing.Optional[typing.Mapping[str, str]] = None, **kwargs):
        self.tabids = self.tabids or tabids
        if self.tabids is None:
            raise exception.InvalidWidgetDefinition('Missing required tabids')
        super().__init__(*args, **kwargs)

    def setup_tabs(self, *args, **kwargs) -> typing.Mapping[str, model.NotebookTab]:
        '''Define the sub tabs, based on the common tab.

        Do not overwrite this unless you know what you are doing.

        To edit the common tab, see `setup_tab`.
        '''
        assert self.tabids is not None
        tabs = {}
        for tid, tname in self.tabids.items():
            tabs[tid] = Notebook.Tab(tname,
                                     self.setup_tab(tid, tname),
                                     *args, **kwargs)
        return tabs

    def setup_tab(self, identifier: str, name: str) -> mixin.ContainerWidget:
        '''Define the common tab `ContainerWidget` here.

        Similar to `setup_tabs <Notebook.setup_tabs>`, but for a single tab widget.
        '''
        raise NotImplementedError


class Tree(ttk.Treeview, mixin.SingleWidget):
    '''A hierarchical multicolumn data display widget.

    This widget is capable of showing a hierarchy of data records (one per
    row). Each record can have multiple columns of data.
    Each record can store arbitrary data on its `Element <model.TreeElement>`,
    exposed on the `onSelect` function.

    See `Python ttk.Treeview <tkinter.ttk.Treeview>` and ``Tk``
    `ttk.Treeview <https://tcl.tk/man/tcl8.6/TkCmd/ttk_treeview.html>`_
    documentation.

    Args:
        variable: Use an externally defined variable, instead of creating a new
            one specific for this widget.
        label: The heading text for the first column, which includes the labels.
            Supports also a `Column <model.TreeColumn>` object directly.
        columns: Mapping between column identifiers and its titles. Supports
            also a direct map between identifier and `Column <model.TreeColumn>`.
        columns_stretch: Select which columns to stretch, a list of
            identifiers. `None` marks the label column.
            There are also special values:

            - `True` stretches all columns
            - `False` stretches no columns
            - `None` stretches only the label column. This is the default.

            There should be at least one stretchable column, or the container
            is not completely filled with the data. This is checked, but as a
            warning only.
        columns_autosize: Configure column automatic sizing, calling the
            `columns_autosize` function.

            - When `True` (the default), the function is called for all content changes.
            - When `False`, the function is never called automatically.
            - When `None`, there's a small checkbox on the upper right corner
              of the widget that controls if the function is called or not.
        columnConfig: Default configuration for basic string ``columns``
            mapping.
            This also applies to the label column. Advanced usage only.
            Overrides ``columns_stretch``.
        selectable: Should the user be able to select one of the values?
            Defaults to `False`.
        tags: A list of record tags to configure. Optional, will override
            any automatic tags created by the widget itself.
        openlevel: The hierarchy level to open the elements. Defaults to ``1``,
            only the toplevel elements are opened.
            Set to ``0`` to close all, and to a really big number to open all.
        expand: Grow the widget to match the container grid size. This is
            usually supported for containers, but it is included here.
        style: Configure the widget style.

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.

    See Also:
        `Listbox`: Simplified version of this
    '''
    # TODO: Move Tree* classes here?
    Element = model.TreeElement  # Alias the tree element information
    Column = model.TreeColumn  # Alias the tree column configurator

    class __w_autosize(Checkbox):
        isAuto = None  # Isolate from GUI state, taken care in `set_gui_state`

    @dataclass
    class Style(model.WStyle):
        '''`Tree` style object.

        These are the style configurations:

        Args:
            show_headings: Show column title headings.
            show_labels: Show the first column, which includes the labels.
            altbg: Show alternate backgrounds for each record.
            altbg_sindex: ``altbg`` initial alternate colour index.
            autosize_label: Label for the ``columns_autosize`` state checkbox.
            autosize_lcolumn_lspace: Spacing for each level indentation (parent items).
            autosize_lcolumn_osize: Width of the ``[+]`` button on each item.
            autosize_heading_multiplier: Multiplier to the regular label size,
                since this is a boldface. Use ``0`` if you want to ignore the
                heading label when automatically resizing.

        These are the colours:

        Args:
            colour_altbg: ``altbg`` alternate line colour.
                Used as the background colour.
        '''
        show_headings: bool = True
        show_labels: bool = True
        altbg: bool = True
        altbg_sindex: typing.Literal[0, 1] = 1
        # Colours
        colour_altbg: str = 'lightgrey'
        # AutoSize
        autosize_label: str = 'AutoSize'
        autosize_lcolumn_lspace: int = 20
        autosize_lcolumn_osize: int = 20
        autosize_heading_multiplier: int = 6

        def __post_init__(self):
            assert self.autosize_lcolumn_lspace >= 0
            assert self.autosize_lcolumn_osize >= 0
            assert self.autosize_heading_multiplier >= 0

    state_type = varTree
    __lines_alt: str = '__:lines-alt'

    lcolumn: model.TreeColumn
    '''The label `Column <model.TreeColumn>` object.'''
    wcolumns: typing.Mapping[str, model.TreeColumn]
    '''Map principal column identifiers to `Column <model.TreeColumn>` objects.

    See Also:
        `lcolumn` has the label column.
        `wcol` can map all the columns (including label column) and more.
    '''
    wdata: typing.MutableMapping[str, typing.Any]

    def __init__(self, parent: mixin.ContainerWidget, *,
                 variable: typing.Optional[varTree] = None,
                 label: typing.Union[model.TreeColumn, str, None],
                 columns: typing.Mapping[str, typing.Union[model.TreeColumn, str]],
                 columns_stretch: typing.Union[None, bool, typing.Sequence[typing.Union[str, None]]] = None,
                 columns_autosize: typing.Optional[bool] = True,
                 columnConfig: typing.Optional[typing.Mapping[str, typing.Any]] = None,
                 selectable: bool = False,
                 tags: typing.Sequence[str] = typing.cast(typing.Sequence[str], set()),
                 openlevel: int = 1,
                 expand: bool = True,
                 style: Style = Style(_default=True),
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        columnConfig = columnConfig or {}
        self.wstyle = style
        if 'stretch' in columnConfig:  # Overriden manually, don't touch
            warnings.warn('Settings Override: "columnConfig" "stretch" overrides "columns_stretch"', stacklevel=2)
            columns_stretch = []
        if columns_stretch is False:  # Special Setting: No columns
            columns_stretch = []
        elif columns_stretch is True:  # Special Setting: All the columns
            columns_stretch = [None, *columns.keys()]
        elif columns_stretch is None:  # Special Setting: Only the label column
            columns_stretch = [None]
        else:
            if __debug__:
                if isinstance(columns_stretch, typing.Sequence) and len(columns_stretch) == 0:
                    warnings.warn('Stretch some columns, or the container is not fully filled', stacklevel=2)
                if columns_autosize in [True, None] and len(columns_stretch) == len(columns) + 1:
                    warnings.warn('Stretching all columns means autosize does not work well', stacklevel=2)
                if columns_autosize in [True, None] and (len(columns) + (0 if label is None else 1)) == 1:
                    warnings.warn('AutoSize for a single column is unnecessary', stacklevel=2)
        assert all(c is None or isinstance(c, str) for c in columns_stretch), f'Invalid Columns Stretch: "{columns_stretch}"'
        if __debug__:
            for k in ('identifier', 'name'):
                assert k not in columnConfig, f'{self!r}: Invalid Column Config Key "{k}"'
        wcolumns = {}
        for cid, cobj in columns.items():
            if isinstance(cobj, model.TreeColumn):
                ccol = cobj
                cobj.identifier = cid
            elif isinstance(cobj, str):
                ccol = model.TreeColumn(
                    identifier=cid,
                    name=cobj,
                    **columnConfig,
                )
            else:
                raise exception.InvalidWidgetDefinition(f'Invalid column "{cid}": {cobj!r}')
            if ccol.identifier is None:
                raise exception.InvalidWidgetDefinition(f'Missing column id: "{cid}"')
            if len(columns_stretch) > 0:  # Override stretch value
                ccol.stretch = cid in columns_stretch
            wcolumns[cid] = ccol
        self._var_autosize: typing.Optional[var.Boolean] = None
        self.wcolumns = wcolumns
        if isinstance(label, model.TreeColumn):
            self.lcolumn = label
            self.lcolumn.identifier = '#0'
        else:
            self.lcolumn = model.TreeColumn(
                identifier='#0',
                name=label or '',
                **columnConfig,
            )
        if len(columns_stretch) > 0:  # Override stretch value
            self.lcolumn.stretch = None in columns_stretch
        if columns_autosize is None and tk.W in self.lcolumn.nameAnchor.value:
            warnings.warn('AutoSize: Make sure the label anchor is not on the CP.W side', stacklevel=2)
        wshow = []
        if self.wstyle.show_headings:
            wshow.append('headings')
        if self.wstyle.show_labels:
            wshow.append('tree')
        # Initialise Variable and Data
        self.init_single(variable)
        kwargs.update({
            'show': wshow,  # Override the given `show` argument
            'selectmode': tk.BROWSE if selectable else tk.NONE,
            'columns': list(self.wcolumns.keys()),
            'style': parent.wroot.register_styleID(styleID, 'Treeview'),  # Also: Heading Item Tree
        })
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, **kwargs)
        self.wdata = {}
        # Pre-Reserve some tag names
        for tag in tags:
            self.tag_configure(tag)
        # Selection
        if selectable:
            self.binding('<<TreeviewSelect>>', self._onSelect)
            # Disable Double-Click event, when selectable
            self.binding('<Double-Button-1>', fn.binding_disable)
        # Appearance
        if expand:
            self.grid(sticky=tk.NSEW)
        self.openlevel: int = openlevel  # TODO: Support opening all levels, explicit?
        # # Headers
        for wcol in [self.lcolumn, *self.wcolumns.values()]:
            assert wcol.identifier is not None, f'{wcol!r}: Missing identifier'
            # TODO: Migrate "image" support to the tags
            self.heading(wcol.identifier, text=wcol.name, image=wcol.image or '', anchor=wcol.nameAnchor.value,
                         command=self.__tree_header_click(wcol.identifier))
            self.column(wcol.identifier, anchor=wcol.cellAnchor.value, stretch=wcol.stretch)
        self.__autosize: typing.Optional[model.TimeoutIdle] = None
        if columns_autosize in [True, None]:
            self.__autosize = self.tidle(self.columns_autosize)
            self.binding('<Double-Button-1>', self.__tree_header_autoresize, key='__:autoresize:dbl_left')
            self.binding('<Button-2>', self.__tree_header_autoresize, key='__:autoresize:middle')  # Middle Mouse Button
            # Control Widget
            self._var_autosize = var.Boolean()
            if columns_autosize is None:
                # Pretend "self" is a ContainerWidget
                # This works due to the `place` usage, I think.
                wautosize_parent = typing.cast(mixin.ContainerWidget, self)
                wautosize = self.__class__.__w_autosize(wautosize_parent, variable=self._var_autosize,
                                                        label=self.wstyle.autosize_label,
                                                        takefocus=False)
                wautosize.place(anchor=tk.NW, relx=0, rely=0,  # Top Right (NW)
                                x=2, y=2,  # Delta (x Left, y Down)
                                height=18)   # Force Height
                wautosize.wparent = wautosize_parent  # Pretend "self" is a ContainerWidget
            self._var_autosize.set(True)  # Default autosize state
        # # Alternate Backgrounds
        if self.wstyle.altbg:
            self.tag_configure(Tree.__lines_alt, background=self.wstyle.colour_altbg)
            # Minor issue: There is a nearly impercetible flash of badness with
            # `TimeoutIdle` that doesn't happen when calling the function
            # directly.
            # Possible fix: in `__tree_lsvisible`, pass an optional
            # `self.focus()` ID (when != '') and open/close state, that
            # replaces `wopen`.
            altbg = self.tidle(self.__tree_altbg, key='altbg')
            self.binding('<<TreeviewOpen>>', altbg.reschedule, key='__:altbg:open')
            self.binding('<<TreeviewClose>>', altbg.reschedule, key='__:altbg:close')
        # Trace variable state
        self.__gui_changed: bool = False  # Mark the GUI as changed already
        self.trace(self.__tree_set, trace_name=f'__:{__name__}')

    def _tree_get(self, variable: var.Variable) -> typing.Sequence[model.TreeElement]:
        '''Generate a `varTree` object, based on the variable.

        Should be reimplemented by subclasses that change the variable type.
        '''
        assert isinstance(variable, varTree)
        return variable.get()

    def __tree_lslevel(self, parent: typing.Optional[str] = None, _level: int = 0) -> typing.Iterable[typing.Tuple[str, int]]:
        '''Generate a list all widget ids and its corresponding tree level, in GUI order.

        The toplevel has level ``0``.

        See Also:
            `__tree_ls`: Generate a list of all widgets only, without the tree level.
            `__tree_lsvisible`: Generate a list of all visible widgets.
        '''
        for wtop in self.get_children(item=parent):
            yield wtop, _level
            yield from self.__tree_lslevel(parent=wtop, _level=_level + 1)

    def __tree_ls(self, parent: typing.Optional[str] = None) -> typing.Iterable[str]:
        '''Generate a list all widget ids, in GUI order.

        See Also:
            `__tree_lslevel`: Generate a list of all widgets and its tree level.
            `__tree_lsvisible`: Generate a list of all visible widgets.
        '''
        for wtop, _ in self.__tree_lslevel(parent):
            yield wtop

    def __tree_lsvisible(self, parent: typing.Optional[str] = None, _kids=None) -> typing.Iterable[str]:
        '''Generate a list of all visible widget ids, in GUI order.

        This guarantees the yielded values are visible to the user, as long as
        the tree is stable.

        See Also:
            `__tree_ls`: Generate a list of all widgets, even the not currently shown.
            `__tree_lslevel`: Generate a list of all widgets and its tree level.

        Note:
            When called directly from the ``<<TreeviewOpen>>`` or
            ``<<TreeviewClose>>`` event, this will "fail", that event runs too
            early. Use a `model.TimeoutIdle` in there to get the correct
            results.
        '''
        for wtop in _kids or self.get_children(item=parent):
            yield wtop
            wopen = self.item(wtop, option='open') == 1
            wkids = self.get_children(item=wtop)
            if len(wkids) > 0 and wopen:
                yield from self.__tree_lsvisible(parent=wtop, _kids=wkids)

    def __tree_clean(self, parent=None) -> None:
        self.delete(*self.__tree_ls(parent=parent))
        self.wdata.clear()

    def __tree_put(self, elements: typing.Sequence[model.TreeElement], *,
                   parent: typing.Optional[str] = None,
                   openlevel: typing.Optional[int] = None, _level: int = 0):
        parent_loc: typing.Optional[int] = None if parent is None else self.index(parent)
        openlevel = openlevel or self.openlevel
        for eid, element in enumerate(elements):
            # if __debug__:
            #     tpl_text = f'{parent or "__top__"}::#{eid}'
            #     logger.debug(f'{">" * (_level + 1)} {tpl_text}: L:"{element.label}" C:|{" ".join(element.columns)}|')
            if element.columns is not None:
                # TODO: Support a dict with keys corresponding to the `self.wcolumns`, possible subset
                assert len(element.columns) == len(self.wcolumns), f'Invalid Column #{eid}: Size: E{len(element.columns)} W{len(self.wcolumns)}'
            child_loc: typing.Union[int, typing.Literal['end']]
            if parent_loc is None:
                child_loc = tk.END
            else:
                child_loc = parent_loc + eid
            cid = self.insert(parent or '', child_loc,
                              text=element.label, values=tuple(element.columns or []),
                              open=_level < openlevel,
                              image=element.image or '',
                              tags=list(element.tags or []),
                              )
            self.wdata[cid] = element.data
            # if __debug__:
            #     logger.debug(f'{"|" * (_level + 1)} ID: {cid}')
            if element.children:
                # if __debug__:
                #     logger.debug(f'{"|" * (_level + 1)} Children: {len(element.children)}')
                self.__tree_put(element.children,
                                parent=cid,
                                openlevel=openlevel, _level=_level + 1)

    def __tree_set(self, *args, **kwargs) -> None:
        assert self.variable is not None, f'{self!r}: Missing variable'
        value = self._tree_get(self.variable)
        if self.__gui_changed:
            # if __debug__:
            #     logger.debug(f'{self}:   Keep GUI state')
            self.__gui_changed = False
        else:
            # if __debug__:
            #     logger.debug(f'{self}: Change GUI state')
            self.__tree_clean()
            self.__tree_put(value)
        if self.wstyle.altbg:
            self._tidles['altbg'].schedule()
        if self._var_autosize and self._var_autosize.get() is True:
            assert self.__autosize is not None
            self.__autosize.schedule()
        self._tree_onset(value)

    def __tree_header_click(self, cid: str):
        # Search column by cid, or else it's the label column
        return lambda: self.onClickHeader(self.wcolumns.get(cid, self.lcolumn))

    def __tree_header_autoresize(self, event):
        # self.identify_region(event.x, event.y)  # Alternative, only for tk8.6
        if self.identify('region', event.x, event.y) != 'separator':
            return
        asizes = self.__columns_autosize()
        if event.num == 2:  # Check if it's Middle Mouse Button
            # if __debug__:
            #     logger.debug('Resize All Columns')
            self.columns_size(asizes)
        else:
            # wcol = self.wcol(self.identify_column(event.x, event.y))  # Alternative, only for tk8.6
            wcol = self.wcol(self.identify('column', event.x, event.y))
            # if __debug__:
            #     logger.debug(f'Column: {wcol}')
            if not wcol.stretch:
                self.columns_size({wcol.identifier: asizes[wcol.identifier]})

    def __columns_autosize(self) -> typing.Mapping[str, int]:
        cols = {wcol.identifier: wcol for wcol in [self.lcolumn, *self.wcolumns.values()]}
        assert None not in cols
        # widths: Only the non-stretched("fixed") columns
        widths: typing.MutableMapping[str, int] = {cid: 0 for cid, wcol in cols.items() if cid and not wcol.stretch}
        if len(widths) == 0:
            # if __debug__:
            #     logger.debug('Nothing to Calculate')
            return {}
        # if __debug__:
        #     logger.debug('AutoSize Columns: %s', ' '.join(widths))
        cid: typing.Optional[str]
        for iid, ilevel in self.__tree_lslevel():
            item = self.item(iid)
            # if __debug__:
            #     logger.debug('| %5s | %r', iid, item)  # 5 should enough for the auto-generated ID
            # Label Column
            cid = '#0'
            if cid in widths:
                lsize = fn.label_size(len(str(item['text'])))  # Label Size
                psize = self.wstyle.autosize_lcolumn_lspace * (ilevel + 1)
                isize = 0 if item['image'] == '' else 16  # TODO: Calculate the image width, from the ID
                widths[cid] = max(widths[cid], lsize + psize + isize)
                # if __debug__:
                #     logger.debug('  %5s | %s | %d+%d+%d = %d', 'LPI', '#0', lsize, psize, isize, widths[cid])
            # Other Columns
            for cid, cval in zip(self.wcolumns, item['values']):
                if cid in widths:
                    lsize = fn.label_size(len(str(cval)))  # Label Size
                    widths[cid] = max(widths[cid], lsize)
                    # if __debug__:
                    #     logger.debug('  %5s | %s | %d = %d', 'L', cid, lsize, widths[cid])
        # logger.debug('AutoSize Delta Values')
        for cid in widths:
            assert cid is not None
            wcol = cols[cid]
            lsize = fn.label_size(len(wcol.name)) * self.wstyle.autosize_heading_multiplier  # Bold
            psize = self.wstyle.autosize_lcolumn_osize if wcol.identifier == '#0' else 0
            isize = wcol.image.width() if wcol.image else 0
            # if __debug__:
            #     logger.debug('  %s | %d + %d+%d+%d', cid, widths[cid], lsize, psize, isize)
            widths[cid] += lsize + psize + isize
        return widths

    def columns_size(self, widths: typing.Mapping[str, int]) -> None:
        '''Set the column widths.

        Args:
            widths: Mapping between column identifiers and column ``width``.
        '''
        assert all(cid in self.wcolumns or cid == '#0' for cid in widths)
        # logger.debug('Set Widths:')
        for cid, cwidth in widths.items():
            # logger.debug('> %s | %d', cid, cwidth)
            self.column(cid, width=cwidth)

    def columns_autosize(self) -> None:
        '''Automatically set the column widths.

        Uses heristics to find the "natural" column widths, it might not work
        perfectly.
        '''
        self.columns_size(self.__columns_autosize())

    def element_move(self, wid: str, newindex: int) -> bool:
        '''Move element on the `Tree` without recreating the state.

        This is a `wstate` alternative, for moving an existing element without
        having to regenerate the entire state. This has much better performance
        characteristics, particularly for big trees.

        For now this does not support any children elements anywhere.
        Everything must remain on the toplevel level.

        Returns:
            `True` when the state is effectively changed, `False` otherwise.
            The reasons for not changing the state might be a no-op (the
            current and the new indexes are the same), or an invalid operation
            (moving an element outside the range).

        See Also:
            You can get the selected element using `wsid`.
        '''
        pid = ''  # Only for the toplevel elements
        oldindex = self.index(wid)
        assert wid in self.wdata, f'{self}: Missing element "{wid}"'
        if __debug__:
            old_pid = self.parent(wid)
            assert old_pid == pid, f'{self}: Element "{wid}" child of "{old_pid}"'
            assert len(self.get_children(item=wid)) == 0, f'{self}: Element "{wid}" has children'
        if oldindex == newindex:
            return False  # No-Op
        if newindex < 0 or newindex >= len(self.wdata):
            return False  # Outside the range
        if __debug__:
            new_id = self.get_children(item=pid)[newindex]
            new_pid = self.parent(new_id)
            assert new_pid == pid, f'{self}: Moving "{wid}" into the middle of children ("{newindex}")'
        # Calculate Variable State
        state = self.wstate
        state[oldindex], state[newindex] = state[newindex], state[oldindex]
        # Change the GUI State
        self.move(wid, pid, newindex)
        # Change the Variable State (no GUI changes)
        self.__gui_changed = True
        self.wstate = state
        return True

    def __tree_altbg(self, *, remove: bool = False) -> None:
        '''Setup the alternate background, based on tags.

        Args:
            remove: Force removing all the backgrounds
        '''
        tname = Tree.__lines_alt
        index: int = self.wstyle.altbg_sindex
        for rid in self.__tree_lsvisible():
            tags = list(self.item(rid, option='tags'))
            dotags = False
            if not remove and index % 2 == 0:
                if tname not in tags:
                    tags.insert(0, tname)  # Prepend
                    dotags = True
            else:
                try:
                    tags.remove(tname)
                    dotags = True
                except ValueError:
                    pass  # Tag doesn't exist, skip
            if dotags:
                self.item(rid, tags=tags)
            index += 1
        # if __debug__:
        #     # This should run only once, even with multiple changes
        #     if index > self.wstyle.altbg_sindex:
        #         logger.debug(f'{self}: Calculated AltBG')

    def wcol(self, identifier: str) -> model.TreeColumn:
        '''Get the `Column <model.TreeColumn>` corresponding to the given identifier.

        The identifier can be one of the following formats:

        - ``#0``: The label column
        - Any of the `wcolumns` keys: The corresponding column
        - ``#n`` for any numeric ``n``: The index (starts on 1) for the visible column.

        Note:
            There is no support for the visible columns being different from
            the data columns, so ``#n`` always refers to the index into
            `wcolumns`.

        There is no Python documentation, see ``Tk`` `Treeview column
        identifiers <https://tcl.tk/man/tcl8.6/TkCmd/ttk_treeview.htm#M77>`_
        documentation.

        Args:
            identifier: The column identifier.
                See above for all the possible formats.
        '''
        if identifier == '#0':
            column = self.lcolumn
        elif identifier in self.wcolumns:
            column = self.wcolumns[identifier]
        elif identifier.startswith('#'):  # This is an index into the "displaycolumns"
            # TODO: Suport display columns? This is technically wrong for now
            int_id = int(identifier[1:]) - 1  # Starts on 1
            assert int_id >= 0 and int_id < len(self.wcolumns)
            column = list(self.wcolumns.values())[int_id]
        else:
            raise ValueError(f'Unsupported ID: "{identifier}"')
        return column

    def wsid(self) -> typing.Optional[str]:
        '''Get the selected element identifier.

        Returns:
            `Element <model.TreeElement>` id, or `None` when nothing is selected.

            If the widget was created without the ``selectable`` flag, this always
            returns `None`.

        See Also:
            Use `wsel` to set the currently selected element identifier.
        '''
        selection = self.selection()
        if __debug__:
            selectmode = str(self['selectmode'])
            assert selectmode in [tk.BROWSE, tk.NONE], f'{self!r}: Invalid Selection Mode: {selectmode}'
            # logger.debug('Selection: %r', selection)
        if len(selection) == 0:
            # Skip un-selections
            # Usually the Tree contents changed...
            return None
        else:
            # Regular Selection
            assert len(selection) == 1, f'{self!r}: Invalid selection mode'
            treeid = selection[0]
            return treeid

    def wsel(self, wid: typing.Optional[str], *, see: bool = True) -> typing.Optional[str]:
        '''Set the currently selected element identifier.

        Defaults to ensuring the selected element, by scrolling the view. This
        is controlled by the ``see`` argument.

        Args:
            wid: The element identifier to select. `None` to clear the
                selection.
            see: Ensure the element is visible.

        Returns:
            Return the source ``wid`` argument.

        See Also:
            Use `wsid` to get the currently selected data.
        '''
        if wid is None:
            # Clear selection
            self.selection_remove(*self.wdata.keys())
        else:
            assert wid in self.wdata, f'{self}: Missing element "{wid}"'
            self.selection_set(wid)
            if see:
                self.see(wid)
        return wid

    def wselection(self) -> typing.Optional[typing.Any]:
        '''Get the selected data.

        Returns:
            Since this supports only a single selection, return the selected
            value, or ``None`` when nothing is selected.

            If the widget was created without the ``selectable`` flag, this always
            returns `None`.

        See Also:
            Use `wselect` to set the currently selected data.
        '''
        wsid = self.wsid()
        return self.wdata[wsid] if wsid else None

    def wselect(self, selection: typing.Optional[typing.Any], *, see: bool = True) -> typing.Optional[str]:
        '''Set the current selection data.

        This will select the element with the given data. This will need to
        read the whole data, and does not support multiple elements with the
        same data. Avoid using this unless absolutely needed, use `wsel`
        directly.

        Args:
            selection: The element data to select. `None` clears the selection.
            see: Ensure the element is visible.

        Returns:
            Return the selected element identifier.

        See Also:
            Use `wsel` to select a specific identifier.
            Use `wselection` to get the currently selected data.
        '''
        if selection is None:
            wsid = None
        else:
            wsids = [wsid for wsid in self.__tree_ls() if self.wdata[wsid] == selection]
            assert len(wsids) > 0, f'{self}: Missing selection "{selection}'
            assert len(wsids) == 1, f'{self}: Multiple selections "{selection}" > {wsids}'
            wsid = wsids[0]
        return self.wsel(wsid, see=see)

    def _onSelect(self, event=None) -> None:
        ''''''  # Internal, do not document
        selection: tuple = self.selection()
        if __debug__:
            selectmode = str(self['selectmode'])
            assert selectmode in [tk.BROWSE, tk.NONE], f'{self!r}: Invalid Selection Mode: {selectmode}'
            # logger.debug('Selection: %r', self.selection())
        if len(selection) == 0:
            # Skip
            # - NONE selectmode
            # - un-selections (usually the Tree contents changed)
            pass
        else:
            # Regular Selection
            assert len(selection) == 1, f'{self!r}: Invalid selection mode'
            treeid = selection[0]
            data = self.wdata[treeid]
            self.onSelect(treeid, data)

    def _tree_onset(self, value: typing.Sequence[model.TreeElement]) -> None:
        '''Callback to be executed when setting a different value.

        Available for subclass redefinition.
        '''
        pass

    def onClickHeader(self, column: model.TreeColumn):
        '''Callback to be executed when clicking any header.

        Defaults to doing nothing.

        Available for subclass redefinition.

        Args:
            column: The `Column <model.TreeColumn>` object
        '''
        pass

    def onSelect(self, treeid: str, data: typing.Any = None) -> None:
        '''Callback to be executed when clicking this widget.

        Defaults to doing nothing.

        Available for subclass redefinition.

        Args:
            treeid: The selected tree id
            data: The arbitrary data associated with the element. Defaults to `None`.
        '''
        pass


class Listbox(Tree):
    '''A listbox widget, a list of strings.

    This is a modern variation of the listbox, a way to display several rows of
    content (simple strings, in this case), and be able to select one at a
    time.

    The ``height`` can be hardcoded to a value, or it can vary with the
    contents. Note that the ``maxHeight`` is smaller than the amount of rows to
    display, no scrollbar is shown, but the list can be
    scrolled with the mouse wheel.
    The automatic variation on the height size (AKA auto-height) can be
    completely disabled by setting all height-related arguments to `None`. This
    is the default. The ``expand`` argument is set to `False` when the
    auto-height is disabled.

    Each string is centered on the list. This can be tweaked using the
    ``columnConfig`` argument.

    The state is a `list` of `str` values, `var.StringList`.

    This is a variation on the `Tree` widget, with a single column, a different
    variable type and some overriden default values.
    See also `Python ttk.Treeview <tkinter.ttk.Treeview>` and ``Tk``
    `ttk.Treeview <https://tcl.tk/man/tcl8.6/TkCmd/ttk_treeview.html>`_
    documentation.

    Args:
        variable: Use an externally defined variable, instead of creating a new
            one specific for this widget.
        label: The label to include besides the listbox. Can be given as a
            class variable.
            Optional, when given is show as the single column heading.
        columnConfig: Override configuration for the single column. Advanced
            usage only.
        height: If given, always show this quantity of rows.
            If it is `None`, the number of permanently shown rows will vary between
            ``minHeight`` and ``maxHeight``.
        minHeight: If ``height`` is `None`, make sure this number of rows is
            always visible.
            Optional, when `None`, there's no lower limit on the visible number
            of rows.
        maxHeight: If ``height`` is `None`, make sure there are no more
            visible rows than this number.
            Optional, when `None`, there's no upper limit on the visible
            number of rows.
        selectable: See `Tree` for its meaning.
            Defaults to `True`.
        style_altbg: See `Tree` for its meaning.
            Defaults to `False`.
        expand: See `Tree` for its meaning.
            Defaults to `False`, but interacts with the auto-height settings.
        style: Configure the widget style.

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.
    '''
    label: typing.Optional[str] = None

    @dataclass
    class Style(Tree.Style):
        '''`Listbox` style object.

        See `Tree.Style` for upstream values, these are the differences:

        Args:
            altbg: Disabled by default.
            show_labels: Unsupported.
        '''
        altbg: bool = False
        show_labels: bool = False

        if __debug__:
            def __post_init__(self):
                if self.show_labels:
                    warnings.warn(f'{self}: Unsupported "show_labels"', stacklevel=3)
                self.show_labels = False

    state_type = var.StringList  # type: ignore  # Change the variable type

    def __init__(self, *args, variable: typing.Optional[var.StringList] = None,
                 label: typing.Optional[str] = None,
                 columnConfig: typing.Optional[typing.Mapping[str, typing.Any]] = None,
                 height: typing.Optional[int] = None, minHeight: typing.Optional[int] = None, maxHeight: typing.Optional[int] = None,
                 selectable: bool = True, expand: typing.Optional[bool] = None,  # Override
                 style: Style = Style(_default=True),
                 **kwargs):
        chosen_label = self.label or label
        if style._default:
            style.show_headings = chosen_label is not None
        kwargs.update({
            'label': chosen_label,
            'variable': variable,
            'selectable': selectable,  # Override
            'columns': {'label': chosen_label or 'Label'},  # Single Column "label"
            'style': style,
            'columns_autosize': False,  # Single Column
        })
        # Configure height
        self.heightRange: typing.Optional[typing.Tuple[typing.Optional[int], typing.Optional[int]]]
        if height is None:
            self.heightRange = minHeight, maxHeight
        else:
            kwargs['height'] = height  # Hardcode the height value
            self.heightRange = None
        if height or minHeight or maxHeight and expand is None:
            # Don't expand when the fixed or varying height is set
            expand = False
        # Configure (single) column
        # - Don't use `#0` since that is not properly centered, it has the tree
        #   elements in there, even hidden.
        cConfig = {
            'anchor': tk.CENTER,
            'stretch': True,
        }
        if expand is not None:
            kwargs['expand'] = expand
        if columnConfig:
            cConfig.update(columnConfig)
        super().__init__(*args, **kwargs)
        # Make sure cConfig keys match options for `tkinter.ttk.Treeview.column`
        self.column('label', **cConfig)  # type: ignore

    def _tree_get(self, variable: var.Variable) -> typing.Sequence[model.TreeElement]:
        return [model.TreeElement(label=e, columns=[e], data=e) for e in variable.get()]

    def _tree_onset(self, value: typing.Sequence[model.TreeElement]) -> None:
        if self.heightRange is not None:
            minHeight, maxHeight = self.heightRange
            wsize = None
            if minHeight:
                wsize = max(minHeight, len(value))
            if maxHeight:
                wsize = min(maxHeight, wsize or len(value))
            if wsize:
                if __debug__:
                    logger.debug(f'{self}: Auto Height: {wsize}')
                self.configure(height=wsize)


class FramePaned(ttk.PanedWindow, mixin.ContainerWidget):
    '''A frame to hold other widgets, with user-controllable relative sizes.

    This is similar to a `FrameUnlabelled`, restricted to horizontal or
    vertical layouts, but where the interfaces between the children can be
    adjusted by the user, to resize them at will.

    This allows some child widgets to be hidden, by resizing the other panes to
    fully occupy the widget area.

    Note that using this with more than two children can be confusing for the
    users, particularly when resizing takes place.

    There is no Python documentation, see ``Tk`` `ttk.PanedWindow <https://www.tcl.tk/man/tcl/TkCmd/ttk_panedwindow.html>`_ documentation.

    Args:
        layout: The orientation of the child widgets.
            Restricted to ``tk.VERTICAL`` or ``tk.HORIZONTAL``.
        orient: Alias for "layout".
        weight: The weight for each children widget. Optional, defaults to 1.
        weights: Per-child widget. Optional, defaults to the common "weight".

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.

    Note:
        The ``layout``/``orient`` argument has similar semantics to ``layout``
        argument on other frame types.

    See Also:
        - `FrameUnlabelled`, `FrameLabelled`: Similar versions, without user
          control over sizing.
    '''
    layout: typing.Optional[str] = None

    def __init__(self, parent: mixin.ContainerWidget,
                 *args,
                 orient: typing.Optional[typing.Union[typing.Literal['vertical'], typing.Literal['horizontal']]] = None,
                 weight: typing.Optional[int] = None,
                 weights: typing.Optional[typing.Mapping[str, int]] = None,
                 styleID: typing.Optional[str] = None,
                 **kwargs):
        # Orientation can be given as the layout
        # But the ContainerWidget layout is always None
        # No Default Orientation, must be given somewhere
        orientation = kwargs.pop('layout', None) or orient or self.layout
        assert orientation in [tk.VERTICAL, tk.HORIZONTAL], f'Invalid Orientation: {orientation}'
        if typing.TYPE_CHECKING:
            orientation = typing.cast(typing.Union[typing.Literal['vertical'], typing.Literal['horizontal']], orientation)
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, orient=orientation,
                         style=parent.wroot.register_styleID(styleID, 'TPanedwindow')  # Also: Sash
                         )  # ttk.PanedWindow
        self.init_container(*args, layout=None, **kwargs)
        for wname, raw_widget in self.widgets.items():
            widget = raw_widget.wproxy or raw_widget  # Use the proxy widget, if applies
            # Widget Weight: Default to 1
            wweight = weight or 1
            if weights:
                # Per-Widget Override
                wweight = weights.get(wname, wweight)
            assert isinstance(widget, tk.Widget)
            self.add(widget,
                     weight=wweight)
        assert len(self.panes()) == len(self.widgets)


class ScrolledWidget(ttk.Frame, mixin.ProxyWidget):
    '''A proxy widget to include functional scrollbars.

    This is a proxy frame, with a single child widget, which includes
    functional scrollbars. Both horizontal and vertical scrollbars are
    supported (depending on the child widget).

    A corner widget to hide the "blank" space between scrollbars is
    automatically included if needed, this is implemented as a so-called
    "sizegrip".

    There is no Python documentation, see ``Tk``
    `ttk.Scrollbar <https://www.tcl.tk/man/tcl/TkCmd/ttk_scrollbar.html>`_ and
    `ttk.Sizegrip <https://www.tcl.tk/man/tcl/TkCmd/ttk_sizegrip.html>`_ documentation.

    The scrollbars can be forced to be shown, or they can be configured in
    automatic mode, independenty. This will show or hide the scrollbars as
    needed. This amounts to hide them when the child widget needs no
    scrollbars. The default behaviour is this automatic showing/hiding for both
    scrollbars.

    Note:
        Like any `ProxyWidget`, creating an instance of this type will return a
        ``childClass`` instance.

        If you want to access the functions defined in this class, you need to
        use the `wproxy <mixin.MixinWidget.wproxy>` reference.
        See also the `proxee <mixin.MixinWidget.proxee>` reference to get a
        reference to the child widget from the proxy.

    Args:
        childClass: The children class (called to create the child widget).
            Must be a `SingleWidget`.
        scrollVertical: Show the vertical scrollbar.
            Use a `bool` to force a state, or `None` to automatically show or hide the scrollbar.
            Defaults to `None`.
        scrollHorizontal: Include a horizontal scrollbar.
            Use a `bool` to force a state, or `None` to automatically show or hide the scrollbar.
            Defaults to `None`.
        scrollExpand: Expand the parent widget.
            This is analogous to the ``expand`` argument on
            `mixin.ContainerWidget.init_container`.

        styleID: Set a style identifier. Combined with the widget type in `RootWindow.register_styleID`.
        parent: The parent widget. Can be a `RootWindow` or another `mixin.ContainerWidget`.

    All other arguments are passed to the children ``childClass`` invocation.

    See Also:
        There is some anciliary Python documentation in `scrollable widget
        options
        <https://docs.python.org/3.8/library/tkinter.ttk.html#scrollable-widget-options>`_.

    ..
        Python 3.8 is missing this reference, included in Python 3.9:

        :ref:`scrollable widget options <python:Scrollable-Widget-Options>`
    '''
    def __init__(self, parent: mixin.ContainerWidget, childClass: typing.Type[mixin.SingleWidget],
                 *args,
                 scrollVertical: typing.Optional[bool] = None,
                 scrollHorizontal: typing.Optional[bool] = None,
                 scrollExpand: bool = True,
                 styleID: typing.Optional[str] = None,
                 **ckwargs):
        assert childClass is not ScrolledWidget, f'{parent}: Do not nest ScrolledWidget'

        # Current Frame
        assert isinstance(parent, tk.Misc), f'{parent} is not a valid parent widget'
        super().__init__(parent, style=parent.wroot.register_styleID(styleID, 'TFrame'))  # ttk.Frame
        rweight = [1]
        cweight = [1]

        type_scrollGenCommand = typing.Callable[[float, float], None]

        # Widget Helpers
        def scrollGenCommand(fn: type_scrollGenCommand, why: typing.Optional[bool], what: str) -> type_scrollGenCommand:
            if why:
                # Force Enable, don't change the state
                return fn
            else:
                # Automatic, change the state as needed
                @wraps(fn)
                def scrollGenCommand(sposs: float, eposs: float) -> None:
                    # Defensive Programming, for older versions (make REALLY sure those are floats)
                    spos: float = float(sposs)
                    epos: float = float(eposs)
                    allvisible: bool = spos == 0.0 and epos == 1.0
                    # if __debug__:
                    #     logger.debug('ScrollCommand[%s]: [%f , %f] = %s', what, spos, epos, allvisible)
                    self.set_scroll_state(**{what: not allvisible})
                    return fn(spos, epos)
                return scrollGenCommand

        # Widgets
        self.__vbar: typing.Optional[ttk.Scrollbar] = None
        self.__hbar: typing.Optional[ttk.Scrollbar] = None
        self.__corner: typing.Optional[ttk.Sizegrip] = None
        if scrollHorizontal in (None, True):
            self.__hbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
            ckwargs['xscrollcommand'] = scrollGenCommand(self.__hbar.set, scrollHorizontal, 'hstate')
            cweight.append(0)
        if scrollVertical in (None, True):
            self.__vbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
            ckwargs['yscrollcommand'] = scrollGenCommand(self.__vbar.set, scrollVertical, 'vstate')
            rweight.append(0)
        if scrollVertical in (None, True) and scrollVertical in (None, True):
            # This is not stricly necessary, but nice to have.
            self.__corner = ttk.Sizegrip(self, cursor='', takefocus=False)
            # Disable sizegrip events
            self.__corner.bind('<Button-1>', fn.binding_disable)
        cwidget = childClass(self, *args, **ckwargs)  # type: ignore

        # State
        self.state_type = cwidget.state_type
        self.init_single(cwidget.variable)  # Wrap child widget variable
        # Special Widget state
        self.wparent = parent

        # Glue scrollbars with child widget
        if self.__hbar:
            assert isinstance(cwidget, tk.XView), f'Invalid Child Widget: {cwidget!r}'
            self.__hbar['command'] = cwidget.xview
        if self.__vbar:
            assert isinstance(cwidget, tk.YView), f'Invalid Child Widget: {cwidget!r}'
            self.__vbar['command'] = cwidget.yview

        # Layout
        if scrollExpand:
            self.grid(sticky=tk.NSEW)
        assert isinstance(cwidget, tk.Grid), f'Invalid Child Widget: {cwidget!r}'
        cwidget.grid(row=0, column=0, sticky=tk.NSEW)
        self.set_scroll_state(scrollHorizontal or None, scrollVertical or None)
        # Emulate `fn.configure_grid(self, rweight, cweight)`
        for ridx, weight in enumerate(rweight):
            self.rowconfigure(ridx, weight=weight)
        for cidx, weight in enumerate(cweight):
            self.columnconfigure(cidx, weight=weight)

        # Proxy all access to `cwidget`
        self.proxee = cwidget

    def get_scroll_state(self) -> typing.Tuple[bool, bool]:
        '''Get the current scrollbar visibility state.

        If the scrollbar is completely disabled, `False` is returned.

        This is a tuple with the state for both scrollbars, horizontal and
        vertical.

        See Also:
            - `set_scroll_state`: Change the current state
        '''
        return (
            self.__hbar is not None and bool(self.__hbar.grid_info()),
            self.__vbar is not None and bool(self.__vbar.grid_info()),
        )

    def set_scroll_state(self, hstate: typing.Optional[bool] = None, vstate: typing.Optional[bool] = None) -> None:
        '''Change the current scrollbar visibility state.

        This can change both horizontal and vertical state independently. The
        corner widget is managed automatically.

        Args:
            hstate: If not `None`, set the horizontal scrollbar visibility.
            vstate: If not `None`, set the vertical scrollbar visibility.

        See Also:
            - `get_scroll_state`: Get the current state
        '''
        if hstate is not None and self.__hbar is not None:
            h_wgrid = self.__hbar.grid_info()
            if hstate:
                if not h_wgrid:
                    self.__hbar.grid(row=1, column=0, sticky=tk.EW)
                    # if __debug__:
                    #     logger.debug('%s: Show hbar', self)
            else:
                if h_wgrid:
                    # if __debug__:
                    #     logger.debug('%s: Hide hbar', self)
                    self.__hbar.grid_remove()
        if vstate is not None and self.__vbar is not None:
            v_wgrid = self.__vbar.grid_info()
            if vstate:
                if not v_wgrid:
                    self.__vbar.grid(row=0, column=1, sticky=tk.NS)
                    # if __debug__:
                    #     logger.debug('%s: Show vbar', self)
            else:
                if v_wgrid:
                    # if __debug__:
                    #     logger.debug('%s: Hide vbar', self)
                    self.__vbar.grid_remove()
        if self.__corner is not None:
            isHorizontal = self.__hbar is not None and self.__hbar.grid_info()
            isVertical = self.__vbar is not None and self.__vbar.grid_info()
            c_wgrid = self.__corner.grid_info()
            if isHorizontal and isVertical:
                if not c_wgrid:
                    self.__corner.grid(row=1, column=1)
                    # if __debug__:
                    #     logger.debug('%s: Show corner', self)
            else:
                if c_wgrid:
                    # if __debug__:
                    #     logger.debug('%s: Hide corner', self)
                    self.__corner.grid_remove()

# # Complex Widgets


class ListboxControl(FrameUnlabelled):
    '''A listbox widget, with extra controls for a set of strings.

    This is complex variation on `Listbox`, with extra widgets for manipulating
    the string list. This is useful to manipulate string lists.

    The extra widget controls can be grouped as follows:

    - There is a `ComboboxN` to select the element to add, or another button to
      add all supported elements.
    - There are buttons to remove the currently selected element, or clear all
      elements.
    - There are buttons to manipulate the order of the currently selected
      element, upwards or downwards. Clicking on these buttons with the middle
      mouse button moves the currently selected element to the top or bottom of
      the list.

    All these groups are configurable, see the ``button*`` arguments.

    .. note::
        When ``buttonOne`` is set to `False`, it might be interesting to move
        the button widgets to the right side.
        Set the ``layout`` argument as ``layout='c1,x'`` to achieve this
        configuration.

    Args:
        selAll: Specification for all supported elements.
        selList: Initial selected string list.
        variable: Use an externally defined variable, instead of creating a new
            one specific for this widget. Passed to the `Listbox`.
        label: The heading text for the first column. Optional, passed to the `Listbox`.
        buttonOne: Include buttons for adding a single element, and removing
            the selected element. This controls the `ComboboxN` placement too.
        buttonAll: Include buttons for adding all supported elements and clean
            all elements. Defaults to include.
        buttonOrder: Include buttons to manipulate the order of selected
            element. Defaults to not include.

    See Also:
        The container widget is `FrameUnlabelled`, and the inner widgets are
        `Listbox` (with `ScrolledWidget` handling), `ComboboxN` and `Button`.
    '''
    layout = 'R1,x'
    wstate_single = 'selected'

    # Ignore types, incompatible with `FrameLabelled.setup_widgets`
    def setup_widgets(self,
                      selAll: typing.Union[var.SpecCountable, validation.VSpec],
                      selList: typing.Optional[typing.Iterable[str]] = None,
                      variable: typing.Optional[var.StringList] = None,
                      label: typing.Optional[str] = None,
                      buttonOne: bool = True, buttonAll: bool = True, buttonOrder: bool = False,
                      ) -> None:
        ''''''  # Do not document
        assert any((buttonOne, buttonAll, buttonOrder)), f'{self}: This is just a Listbox'
        self.selected = ScrolledWidget(self, Listbox,
                                       variable=variable, selectable=True, label=label,
                                       scrollHorizontal=False, scrollVertical=None)
        self.rm = Button(self, label='-') if buttonOne else None
        self.rmAll = Button(self, label='---') if buttonAll else None
        self.moveDown = Button(self, label='↓') if buttonOrder else None
        self.all = ComboboxN(self, vspec=selAll) if buttonOne else None
        self.moveUp = Button(self, label='↑') if buttonOrder else None
        self.addAll = Button(self, label='+++') if buttonAll else None
        self.add = Button(self, label='+') if buttonOne else None

        # Events
        if self.rm:
            self.rm.onClick = self.onRemove  # type: ignore
        if self.rmAll:
            self.rmAll.onClick = self.onRemoveAll  # type: ignore
        if self.moveDown:
            self.moveDown.onClick = self.onMoveDown  # type: ignore
            self.moveDown.binding('<ButtonPress-2>', self.onMoveBottom)
        if self.all:
            self.all.binding('<Return>', self.onAdd)
        if self.add:
            self.add.onClick = self.onAdd  # type: ignore
        if self.moveUp:
            self.moveUp.onClick = self.onMoveUp  # type: ignore
            self.moveUp.binding('<ButtonPress-2>', self.onMoveTop)
        if self.addAll:
            self.addAll.onClick = self.onAddAll  # type: ignore

        assert isinstance(self.selected, Listbox)
        # State
        self._all = selAll
        if self.all:
            self.all.ignoreContainerState = True
        if selList:
            selection = list(selList)
            assert all(e in selAll for e in selection), f'Invalid selList: {selList}'
            self.selected.wstate = selection

    def setup_defaults(self):
        # Don't grow any buttons
        if self.rm and self.add:
            self.pgrid(self.rm, self.add,
                       weight=0, uniform='button_small')
        if self.rmAll and self.addAll:
            self.pgrid(self.rmAll, self.addAll,
                       weight=0, uniform='button_big')

    def onAdd(self, event: typing.Any = None) -> None:
        assert self.all, f'{self}: Calling `onAdd` without "buttonOne" argument'
        assert isinstance(self.selected, Listbox)
        assert self.all.wstate.valid
        selection = self.all.wstate.label
        allelements = self.selected.wstate
        if selection not in allelements:
            self.selected.wstate = (*allelements, selection)

    def onAddAll(self, event: typing.Any = None) -> None:
        assert isinstance(self.selected, Listbox)
        # TODO: Keep the existing state, add missing
        self.selected.wstate = self._all.lall()

    def onRemove(self, event: typing.Any = None) -> None:
        assert isinstance(self.selected, Listbox)
        selection = self.selected.wselection()
        if selection:
            allelements = self.selected.wstate
            if selection in allelements:
                self.selected.wstate = (s for s in allelements if s != selection)

    def onRemoveAll(self, event: typing.Any = None) -> None:
        self.selected.wstate = []

    def onMove(self, delta: typing.Union[int, typing.Literal['top'], typing.Literal['bottom']]):
        assert delta != 0
        assert isinstance(self.selected, Listbox)
        swidget = self.selected
        selection = swidget.wselection()
        # TODO: Test this, `tests/test_widget_listbox.py`
        if selection:
            wsid = swidget.wsid()
            if delta == 'top':
                newidx = 0
            elif delta == 'bottom':
                newidx = len(swidget.wstate) - 1
            else:
                oldidx = swidget.index(wsid)
                newidx = oldidx + delta
            if swidget.element_move(wsid, newidx):
                # Re-Select the old element
                swidget.wsel(wsid)

    def onMoveUp(self, event=None):
        return self.onMove(-1)

    def onMoveTop(self, event=None):
        return self.onMove('top')

    def onMoveDown(self, event=None):
        return self.onMove(+1)

    def onMoveBottom(self, event=None):
        return self.onMove('bottom')


class CheckboxFrame(FrameUnlabelled):
    '''A frame filled with checkboxes, with optional buttons for full state
    manipulation.

    This is a bunch of checkboxes, with optional buttons to enable or disable
    them all at once. Each checkbox is independent.
    Supports a nested specification for multiple checkboxen inside nested
    `FrameLabelled`, there's no limit to the nesting level.

    Each widget can be traced separately, with a non-ambigous function
    generator (see ``traceFn``).
    The widget ID and the labels can be customised using ``labelsCheckboxes``.

    The child widgets are placed on an internal `FrameUnlabelled`, named ``cbox``.

    Args:
        stateCheckboxes: Mapping from identifier to `Checkbox` label.
            Can be a nested mapping, keys and values must always be `str`.
        stateDefault: Default state for all child widgets. Optional, is `None`
            it's not changed from the `Checkbox` default.
        traceFn: Function generator for tracing each individual `Checkbox` widget.
            Receives the tree of nested widget ID as positional arguments.
        hasButtons: Include state manipulation buttons. Can be given as:

            - `True`: Include ``Enable All``/``Disable All`` buttons. This is
              the **default**.
            - `False`: Do not include any buttons
            - A list of `IButton <CheckboxFrame.IButton>` objects.

        layout: Layout setting for this frame. Only some values make sense:

            - ``R1,x``: "Enable" / "Disable" buttons on bottom. This is the
              **default**.
            - ``H1,x``: "Enable" / "Disable" buttons on top.
            - ``C1,x``: "Enable" / "Disable" buttons on the right side
            - ``V1,x``: "Enable" / "Disable" buttons on the left side
            - `VERTICAL`: Buttons on bottom, in a single column.
            - `HORIZONTAL`: Buttons on the left side, in a single line.

            All other layouts are possible, but they are ugly.
            Override `CheckboxFrame.setup_layout` in that case, for further
            tweaking.
        layoutCheckboxes: ``layout`` setting for the internal nested frames.
            Can be a single string, to be applied everywhere, or a list of strings
            to be applied on each nested level.
            This affects the orientation of the child widgets only.
            Defaults to automatic layout, whenever is not given.
        label: Include a toplevel label, keeping the state as-is.
            Optional, similar to a choice between `FrameLabelled` and
            `FrameUnlabelled`.
        labelsCheckboxes: Labels for internal nested widgets. Given as a
            mapping between nested identifiers and the label.
            For a simple case of a single level, the mapping key can be a
            simple string, instead of a tuple with a single string.
        argCheckboxes: Extra arguments passed to each individual `Checkbox` widget.
        argButtons: Extra arguments passed to each individual `Button` widget.
            Overriden by the `IButton.args <CheckboxFrame.IButton>` arguments.

    .. note::

        To create a version if this widget with a different base class (i.e.
        `FrameStateful` for example), use the following workaround:

        .. code:: python

            class CheckboxFrameStateful(FrameStateful):
                wstate_single = 'frame'

                def setup_widgets(self, **kwargs):
                    self.frame = tkmilan.CheckboxFrame(self, **kwargs)
            ...

            frame = CheckboxFrameStateful(PARENT, label='Frame Label', ...)

        Note this is different from setting a ``label``.
    '''
    wstate_single = 'cbox'

    @dataclass
    class IButton:
        '''`CheckboxFrame` button configuration object.

        Args:
            identifier: Identifies the button
            label: Button Label.
                Optional, if `None`, uses a label derived from the ``identifier``
            onClick: Widget ``onClick`` changes. Optional.
            onClickFn: Function generator for ``onClick`` function.
                Optional, overrides the ``onClick`` function.
                Receives the current widget as a single argument.
            onClickSetAll: Generate a `setAll <CheckboxFrame.setAll>` call,
                with the correct target.
                Optional, overrides the ``onClick`` function.
            args: Other arguments, passed to `Button`. Optional.
        '''
        identifier: str
        label: typing.Optional[str] = None
        onClick: typing.Optional[typing.Union[bool, typing.Callable]] = None
        onClickFn: typing.Optional[typing.Callable] = None
        onClickSetAll: typing.Optional[bool] = None
        args: typing.Optional[typing.Mapping[str, typing.Any]] = None

        def __post_init__(self):
            if __debug__:
                cnt_none_clicks = sum(1 for e in (
                    self.onClick,
                    self.onClickFn,
                    self.onClickSetAll,
                ) if e is not None)
                if cnt_none_clicks > 1:
                    raise ValueError(f'Button "{self.identifier}": Ambigous `onClick` definition')

        @property
        def id(self) -> str:
            return f'b:{self.identifier}'

        @property
        def lbl(self) -> str:
            return self.label or f'ID[{self.identifier}]'

    class __w_checkboxen:
        ''''''  # Internal, do not document
        _ID: typing.Tuple[str, ...]
        _subclass: 'CheckboxFrame.__w_checkboxen'

        def setup_widgets(self, *,
                          stateCheckboxes: typing.Mapping[str, typing.Any],
                          layoutCheckboxes: typing.Union[str, typing.Sequence[str]],
                          labelsCheckboxes: typing.Mapping[typing.Union[str, typing.Tuple[str, ...]], str],
                          argCheckboxes: typing.Optional[typing.Mapping[str, typing.Any]] = None,
                          ):
            ''''''  # Internal, do not document
            widgets = {}  # typing.MutableMapping[str, typing.Union[Checkbox, __w_lcheckboxen]]
            this_layout, next_layout = autolayout.gnested(layoutCheckboxes)

            assert callable(self._subclass), f'{self._subclass!r}: Invalid sub class'
            for cid, cobj in stateCheckboxes.items():
                c_id = (*self._ID, cid)
                c_label: str
                if isinstance(cobj, typing.Mapping):
                    c_label = labelsCheckboxes.get(cid, cid) if len(self._ID) == 0 else cid
                    widgets[cid] = self._subclass(self, thisID=c_id,
                                                  label=labelsCheckboxes.get(c_id, c_label),
                                                  stateCheckboxes=cobj,
                                                  layout=this_layout, layoutCheckboxes=next_layout,
                                                  labelsCheckboxes=labelsCheckboxes,
                                                  argCheckboxes=argCheckboxes)
                elif isinstance(cobj, str):
                    c_label = labelsCheckboxes.get(cid, cobj) if len(self._ID) == 0 else cobj
                    assert isinstance(self, mixin.ContainerWidget)
                    widgets[cid] = Checkbox(self, label=labelsCheckboxes.get(c_id, c_label),
                                            **(argCheckboxes or {}))
                else:
                    raise NotImplementedError
            return widgets

        def _setup_trace(self, traceFn):
            for wid, w in self.widgets.items():
                if isinstance(w, Checkbox):
                    w.trace(traceFn(*self._ID, wid))
                else:
                    assert hasattr(w, '_setup_trace'), f'Invalid Internal Checkbox Widget: {w}'
                    w._setup_trace(traceFn)

        def _state_all(self, state: bool):
            rval = {}
            assert isinstance(self, mixin.ContainerWidget), '{self} is not a valid tkmilan container widget'
            for wname, w in self.widgets.items():
                if isinstance(w, Checkbox):
                    rval[wname] = state
                else:
                    assert hasattr(w, '_state_all'), f'Invalid Internal Checkbox Widget: {w}'
                    rval[wname] = w._state_all(state)
            return rval

    class __w_lcheckboxen(__w_checkboxen, FrameLabelled):
        def __init__(self, *args,
                     thisID: typing.Tuple[str, ...],
                     **kwargs):
            self._ID = thisID
            super().__init__(*args, **kwargs)
    __w_lcheckboxen._subclass = typing.cast('CheckboxFrame.__w_checkboxen', __w_lcheckboxen)

    class __w_ucheckboxen(__w_checkboxen, FrameUnlabelled):
        def __init__(self, *args,
                     thisID: typing.Tuple[str, ...],
                     **kwargs):
            self._ID = thisID
            super().__init__(*args, **kwargs)
    __w_ucheckboxen._subclass = typing.cast('CheckboxFrame.__w_checkboxen', __w_lcheckboxen)

    def __init__(self, *args,
                 hasButtons: 'typing.Union[bool, typing.Sequence[CheckboxFrame.IButton]]' = True,
                 stateDefault: typing.Optional[bool] = None,
                 traceFn: typing.Optional[typing.Callable] = None,
                 **kwargs):
        # Save for later
        self._buttons: 'typing.Sequence[CheckboxFrame.IButton]'
        if hasButtons is True:
            self._buttons = [
                self.__class__.IButton('enable', 'Enable All',
                                       onClickSetAll=True),
                self.__class__.IButton('disable', 'Disable All',
                                       onClickSetAll=False),
            ]
        elif hasButtons is False:
            self._buttons = []
        else:
            self._buttons = hasButtons
        self._traceFn = traceFn
        self._stateDefault = stateDefault
        if self.layout == '':  # Automatic AUTO
            kwargs.setdefault('layout', AUTO if hasButtons is False else 'R1,x')
        super().__init__(*args, **kwargs)

    def setup_widgets(self, *, label: typing.Optional[str] = None,
                      stateCheckboxes: typing.Mapping[str, typing.Any],
                      layoutCheckboxes: typing.Union[str, typing.Sequence[str]] = AUTO,
                      labelsCheckboxes: typing.Optional[typing.Mapping[typing.Union[str, typing.Tuple[str, ...]], str]] = None,
                      argCheckboxes: typing.Optional[typing.Mapping[str, typing.Any]] = None,
                      argButtons: typing.Optional[typing.Mapping[str, typing.Any]] = None,
                      ):
        ''''''  # Do not document
        if __debug__:
            if all(isinstance(v, str) for v in stateCheckboxes.values()):
                assert len(stateCheckboxes) > 1, f'{self}: This is just a single Checkbox'

        self.cbox: 'typing.Union[CheckboxFrame.__w_ucheckboxen, CheckboxFrame.__w_lcheckboxen]'

        labelsCheckboxes = labelsCheckboxes or {}
        assert labelsCheckboxes is not None
        this_layout, next_layout = autolayout.gnested(layoutCheckboxes)
        if label is None:
            self.cbox = self.__class__.__w_ucheckboxen(self, thisID=tuple(),
                                                       stateCheckboxes=stateCheckboxes,
                                                       layout=this_layout, layoutCheckboxes=next_layout,
                                                       labelsCheckboxes=labelsCheckboxes,
                                                       argCheckboxes=argCheckboxes)
        else:
            self.cbox = self.__class__.__w_lcheckboxen(self, thisID=tuple(),
                                                       stateCheckboxes=stateCheckboxes,
                                                       layout=this_layout, layoutCheckboxes=next_layout,
                                                       labelsCheckboxes=labelsCheckboxes, label=label,
                                                       argCheckboxes=argCheckboxes)
        widgets: typing.MutableMapping[str, mixin.MixinWidget] = {}
        widgets['cbox'] = self.cbox
        for btn in self._buttons:
            assert btn.id not in ('', 'cbox'), f'Invalid IButton: {btn}'
            assert btn.id not in widgets, f'Repeated IButton ID: {btn.id}'
            btn_args = {
                **(argButtons or {}),
                **(btn.args or {})
            }
            widgets[btn.id] = Button(self, label=btn.lbl,
                                     **btn_args)
        return widgets

    def setup_layout(self, layout):
        '''Setup the layout for this widget.

        Adjusts the row and column configuration for the buttons.

        See the upstream `setup_layout <ContainerWidget.setup_layout>`
        documentation.

        Available for subclass redefinition.
        '''
        for btn in self._buttons:
            widget = self.widgets[btn.id]
            bgrid = widget.wgrid
            if layout.startswith(('R', 'r', 'H')):
                self.rowconfigure(bgrid.row, weight=0)  # Buttons Row
            elif layout.startswith(('C', 'c', 'V')):
                self.columnconfigure(bgrid.column, weight=0)  # Buttons Column
            else:
                pass  # Not a simple row/column alignment

    def setup_defaults(self):
        '''Set the default values and wire up button events.

        See the upstream `setup_defaults <ContainerWidget.setup_defaults>`
        documentation.

        Available for subclass redefinition, make sure this still runs.
        '''
        if self._stateDefault is not None:
            self.setAll(self._stateDefault)
        for btn in self._buttons:
            btn_widget = self.widgets[btn.id]
            if btn.onClickSetAll is not None:
                btn_widget.onClick = self.setAllFn(btn.onClickSetAll)
            elif btn.onClickFn is not None:
                btn_widget.onClick = btn.onClickFn(self)
            elif btn.onClick is not None:
                btn_widget.onClick = btn.onClick

    def setup_adefaults(self):
        '''Set the widget traces.

        See the upstream `setup_adefaults <ContainerWidget.setup_adefaults>`
        documentation.

        Available for subclass redefinition, make sure this still runs.
        '''
        if self._traceFn:
            self.cbox._setup_trace(self._traceFn)

    def wbutton(self, identifier: str) -> Button:
        '''Get the button widget by identifier.

        This is just an helper function to get the correct widget value out of
        ``widgets``, based on the identifier.

        Args:
            idx: The tab identifier.

        Note:
            In debug mode, this will fail if called with the wrong identifier.
            This check is skipped for performance on optimized mode.
        '''
        btn_id = f'b:{identifier}'
        assert btn_id == self.__class__.IButton(identifier).id
        assert btn_id in self.widgets, f'Invalid Button: {identifier}'
        btn_w = self.widgets.get(btn_id)
        assert isinstance(btn_w, Button), f'Invalid Widget: {btn_w!r}'
        return btn_w

    def setAll(self, state: bool):
        '''Set the state for all child widgets.

        Args:
            state: The state to consider.
        '''
        self.wstate = self.cbox._state_all(state)

    def setAllFn(self, state: bool) -> typing.Callable:
        '''Function generator for `setAll`.'''
        def setAllFn():
            return self.setAll(state)
        return setAllFn


# # Legacy Wrappers

def Spinbox(*args, **kwargs):
    warnings.warn('Use `SpinboxN`, the widget state is slightly different', stacklevel=2)
    return SpinboxNum(*args, **kwargs)


def SpinboxNum(*args, **kwargs):
    warnings.warn('Use `SpinboxN`, just a rename', stacklevel=2)
    return SpinboxN(*args, **kwargs)


def Combobox(*args, **kwargs):
    warnings.warn('Use `ComboboxN`, the widget state is slightly different', stacklevel=2)
    return ComboboxN(*args, **kwargs)


def ComboboxRaw(*args, **kwargs):
    warnings.warn('Use `ComboboxN`, just a rename', stacklevel=2)
    return ComboboxN(*args, **kwargs)


def ComboboxMap(*args, **kwargs):
    warnings.warn('Use `ComboboxN`, just a rename', stacklevel=2)
    return ComboboxN(*args, **kwargs)


def Entry(*args, **kwargs):
    warnings.warn('Use `EntryRaw`, just a rename', stacklevel=2)
    return EntryRaw(*args, **kwargs)
