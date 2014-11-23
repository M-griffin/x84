"""
x/84 bbs module, https://github.com/jquast/x84
"""
# std
import warnings

# local, side-effects (encodings are registered)
__import__('encodings.aliases')
__import__('x84.encodings')
# local/exported
from x84.bbs.userbase import list_users, get_user, find_user, User, Group
from x84.bbs.msgbase import list_msgs, get_msg, list_tags, Msg
from x84.bbs.exception import Disconnected, Goto
from x84.bbs.editor import LineEditor, ScrollingEditor
from x84.bbs.output import (echo, timeago, encode_pipe, decode_pipe,
                            syncterm_setfont,
                            Ansi, ansiwrap  # deprecated
                            )
from x84.bbs.ansiwin import AnsiWindow
from x84.bbs.selector import Selector
from x84.bbs.lightbar import Lightbar
from x84.bbs.cp437 import from_cp437
from x84.bbs.dbproxy import DBProxy
from x84.bbs.pager import Pager
from x84.bbs.door import Door, DOSDoor, Dropfile


__all__ = ['list_users', 'get_user', 'find_user', 'User', 'Group', 'list_msgs',
           'get_msg', 'list_tags', 'Msg', 'LineEditor', 'ScrollingEditor',
           'echo', 'timeago', 'Ansi', 'ansiwrap', 'AnsiWindow', 'Selector',
           'Lightbar', 'from_cp437', 'DBProxy', 'Pager', 'Door', 'DOSDoor',
           'goto', 'disconnect', 'getsession', 'getterminal', 'getch', 'gosub',
           'ropen', 'showart', 'showcp437', 'Dropfile', 'encode_pipe',
           'decode_pipe', 'syncterm_setfont', 'get_ini',
           ]


# Translation map for embedded font hints in SAUCE records as documented at
# http://www.acid.org/info/sauce/sauce.htm section FontName

SAUCE_FONT_MAP = {
    'Amiga MicroKnight':  'amiga',
    'Amiga MicroKnight+': 'amiga',
    'Amiga mOsOul':       'amiga',
    'Amiga P0T-NOoDLE':   'amiga',
    'Amiga Topaz 1':      'amiga',
    'Amiga Topaz 1+':     'amiga',
    'Amiga Topaz 2':      'amiga',
    'Amiga Topaz 2+':     'amiga',
    'Atari ATASCII':      'atari',
    'IBM EGA43':          'cp437',
    'IBM EGA':            'cp437',
    'IBM VGA25G':         'cp437',
    'IBM VGA50':          'cp437',
    'IBM VGA':            'cp437',
}

# All IBM PC code pages that are supported

for page in (
    '437', '720', '737', '775', '819', '850', '852', '855', '857', '858',
    '860', '861', '862', '863', '864', '865', '866', '869', '872',
):
    codec = 'cp%s' % (page,)
    SAUCE_FONT_MAP.update({
        'IBM EGA43 %s'  % (page,): codec,
        'IBM EGA %s'    % (page,): codec,
        'IBM VGA25g %s' % (page,): codec,
        'IBM VGA50 %s'  % (page,): codec,
        'IBM VGA %s'    % (page,): codec,
    })


def goto(script, *args, **kwargs):
    """
    Change bbs script. Does not return.
    """
    raise Goto(script, *args, **kwargs)


def disconnect(reason=u''):
    """
    Disconnect session. Does not return.
    """
    raise Disconnected(reason,)


def getsession():
    """
    Returns Session of calling process.
    """
    import x84.bbs.session
    return x84.bbs.session.getsession()


def getterminal():
    """
    Returns Terminal of calling process.
    """
    import x84.bbs.session
    return x84.bbs.session.getterminal()


# temporary hacks until blessings updates with term.inkey() upstream ..
def getch(timeout=None):
    """
    Retrieve a keystroke from 'input' queue, blocking forever or, when
    specified, None when timeout has elapsed.

    upstream blessings has better 'keycode' evaluation (none of this
    duck typing, its always unicode, but has .is_sequence bool test,
    and a .value test for keycode comparison). we workaround for legacy
    behavior unless upstream blessings accepts our impl. in some form ..
    """
    keystroke = getterminal().inkey(timeout)
    if keystroke == u'':
        return None
    if keystroke.is_sequence:
        return keystroke.code
    return keystroke


def gosub(script, *args, **kwargs):
    """
    Call bbs script with optional arguments, Returns value.
    """
    from x84.bbs.session import Script
    # pylint: disable=W0142
    #        Used * or ** magic
    script = Script(name=script, args=args, kwargs=kwargs)
    return getsession().runscript(script)


def ropen(filename, mode='rb'):
    """
    Open random file using wildcard (glob)
    """
    import glob
    import random
    files = glob.glob(filename)
    return open(random.choice(files), mode) if len(files) else None


def showart(filepattern, encoding=None, auto_mode=True, center=False,
            poll_cancel=False, msg_cancel=None):
    """
    Yield unicode sequences for any given ANSI Art (of art_encoding). Effort
    is made to parse SAUCE data, translate input to unicode, and trim artwork
    too large to display.  If ``poll_cancel`` is not ``False``, represents
    time as float for each line to block for keypress -- if any is received,
    then iteration ends and ``msg_cancel`` is displayed as last line of art.

    If you provide no ``encoding``, the piece encoding will be based on either
    the encoding in the SAUCE record, the configured default or the default
    fallback ``CP437`` encoding.

    Alternate codecs are available if you provide the ``encoding`` argument.
    For example, if you want to show an Amiga style ASCII art file::

        >>> from x84.bbs import echo, showart
        >>> for line in showart('test.asc', 'topaz'):
        ...     echo(line)

    The ``auto_mode`` flag will, if set, only respect the selected encoding if
    the active session is UTF-8 capable.

    If ``center`` is set to ``True``, the piece will be centered respecting the
    current terminal's width.

    """
    import random
    import glob
    import os
    from sauce import SAUCE
    from x84.bbs.ini import CFG

    term = getterminal()

    # Open the piece
    try:
        filename = os.path.relpath(random.choice(glob.glob(filepattern)))
    except IndexError:
        filename = None

    if filename is None:
        yield u''.join((
            term.bold_red(u'-- '),
            u'no files matching {0}'.format(filepattern),
            term.bold_red(u' --'),
        ))
        return

    # Parse the piece
    parsed = SAUCE(filename)

    # If no explicit encoding is given, we go through a couple of steps to
    # resolve the possible file encoding:
    if encoding is None:
        # 1. See if the SAUCE record has a font we know about, it's in the
        #    filler
        if parsed.record and parsed.filler_str in SAUCE_FONT_MAP:
            encoding = SAUCE_FONT_MAP[parsed.filler_str]

        # 2. Get the system default art encoding
        elif CFG.has_option('system', 'art_utf8_codec'):
            encoding = CFG.get('system', 'art_utf8_codec')

        # 3. Fall back to CP437
        else:
            encoding = 'cp437'

    # If auto_mode is enabled, we'll only use the input encoding on UTF-8
    # capable terminals, because our codecs do not know how to "transcode"
    # between the various encodings.
    if auto_mode:
        def _decode(what):
            session = getsession()
            if session.encoding == 'utf8':
                return what.decode(encoding)
            elif session.encoding == 'cp437':
                return what.decode('cp437')
            else:
                return what

    # If auto_mode is disabled, we'll just respect whatever input encoding was
    # selected before
    else:
        _decode = lambda what: what.decode(encoding)

    # For wide terminals, center the piece on the screen using cursor movement,
    # if requested
    padding = u''
    if center and term.width > 81:
        padding = term.move_x((term.width / 2) - 40)

    msg_cancel = msg_cancel or u''.join(
        (term.normal,
         term.bold_black(u'-- '),
         u'cancelled {0} by input'.format(filename),
         term.bold_black(u' --'),
         ))

    msg_too_wide = u''.join(
        (term.normal,
         term.bold_black(u'-- '),
         u'cancelled {0}, too wide:: {{0}}'.format(filename),
         term.bold_black(u' --'),
         ))

    lines = _decode(parsed.data).splitlines()
    for idx, line in enumerate(lines):
        # Allow slow terminals to cancel by pressing a keystroke
        if poll_cancel is not False and term.inkey(poll_cancel):
            yield u'\r\n' + term.center(msg_cancel) + u'\r\n'
            return
        line_length = term.length(line.rstrip())
        if not padding and term.width < line_length:
            yield (u'\r\n' +
                   term.center(msg_too_wide.format(line_length)) +
                   u'\r\n')
            return
        if idx == len(lines) - 1:
            # strip DOS end of file (^Z)
            line = line.rstrip('\x1a')
            if not line.strip():
                break
        yield padding + line + u'\r\n'
    yield term.normal


def showcp437(filepattern):
    warnings.warn('showcp437() is deprecated, use show_art()')
    return showart(filepattern, 'cp437')


def get_ini(section=None, key=None, getter='get', split=False, splitsep=None):
    """
    Get an ini configuration of ``section`` and ``key``.

    If the option does not exist, an empty list, string, or False
    is returned -- return type decided by the given arguments.

    The ``getter`` method is 'get' by default, returning a string.
    For booleans, use ``getter='get_boolean'``.

    To return a list, use ``split=True``.
    """
    from x84.bbs.ini import CFG
    assert section is not None, section
    assert key is not None, key
    if CFG.has_option(section, key):
        getter = getattr(CFG, getter)
        value = getter(section, key)
        if split and hasattr(value, 'split'):
            return map(str.strip, value.split(splitsep))
        return value
    if getter == 'getboolean':
        return False
    if split:
        return []
    return u''
