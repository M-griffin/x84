"""
 New user account script for X/84, http://1984.ws
 $Id: nua.py,v 1.6 2010/01/02 01:03:10 dingo Exp $

 Simply create a new User() instance and set the most minimum values,
 handle and password, then call the .add() method to commit this record.

"""
__author__ = 'Jeffrey Quast <dingo@1984.ws>'
__copyright__ = ['Copyright (c) 2009 Jeffrey Quast']
__license__ = 'ISC'
__url__ = 'http://1984.ws'

deps = ['bbs']

def init():
  pass # nothing to initialize

def warning(string, x, y, clean=True):
  " Display warning to user with a dynamic pause "
  cpsec =  13.0   # characters per second to pause for, sleep(len(string)/cps)
  split_loc = 3   # characters from right to split for two-tone shading
  warning_msg = \
    attr(NORMAL) + color(RED) + string[:-split_loc] \
    + color() + string[-split_loc:] \
    + color(BLACK, BRIGHT) + '! '
  echo ( cl() + pos (x, y) + warning_msg )
  inkey = readkeyto ( float( len( string)) /cpsec) # pause
  echo (pos (x, y) + ' '*ansilen(warning_msg) ) # clear
  return inkey # return keypress, if any

def main (user):
  if user.lower() == 'new':
    user == ''
  location, hint = '', ''
  password, verify, = '', ''

  # input area (x, y)
  loc_user   = (20, 16)
  loc_origin = (20, 17)
  loc_pass   = (20, 18)
  loc_email  = (20, 19)
  loc_state  = (10, 20)
  loc_prompt = (35, 22)

  getsession().activity = 'New User Application'
  echo (cls() + color() + pos(1, 1))
  showfile ('art/newuser.asc')
  echo ( pos(40 -(ansilen(getsession().activity)/2), 14) + getsession().activity)

  while True:
    user_ok, origin_ok, pass_ok, email_ok = False, False, False, 0

    while not (user_ok):
      echo (pos(*loc_user) + cl() + color() + 'username: ')
      user = readline (cfg.max_user, user)
      if not user:
        if warning ('Enter an alias, Press Ctrl+X to cancel', *loc_origin) == chr(24):
          return
      elif userexist (user):
        warning ('User exists', *loc_origin)
      elif user == '' or len(user) < cfg.min_user:
        warning ('Too short! (%i)' % cfg.min_user, *loc_origin)
      elif user.lower() in cfg.invalid_handles:
        warning ('Illegal username', *loc_origin)
      else:
        user_ok = True

    while not (origin_ok):
      echo (pos(*loc_origin) + color() + 'origin: ')
      location = readline (cfg.max_origin, location)
      if location == '':
        if warning ('Enter a location, Press Ctrl+X to cancel', *loc_pass) == chr(24):
          return
        echo (cl())
      else:
        origin_ok = True

    while not (pass_ok):
      echo (pos(*loc_pass) + cl() + color() + 'password: ')
      password = readline (cfg.max_pass, hidden='x')
      if len(password) < 4:
        # fail if password too short
        if warning ('too short, Press Ctrl+X to cancel', *loc_email) == chr(24):
          return
        echo (cl())
      else:
        # verify
        echo (pos(*loc_pass) + cl() + color() + '   again: ')
        verify = readline (cfg.max_pass, hidden='z')
        if password != verify:
          if warning ('verify must match, Press Ctrl+X to cancel', *loc_email) == chr(24):
            return
          echo (cl())
        else:
          break

    while (email_ok < 2):
      email_ok = 0
      # email loop
      echo (pos(*loc_email) + cl() + color() + 'email address: ')
      hint = readline (cfg.max_email)
      for ch in hint:
        # must have @, level 1
        if ch == '@':
          email_ok = 1
        # must have '.' following @, level 2
        if email_ok == 1 and ch == '.':
          email_ok = 2

      if email_ok == 2:
        # email is valid, break out
        break

      # allow user to opt-out of e-mail
      if warning ('invalid, Ctrl+O to Opt out', *loc_state) == chr(15):
        # oh yea? make a statement, then
        echo (pos(*loc_state) + cl() + color() + 'make your statement, then: ')
        hint = readline (cfg.max_email)
        if not hint:
          # if you don't make a statement, forget you!
          disconnect ()
        break

    echo (pos(35, 23) + cl() + color() + 'Everything cool?')
    lr = YesNoClass([62,23])
    lr.left ()
    lr.run()
    if lr.isleft():
      u = User ()
      u.handle = user
      u.password = password
      u.location = location
      u.hint = hint
      u.add ()
      goto ('top', user)
