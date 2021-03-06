
# restart.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Restart computer widget
#

from gi.repository import Gtk
import os
from threading import Timer

from kano_updater.ui.views.countdown import Countdown

class Restart(Countdown):
    def __init__(self):
        Countdown.__init__(self)

        complete = Gtk.Label(_('Update complete!'))
        complete.get_style_context().add_class('complete')

        info = Gtk.Label(_('Your Kano is up to date and \n'
                           'will automatically restart in 10 seconds'))
        info.set_justify(Gtk.Justification.CENTER)
        info.get_style_context().add_class('countdown')

        instructions = Gtk.Label(_('Press ENTER to restart now'))
        instructions.get_style_context().add_class('restart-now')

        self._main_grid.attach(complete, 0, 1, 1, 1)
        self._main_grid.attach(info, 0, 2, 1, 1)
        self._main_grid.attach(instructions, 0, 3, 1, 1)

        self.connect('show', self._on_show)

    def _on_show(self, widget=None):
        self.get_toplevel().connect('key-press-event', self._reboot)
        self._start_timer()

    def _start_timer(self):
        timer = Timer(11, self._reboot, ())
        timer.daemon = True
        timer.start()

    def _reboot(self, window=None, event=None):
        if event and event.get_keycode()[1] != 36: # ENTER
            return

        os.system('reboot')
