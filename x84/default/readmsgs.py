"""
Message reader for x/84, https://github.com/jquast/x84

This script provides an interface to check for new
messages, subscribe to and browse tags and networks,
find all, or unread messages, or all messages since
last login.

It determines a set of message-ids that are then
forwarded to the message browser interface.
"""

from x84.bbs import getsession, getterminal
from common import display_banner

#: banner art displayed in main()
art_file = os.path.join(here, 'art', 'msgarea.ans')

#: character encoding of banner art
art_encoding = 'cp437'

#: preferred fontset for SyncTerm emulator
syncterm_font = 'cp437'


def set_subscription_tags(session, term):
    """
    This function is called to assign a new set of subscription
    tags for a user.  If escape is pressed, the existing value
    is used, or '*' is used if not previously set.

    This should be called for first-time users, and optionally
    at any later time to change a subscription.
    """
    from x84.bbs import echo, ScrollingEditor
    from common import show_description

    # introduce the user to the concept ...
    description = (
        u'You can think of tags as a system of providing context to any '
        u'message stored on this system.  A tag might signify that it was '
        u'received on a particular message network, or it might provide '
        u'the topic of conversation, such as "python" or "rock music".  '
        u"This is similar to flicker's tags, or twitter hashtags. "
        u'Use glob expressions as a comma-delimited list, for example, '
        u'the expression "x84net, sysop, python*" will subscribe to all '
        u'tags of the x84net message network, sysop messages, and any '
        u'topics that begin with the phrase "python".  You can subscribe '
        u'to all topics using the expression, "*".')

    show_description(description, color='yellow')

    echo(u'\r\n')

    description = u' '.join(
        [u'tags available:', ] +
        ['{tag}{term.yellow},{term.normal}'
         .format(tag=tag, term=term)
         for tag in list_tags()])

    echo(u'\r\n')

    # We use the ScrollingEditor class, which must have an absolute (y,x)
    # position.  So we first, we cause a (maybe) scroll at the bottom of
    # the screen to leave room for the editor window.
    echo(term.move(term.height, 0))
    echo(u'\r\n' * 3)

    # display our prompt prefix, input_prefix:
    input_prefix = u'  {sep} {key:>18}: '.format(
        sep=term.bright_yellow(u'::'),
        key='subscription tags')
    echo(input_prefix)

    # and prompt an editor on that row
    editor = ScrollingEditor(xloc=term.length(input_prefix),
                             yloc=term.height - 4,
                             width=(term.width - xloc - 2),
                             colors = {'highlight': term.black_on_yellow})

    value = editor.read() or u''
    echo(term.normal + u'\r\n\r\n')

    return map(str.strip, value.split(','))


def main(last_called=None):
    """ Main procedure. """

    session, term = getsession(), getterminal()
    session.activity = 'checking for new messages'

    # set syncterm font, if any
    if term._kind == 'ansi':
        echo(syncterm_setfont(syncterm_font))

    search_tags = user.get(key='msg_subscription', None)

    if search_tags is None:
        # prompt user for tag subscription
        search_tags = set_subscription_tags(session, term)

    display_banner(art_file, encoding=art_encoding)



#FILTER_PRIVATE = True
#ALREADY_READ = set()
#DELETED = set()
#SEARCH_TAGS = set()
#READING = False
#TIME_FMT = '%A %b-%d, %Y at %r'
#
#
#
#
#def quote_body(msg, width=79, quote_txt=u'> ', hardwrap=u'\r\n'):
#    """
#    Given a message, return new string suitable for quoting it.
#    """
#    from x84.bbs import getterminal
#    import dateutil.tz
#    term = getterminal()
#    ucs = u''
#    for line in msg.body.splitlines():
#        ucs += u''.join((
#            quote_txt,
#            u'\r\n'.join(term.wrap(line, width - len(quote_txt), subsequent_indent=quote_txt)),
#            hardwrap,))
#    return u''.join((
#        'On ',
#        msg.stime.replace(tzinfo=dateutil.tz.tzlocal()).astimezone(dateutil.tz.tzutc()).strftime(TIME_FMT), u' UTC ',
#        msg.author, u' wrote:',
#        hardwrap, ucs, hardwrap))
#
#
#def allow_tag(idx):
#    """
#    Returns true if user is allowed to 't'ag message at idx:
#        * sysop and moderator
#        * author or recipient
#        * a member of any message tag matching user group
#    """
#    from x84.bbs import getsession, get_msg
#    session = getsession()
#    if ('sysop' in session.user.groups
#            or 'moderator' in session.user.groups):
#        return True
#    msg = get_msg(idx)
#    if session.user.handle in (msg.recipient, msg.author):
#        return True
#    for tag in msg.tags:
#        if tag in session.user.groups:
#            return True
#    return False
#
#
#def mark_undelete(idx):
#    """ Mark message ``idx`` as deleted. """
#    from x84.bbs import getsession
#    session = getsession()
#    # pylint: disable=W0603
#    #         Using the global statement
#    global DELETED
#    DELETED = session.user.get('trash', set())
#    if idx in DELETED:
#        DELETED.remove(idx)
#        session.user['trash'] = DELETED
#        return True
#
#
#def mark_delete(idx):
#    """ Mark message ``idx`` as deleted. """
#    from x84.bbs import getsession
#    session = getsession()
#    # pylint: disable=W0603
#    #         Using the global statement
#    global DELETED
#    DELETED = session.user.get('trash', set())
#    if not idx in DELETED:
#        DELETED.add(idx)
#        session.user['trash'] = DELETED
#        return True
#
#
#def mark_read(idx):
#    """ Mark message ``idx`` as read. """
#    from x84.bbs import getsession
#    session = getsession()
#    # pylint: disable=W0603
#    #         Using the global statement
#    global ALREADY_READ
#    ALREADY_READ = session.user.get('readmsgs', set())
#    if idx not in ALREADY_READ:
#        ALREADY_READ.add(idx)
#        session.user['readmsgs'] = ALREADY_READ
#        return True
#
#
#def msg_filter(msgs):
#    """
#        filter all matching messages. userland implementation
#        of private/public messaging by using the 'tags' database.
#        'new', or unread messages are marked by idx matching
#        session.user['readmsgs'] when read. Finally, implement 'group'
#        tagging, so that users of group 'impure' are allowed to read
#        messages tagged by 'impure', regardless of recipient or 'public'.
#
#        returns (msgs), (new). new contains redundant msgs
#    """
#    # pylint: disable=R0914,R0912,R0915
#    #         Too many local variables
#    #         Too many branches
#    #         Too many statements
#    from x84.bbs import list_msgs, echo, getsession, getterminal, get_msg
#    session, term = getsession(), getterminal()
#    public_msgs = list_msgs(('public',))
#    addressed_to = 0
#    addressed_grp = 0
#    filtered = 0
#    deleted = 0
#    private = 0
#    public = 0
#    new = set()
#    echo(u' Processing ' + term.reverse_yellow('..'))
#    for msg_id in msgs.copy():
#        if msg_id in public_msgs:
#            # can always ready msgs tagged with 'public'
#            public += 1
#        else:
#            private += 1
#        msg = get_msg(msg_id)
#        if msg.recipient == session.user.handle:
#            addressed_to += 1
#        else:
#            # a system of my own, by creating groups
#            # with the same as tagged messages, you may
#            # create private or intra-group messages.
#            tag_matches_group = False
#            for tag in msg.tags:
#                if tag in session.user.groups:
#                    tag_matches_group = True
#                    break
#            if tag_matches_group:
#                addressed_grp += 1
#            elif msg_id not in public_msgs:
#                # denied to read this message
#                if FILTER_PRIVATE:
#                    msgs.remove(msg_id)
#                    filtered += 1
#                    continue
#            elif msg_id in DELETED:
#                msgs.remove(msg_id)
#                deleted += 1
#        if msg_id not in ALREADY_READ:
#            new.add(msg_id)
#
#    if 0 == len(msgs):
#        echo(u'\r\n\r\nNo messages (%s filtered).' % (filtered,))
#    else:
#        txt_out = list()
#        if addressed_to > 0:
#            txt_out.append('%s addressed to you' % (
#                term.bold_yellow(str(addressed_to)),))
#        if addressed_grp > 0:
#            txt_out.append('%s addressed by group' % (
#                term.bold_yellow(str(addressed_grp)),))
#        if filtered > 0:
#            txt_out.append('%s filtered' % (
#                term.bold_yellow(str(filtered)),))
#        if deleted > 0:
#            txt_out.append('%s deleted' % (
#                term.bold_yellow(str(deleted)),))
#        if public > 0:
#            txt_out.append('%s public' % (
#                term.bold_yellow(str(public)),))
#        if private > 0:
#            txt_out.append('%s private' % (
#                term.bold_yellow(str(private)),))
#        if len(new) > 0:
#            txt_out.append('%s new' % (
#                term.bold_yellow(str(len(new),)),))
#        if 0 != len(txt_out):
#            echo(u'\r\n\r\n' + u'\r\n'.join(term.wrap(
#                u', '.join(txt_out) + u'.', (term.width - 2))))
#    return msgs, new
#
#
#def prompt_tags(tags):
#    """ Prompt for and return valid tags from TAGDB. """
#    # pylint: disable=R0914,W0603
#    #         Too many local variables
#    #         Using the global statement
#    from x84.bbs import DBProxy, echo, getterminal, getsession
#    from x84.bbs import LineEditor, getch
#    session, term = getsession(), getterminal()
#    tagdb = DBProxy('tags')
#    global FILTER_PRIVATE
#    while True:
#        # Accept user input for a 'search tag', or /list command
#        #
#        echo(u"\r\n\r\nENtER SEARCh %s, COMMA-dEliMitEd. " % (
#            term.red('TAG(s)'),))
#        echo(u"OR '/list', %s%s\r\n : " % (
#            (term.yellow_underline('^x') + u':autoscan '
#                if session.user.get('autoscan', False) else u''),
#            term.yellow_underline('^a') + u':ll msgs ' +
#            term.yellow_underline('Esc') + u':quit',))
#        width = term.width - 6
#        sel_tags = u', '.join(tags)
#        while term.length(sel_tags) >= (width - 8):
#            tags = tags[:-1]
#            sel_tags = u', '.join(tags)
#        lne = LineEditor(width, sel_tags)
#        echo(lne.refresh())
#        while not lne.carriage_returned:
#            inp = getch()
#            if inp in (unichr(27), term.KEY_EXIT):
#                return None
#            if inp in (unichr(24),): # ^A:all
#                return set()
#            if inp in (unichr(1),): # ^X:autoscan
#                return session.user.get('autoscan', set())
#            else:
#                echo(lne.process_keystroke(inp))
#        if lne.carriage_returned:
#            inp_tags = lne.content
#        if (inp_tags is None or 0 == len(inp_tags)
#                or inp_tags.strip().lower() == '/quit'):
#            return set()
#        elif inp_tags.strip().lower() == '/list':
#            # list all available tags, and number of messages
#            echo(term.normal)
#            echo(u'\r\n\r\nTags: \r\n')
#            all_tags = sorted(tagdb.items())
#            if 0 == len(all_tags):
#                echo(u'None !'.center(term.width / 2))
#            else:
#                echo(u'\r\n'.join((term.wrap(u', '.join(([u'%s(%s)' % (
#                    term.red(tag),
#                    term.yellow(str(len(msgs))),)
#                        for (tag, msgs) in all_tags])), (term.width - 2)))))
#            continue
#        elif (inp_tags.strip().lower() == '/nofilter'
#                and 'sysop' in session.user.groups):
#            # disable filtering private messages
#            FILTER_PRIVATE = False
#            continue
#
#        echo(u'\r\n')
#        # search input as valid tag(s)
#        tags = set([_tag.strip().lower() for _tag in inp_tags.split(',')])
#        for tag in tags.copy():
#            if not tag in tagdb:
#                tags.remove(tag)
#                echo(u"\r\nNO MESSAGES With tAG '%s' fOUNd." % (
#                    term.red(tag),))
#        return tags
#
#
#def list_tags():
#
#    from x84.bbs import getsession, getterminal, echo, getch
#    from x84.bbs import list_msgs
#    if subscription is not None:
#        return subscription
#
#
#    echo(banner())
#
#    global ALREADY_READ, SEARCH_TAGS, DELETED
#    if autoscan_tags is not None:
#        SEARCH_TAGS = autoscan_tags
#        echo(u''.join((
#            term.bold_black('[ '),
#            term.yellow('AUtOSCAN'),
#            term.bold_black(' ]'), u'\r\n')))
#    else:
#        SEARCH_TAGS = set(['public'])
#
#        # also throw in user groups, maybe the top 3 .. ?
#        SEARCH_TAGS.update(session.user.groups)
#        SEARCH_TAGS = prompt_tags(SEARCH_TAGS)
#        # user escape
#        if SEARCH_TAGS is None:
#            return
#
#    echo(u'\r\n\r\n%s%s ' % (
#        term.bold_yellow('SCANNiNG'),
#        term.bold_black(':'),))
#    echo(u','.join([term.red(tag) for tag in SEARCH_TAGS]
#                   if 0 != len(SEARCH_TAGS) else ['<All>', ]))
#
#    if (SEARCH_TAGS != session.user.get('autoscan', None)):
#        echo(u'\r\n\r\nSave tag list as autoscan on login [yn] ?\b\b')
#        while True:
#            inp = getch()
#            if inp in (u'q', 'Q', unichr(27), u'n', u'N'):
#                break
#            elif inp in (u'y', u'Y'):
#                session.user['autoscan'] = SEARCH_TAGS
#                break
#
#    # retrieve all matching messages,
#    all_msgs = list_msgs(SEARCH_TAGS)
#    echo(u'\r\n\r\n%s messages.' % (term.yellow_reverse(str(len(all_msgs),))))
#    if 0 == len(all_msgs):
#        getch(0.5)
#        return
#
#    # filter messages public/private/group-tag/new
#    ALREADY_READ = session.user.get('readmsgs', set())
#    DELETED = session.user.get('trash', set())
#    msgs, new = msg_filter(all_msgs)
#    if 0 == len(msgs) and 0 == len(new):
#        getch(0.5)
#        return
#
#    # prompt read 'a'll, 'n'ew, or 'q'uit
#    echo(u'\r\n  REAd [%s]ll %d%s message%s [qa%s] ?\b\b' % (
#        term.yellow_underline(u'a'),
#        len(msgs), (
#        u' or %d [%s]EW ' % (
#        len(new), term.yellow_underline(u'n'),)
#            if new else u''),
#        u's' if 1 != len(msgs) else u'',
#        u'n' if new else u'',))
#    while True:
#        inp = getch()
#        if inp in (u'q', 'Q', unichr(27)):
#            return
#        elif inp in (u'n', u'N') and len(new):
#            # read only new messages
#            msgs = new
#            break
#        elif inp in (u'a', u'A'):
#            break
#
#    # read target messages
#    read_messages(msgs, new)
#
#
#def read_messages(msgs, new):
#    """
#    Provide message reader UI given message list ``msgs``,
#    with new messages in list ``new``.
#    """
#    # pylint: disable=R0914,R0912,R0915
#    #         Too many local variables
#    #         Too many branches
#    #         Too many statements
#    from x84.bbs import timeago, get_msg, getterminal, echo, gosub
#    from x84.bbs import ini, Pager, getsession, getch, Msg
#    import x84.default.writemsg
#    session, term = getsession(), getterminal()
#
#    session.activity = 'reading msgs'
#    # build header
#    len_idx = max([len('%d' % (_idx,)) for _idx in msgs])
#    len_author = ini.CFG.getint('nua', 'max_user')
#    len_ago = 9
#    len_subject = ini.CFG.getint('msg', 'max_subject')
#    len_preview = min(len_idx + len_author + len_ago + len_subject + -1, term.width - 2)
#    reply_depth = ini.CFG.getint('msg', 'max_depth')
#    indent_start, indent, indent_end = u'\\', u'-', u'> '
#
#    def get_header(msgs_idx):
#        """
#        Return list of tuples, (idx, unicodestring), suitable for Lightbar.
#        """
#        import datetime
#        msg_list = list()
#        thread_indent = lambda depth: (term.red(
#            (indent_start + (indent * depth) + indent_end))
#            if depth else u'')
#
#        def head(msg, depth=0, maxdepth=reply_depth):
#            """ This recursive routine finds the 'head' message
#                of any relationship, up to maxdepth.
#            """
#            if (depth <= maxdepth
#                    and hasattr(msg, 'parent')
#                    and msg.parent is not None):
#                return head(get_msg(msg.parent), depth + 1, maxdepth)
#            return msg.idx, depth
#
#        for idx in msgs_idx:
#            msg = get_msg(idx)
#            author, subj = msg.author, msg.subject
#            tm_ago = (datetime.datetime.now() - msg.stime).total_seconds()
#            # pylint: disable=W0631
#            #         Using possibly undefined loop variable 'idx'
#            attr = lambda arg: (
#                term.bold_green(arg) if (
#                    not idx in ALREADY_READ
#                    and msg.recipient == session.user.handle) else
#                term.red(arg) if not idx in ALREADY_READ
#                else term.yellow(arg))
#            status = [u'U' if not idx in ALREADY_READ else u' ',
#                      u'D' if idx in DELETED else u' ', ]
#            row_txt = u'%s %s %s %s %s%s ' % (
#                u''.join(status),
#                attr(str(idx).rjust(len_idx)),
#                attr(author.ljust(len_author)),
#                (timeago(tm_ago)).rjust(len_ago),
#                attr(u'ago'),
#                term.bold_black(':'),)
#            msg_list.append((head(msg), idx, row_txt, subj))
#        msg_list.sort(reverse=True)
#        return [(idx, row_txt + thread_indent(depth) + subj)
#                for (_threadid, depth), idx, row_txt, subj in msg_list]
#
#    def get_selector(mailbox, prev_sel=None):
#        """
#        Provide Lightbar UI element given message mailbox returned from
#        function get_header, and prev_sel as previously instantiated Lightbar.
#        """
#        from x84.bbs import Lightbar
#        pos = prev_sel.position if prev_sel is not None else (0, 0)
#        sel = Lightbar(
#            height=(term.height / 3
#                    if term.width < 140 else term.height - 3),
#            width=len_preview,
#            yloc=2, xloc=0)
#        sel.glyphs['top-horiz'] = u''
#        sel.glyphs['left-vert'] = u''
#        sel.colors['highlight'] = term.yellow_reverse
#        sel.update(mailbox)
#        sel.position = pos
#        return sel
#
#    def get_reader():
#        """
#        Provide Pager UI element for message reading.
#        """
#        reader_height = (term.height - (term.height / 3) - 2)
#        reader_indent = 2
#        reader_width = min(term.width - 1, min(term.width - reader_indent, 80))
#        reader_ypos = ((term.height - 1 ) - reader_height if
#                      (term.width - reader_width) < len_preview else 2)
#        reader_height = term.height - reader_ypos - 1
#        msg_reader = Pager(
#            height=reader_height,
#            width=reader_width,
#            yloc=reader_ypos,
#            xloc=min(len_preview + 2, term.width - reader_width))
#        msg_reader.glyphs['top-horiz'] = u''
#        msg_reader.glyphs['right-vert'] = u''
#        return msg_reader
#
#    def format_msg(reader, idx):
#        """ Format message of index ``idx`` into Pager instance ``reader``. """
#        msg = get_msg(idx)
#        sent = msg.stime.strftime(TIME_FMT)
#        to_attr = term.bold_green if (
#            msg.recipient == session.user.handle) else term.underline
#        ucs = u'\r\n'.join((
#            (u''.join((
#                term.yellow('fROM: '),
#                (u'%s' % term.bold(msg.author,)).rjust(len_author),
#                u' ' * (reader.visible_width - (len_author + len(sent))),
#                sent,))),
#            u''.join((
#                term.yellow('tO: '),
#                to_attr((u'%s' % to_attr(msg.recipient,)).rjust(len_author)
#                        if msg.recipient is not None else u'All'),)),
#            (u'\r\n'.join((term.wrap(
#                term.yellow('tAGS: ')
#                + (u'%s ' % (term.bold(','),)).join((
#                    [term.bold_red(_tag)
#                        if _tag in SEARCH_TAGS
#                        else term.yellow(_tag)
#                        for _tag in msg.tags])),
#                            reader.visible_width,
#                            subsequent_indent=u' ' * 6)))),
#            (term.yellow_underline(
#                (u'SUbj: %s' % (msg.subject,)).ljust(reader.visible_width)
#            )),
#            u'', (msg.body),))
#        return ucs
#
#    def get_selector_title(mbox, new):
#        """
#        Returns unicode string suitable for displaying as title of mailbox.
#        """
#        newmsg = (term.yellow(u' ]-[ ') +
#                  term.yellow_reverse(str(len(new))) +
#                  term.bold_underline(u' NEW')) if len(new) else u''
#        return u''.join((term.yellow(u'[ '),
#                         term.bold_yellow(str(len(mbox))),
#                         term.bold(
#                         u' MSG%s' % (u's' if 1 != len(mbox) else u'',)),
#                         newmsg, term.yellow(u' ]'),))
#
#    dispcmd_mark = lambda idx: (
#        (term.yellow_underline(u' ') + u':mark' + u' ')
#        if idx not in ALREADY_READ else u'')
#    dispcmd_delete = lambda idx: (
#        (term.yellow_underline(u'D') + u':elete' + u' ')
#        if idx not in DELETED else u'')
#    dispcmd_tag = lambda idx: (
#        (term.yellow_underline(u't') + u':ag' + u' ')
#        if allow_tag(idx) else u'')
#
#    def get_selector_footer(idx):
#        """
#        Returns unicode string suitable for displaying
#        as footer of mailbox when window is active.
#        """
#        return u''.join((
#            term.yellow(u'- '),
#            u''.join((
#                term.yellow_underline(u'>') + u':read ',
#                term.yellow_underline(u'r') + u':eply ',
#                dispcmd_mark(idx),
#                dispcmd_delete(idx),
#                dispcmd_tag(idx),
#                term.yellow_underline(u'q') + u':uit',)),
#            term.yellow(u' -'),))
#
#    def get_reader_footer(idx):
#        """
#        Returns unicode string suitable for displaying
#        as footer of reader when window is active
#        """
#
#        return u''.join((
#            term.yellow(u'- '),
#            u' '.join((
#                term.yellow_underline(u'<') + u':back ',
#                term.yellow_underline(u'r') + u':eply ',
#                dispcmd_delete(idx),
#                dispcmd_tag(idx),
#                term.yellow_underline(u'q') + u':uit',)),
#            term.yellow(u' -'),))
#
#    def refresh(reader, selector, mbox, new):
#        """
#        Returns unicode string suitable for refreshing the screen.
#        """
#        from x84.bbs import getsession
#        session = getsession()
#
#        if READING:
#            reader.colors['border'] = term.bold_yellow
#            selector.colors['border'] = term.bold_black
#        else:
#            reader.colors['border'] = term.bold_black
#            selector.colors['border'] = term.bold_yellow
#        title = get_selector_title(mbox, new)
#        padd_attr = (term.bold_yellow if not READING
#                     else term.bold_black)
#        sel_padd_right = padd_attr(
#            u'-'
#            + selector.glyphs['bot-horiz'] * (
#            selector.visible_width - term.length(title) - 7)
#            + u'-\u25a0-' if READING else u'- -')
#        sel_padd_left = padd_attr(
#            selector.glyphs['bot-horiz'] * 3)
#        idx = selector.selection[0]
#        return u''.join((term.move(0, 0), term.clear, u'\r\n',
#                         u'// REAdiNG MSGS ..'.center(term.width).rstrip(),
#                         selector.refresh(),
#                         selector.border() if READING else reader.border(),
#                         reader.border() if READING else selector.border(),
#                         selector.title(
#                             sel_padd_left + title + sel_padd_right),
#                         selector.footer(get_selector_footer(idx)
#                                         ) if not READING else u'',
#                         reader.footer(get_reader_footer(idx)
#                                       ) if READING else u'',
#                         reader.refresh(),
#                         ))
#
#    echo((u'\r\n' + term.clear_eol) * (term.height - 1))
#    dirty = 2
#    msg_selector = None
#    msg_reader = None
#    idx = None
#    # pylint: disable=W0603
#    #         Using the global statement
#    global READING
#    while (msg_selector is None and msg_reader is None
#           ) or not (msg_selector.quit or msg_reader.quit):
#        if session.poll_event('refresh'):
#            dirty = 2
#        if dirty:
#            if dirty == 2:
#                mailbox = get_header(msgs)
#            msg_selector = get_selector(mailbox, msg_selector)
#            idx = msg_selector.selection[0]
#            msg_reader = get_reader()
#            msg_reader.update(format_msg(msg_reader, idx))
#            echo(refresh(msg_reader, msg_selector, msgs, new))
#            dirty = 0
#        inp = getch(1)
#        if inp in (u'r', u'R'):
#            reply_to = get_msg(idx)
#            reply_msg = Msg()
#            reply_msg.recipient = reply_to.author
#            reply_msg.tags = reply_to.tags
#            reply_msg.subject = reply_to.subject
#            reply_msg.parent = reply_to.idx
#            # quote between 30 and 79, 'screen width - 4' as variable dist.
#            reply_msg.body = quote_body(reply_to,
#                                        max(30, min(79, term.width - 4)))
#            echo(term.move(term.height, 0) + u'\r\n')
#            if gosub('writemsg', reply_msg):
#                reply_msg.save()
#                dirty = 2
#                READING = False
#            else:
#                dirty = 1
#            mark_read(idx)  # also mark as read
#
#        # 't' uses writemsg.prompt_tags() routine, how confusing ..
#        elif inp in (u't',) and allow_tag(idx):
#            echo(term.move(term.height, 0))
#            msg = get_msg(idx)
#            if x84.default.writemsg.prompt_tags(msg):
#                msg.save()
#                session.user['msgs_sent'] = session.user.get('msgs_sent', 0) + 1
#            dirty = 2
#
#        # spacebar marks as read, goes to next message
#        elif inp in (u' ',):
#            dirty = 2 if mark_read(idx) else 1
#            msg_selector.move_down()
#            idx = msg_selector.selection[0]
#            READING = False
#
#        # D marks as deleted, goes to next message
#        elif inp in (u'D',):
#            dirty = 2 if mark_delete(idx) else 1
#            msg_selector.move_down()
#            idx = msg_selector.selection[0]
#            READING = False
#
#        # U undeletes, does not move.
#        elif inp in (u'U',):
#            dirty = 2 if mark_undelete(idx) else 1
#            msg_selector.move_down()
#            idx = msg_selector.selection[0]
#            READING = False
#
#        if READING:
#            echo(msg_reader.process_keystroke(inp))
#            # left, <, or backspace moves UI
#            if inp in (term.KEY_LEFT, u'<', u'h',
#                       '\b', term.KEY_BACKSPACE):
#                READING = False
#                dirty = 1
#        else:
#            echo(msg_selector.process_keystroke(inp))
#            idx = msg_selector.selection[0]
#            # right, >, or enter marks message read, moves UI
#            if inp in (u'\r', term.KEY_ENTER, u'>',
#                       u'l', 'L', term.KEY_RIGHT):
#                dirty = 2 if mark_read(idx) else 1
#                READING = True
#            elif msg_selector.moved:
#                dirty = 1
#    echo(term.move(term.height, 0) + u'\r\n')
#    return
