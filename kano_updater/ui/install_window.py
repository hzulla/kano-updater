
# install_window.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Installer main window
#

import os
from gi.repository import Gtk, Gdk, GLib
from threading import Thread

from kano.gtk3.apply_styles import apply_styling_to_screen
from kano.gtk3.kano_dialog import KanoDialog

from kano_updater.utils import kill_apps
from kano_updater.ui.paths import CSS_PATH
from kano_updater.commands.install import install
from kano_updater.ui.progress import GtkProgress
from kano_updater.ui.views.install import Install
from kano_updater.ui.views.restart import Restart


class InstallWindow(Gtk.Window):
    CSS_FILE = os.path.join(CSS_PATH, 'updater.css')

    def __init__(self):
        # Apply styling to window
        apply_styling_to_screen(self.CSS_FILE)

        Gtk.Window.__init__(self)
        self.fullscreen()
        self.set_keep_above(True)

        self.set_icon_name('kano-updater')
        self.set_title(_('Updater'))

        self._install_screen = Install()
        self.add(self._install_screen)

        kill_apps()

        self.show_all()
        self._set_wait_cursor()

        self._start_install()

    def _start_install(self):
        progress = GtkProgress(self)

        self._timer_tag = GLib.timeout_add_seconds(60, self._is_install_running)

        self._install_thread = Thread(target=install, args=(progress,))
        # FIXME: What to do when the gui is killed
        #        and the thread is still running?
        self._install_thread.daemon = True
        self._install_thread.start()

    def _is_install_running(self):
        if self._install_thread.is_alive():
            return True

        self.destroy()
        self._set_normal_cursor()

        unexpected_quit = KanoDialog(
            _('The install unexpectantly quit'),
            _('Please try again later'),
            {
                'OK': {
                    'return_value': True,
                    'color': 'red'
                }
            })
        unexpected_quit.run()

        self.close_window()

        return False

    def _done_install(self, *_):
        self._install_thread.join()
        GLib.source_remove(self._timer_tag)

        for child in self.get_children():
            self.remove(child)

        reboot_screen = Restart()
        self.add(reboot_screen)

        self.show_all()

    def _no_updates(self):
        self.destroy()
        self._set_normal_cursor()

        no_updates = KanoDialog(
            _('No updates available'),
            _('Your system is already up to date'),
            {
                'OK': {
                    'return_value': True,
                    'color': 'green'
                }
            })
        no_updates.run()

        self.close_window()

    def close_window(self, widget=None, event=None):
        Gtk.main_quit()

    def update_progress(self, percent, msg, sub_msg=''):
        self._install_screen.update_progress(percent, msg, sub_msg)

        # FIXME Progress to next with the done
        if percent == 100:
            if sub_msg == _('Update completed'):
                self._done_install()
            elif sub_msg == _('No updates to download'):
                self._no_updates()

    def error(self, msg):
        error = KanoDialog(
            _('Error updating'), msg,
            {
                'CLOSE': {
                    'return_value': True,
                    'color': 'red'
                }
            },
            parent_window=self)
        error.run()
        # FIXME: This close doesn't work for some reason
        self.close_window()

    def _set_wait_cursor(self):
        cursor = Gdk.Cursor.new(Gdk.CursorType.WATCH)
        self.get_root_window().set_cursor(cursor)

    def _set_normal_cursor(self):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
