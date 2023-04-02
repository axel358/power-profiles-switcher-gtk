#!/usr/bin/env python3
import sys
import gi
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class PowerProfilesSwitcher(Gtk.Application):
    def __init__(self, *args, **kargs):
        super().__init__(*args, application_id='cu.axel.PowerProfiles', **kargs)

        icon_theme = Gtk.IconTheme.get_default()
        icon_theme.append_search_path('/usr/share/power-profiles-switcher/icons')

        self.builder = Gtk.Builder.new_from_file('/usr/share/power-profiles-switcher/window.ui')

        self.ps_button = self.builder.get_object('ps_button')
        self.balanced_button = self.builder.get_object('balanced_button')
        self.performance_button = self.builder.get_object('performance_button')
        self.performance_button.set_sensitive(self.supports_performance_profile())
        self.profiles_combobox = self.builder.get_object('profiles_combobox')
        self.command_entry = self.builder.get_object('command_entry')

        active_profile = self.get_active_profile()

        self.balanced_button.set_active('balanced' in active_profile)
        self.performance_button.set_active('performance' in active_profile)

        self.ps_button.connect('toggled', self.set_active_profile, 'power-saver')
        self.balanced_button.connect('toggled', self.set_active_profile, 'balanced')
        self.performance_button.connect('toggled', self.set_active_profile, 'performance')

        self.builder.connect_signals(self)
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = self.builder.get_object('main_window')
            self.window.set_application(self)

        self.window.show_all()

    def on_launch_clicked(self, button):
        self.run_with_profile(self.command_entry.get_text(), self.profiles_combobox.get_active_id())

    def run_cmd(self, args: list):
        try:
            subprocess.run(args)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def run_with_profile(self, command: str, profile: str):
        try:
            subprocess.Popen('powerprofilesctl launch --profile ' + profile + ' ' + command, shell=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_output(self, args: list) -> str:
        try:
            return subprocess.check_output(args).strip().decode("utf-8")
        except (subprocess.CalledProcessError, FileNotFoundError):
            return 'error'

    def supports_performance_profile(self) -> bool:
        return 'performance' in self.check_output(['powerprofilesctl', 'list'])

    def get_active_profile(self) -> str:
        return self.check_output(['powerprofilesctl', 'get'])

    def set_active_profile(self, widget, profile: str):
        if widget.get_active():
            self.run_cmd(['powerprofilesctl', 'set', profile])

    def show_about_dialog(self, button):
        dialog = Gtk.AboutDialog()
        dialog.props.program_name = 'Power Profiles'
        dialog.props.version = "0.1.0"
        dialog.props.authors = ['Axel358']
        dialog.props.copyright = 'GPL-3'
        dialog.props.logo_icon_name = 'cu.axel.PowerProfiles'
        dialog.props.comments = 'Control Power Profiles'
        dialog.props.website = 'https://github.com/axel358/power-profiles-switcher-gtk'
        dialog.set_transient_for(self.window)
        dialog.show()


if __name__ == "__main__":
    app = PowerProfilesSwitcher()
    app.run(sys.argv)
