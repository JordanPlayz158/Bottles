# bottle_installers.py
#
# Copyright 2022 brombinmirko <send@mirko.pm>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, in version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging
import os.path
import time
import uuid
from typing import Optional

from gi.repository import Gtk, GLib, Adw

from bottles.backend.managers.dependency import DependencyManager
from bottles.backend.models.config import BottleConfig
from bottles.backend.state import EventManager, Events
from bottles.backend.utils.manager import ManagerUtils
from bottles.backend.utils.threading import RunAsync
from bottles.backend.wine.reg import Reg
from bottles.frontend.utils.filters import add_font_filters
from bottles.frontend.utils.gtk import GtkUtils
from bottles.frontend.widgets.dependency import DependencyEntry
from bottles.frontend.widgets.external_font import ExternalFontEntry


@Gtk.Template(resource_path='/com/usebottles/bottles/details-externalfonts.ui')
class ExternalFontsView(Adw.Bin):
    __gtype_name__ = 'DetailsExternalFonts'
    __registry = []

    # region Widgets
    list_fonts = Gtk.Template.Child()
    install_fonts = Gtk.Template.Child()
    group_fonts = Gtk.Template.Child()
    bottom_bar = Gtk.Template.Child()

    # endregion

    def __init__(self, details, config: BottleConfig, **kwargs):
        super().__init__(**kwargs)

        # common variables and references
        self.window = details.window
        self.manager = details.window.manager
        self.config = config
        self.queue = details.queue

        self.install_fonts.connect("clicked", self.add)

    def add(self, widget=False):
        """
        This function popup the add program dialog to the user. It
        will also update the bottle configuration, appending the
        path to the program picked by the user.
        The file chooser path is set to the bottle path by default.
        """

        def set_path(_dialog, response):
            if response != Gtk.ResponseType.ACCEPT:
                return

            path = dialog.get_file().get_path()
            basename = dialog.get_file().get_basename()

            if basename in self.config.External_Fonts:
                self.config.External_Fonts.remove(basename)
                self.uninstall_font(self.config, basename)

            self.config.External_Fonts.append(basename)

            self.config = self.manager.update_config(
                config=self.config,
                key="External_Fonts",
                value=self.config.External_Fonts,
            ).data["config"]

            self.install_font(path, basename)

            self.update(config=self.config)
            self.window.show_toast(_("\"{0}\" added").format(basename[:-4]))

        dialog = Gtk.FileChooserNative.new(
            title=_("Select Font"),
            action=Gtk.FileChooserAction.OPEN,
            parent=self.window,
            accept_label=_("Add")
        )

        add_font_filters(dialog)
        dialog.set_modal(True)
        dialog.connect("response", set_path)
        dialog.show()

    def add_font(self, widget):
        self.__registry.append(widget)
        self.group_fonts.remove(self.bottom_bar)  # Remove the bottom_bar
        self.group_fonts.add(widget)
        self.group_fonts.add(self.bottom_bar)  # Add the bottom_bar back to the bottom

    def remove_font(self, widget):
        self.__registry.remove(widget)
        self.group_fonts.remove(widget)

    def install_font(self, path, font):
        install_step = {
            "url": os.path.dirname(path),
            "fonts": [
                font
            ]
        }

        self.manager.dependency_manager._DependencyManager__step_install_fonts(self.config, install_step)
        self.manager.dependency_manager._DependencyManager__step_register_font(self.config, {"name": font[:-4], "file": font})

    def uninstall_font(self, config: BottleConfig, font: str):
        """Remove a font from the registry."""
        reg = Reg(config)
        reg.remove(
            key="HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts",
            value=font[:-4]
        )

        """THEN remove the font from the font folder."""
        bottle_path = ManagerUtils.get_bottle_path(config)

        font_path = f"{bottle_path}/drive_c/windows/Fonts/"
        if not os.path.exists(font_path):
            logging.warning(f"Font folder does not exist.")
            return

        try:
            os.remove(f"{font_path}/{font}")
        except FileNotFoundError:
            logging.warning(f"Font {font} was not found.")

    def empty_list(self):
        for r in self.__registry:
            if r.get_parent() is not None:
                r.get_parent().remove(r)
        self.__registry = []

    def update(self, widget=False, config: Optional[BottleConfig] = None):
        """
        This function update the dependencies list with the
        supported by the manager.
        """
        if config is None:
            config = BottleConfig()
        self.config = config

        def new_font(font, plain=False):
            entry = ExternalFontEntry(
                window=self.window,
                parent=self,
                config=self.config,
                font=font,
                plain=plain
            )
            self.add_font(entry)

        def process_fonts():
            time.sleep(.3)  # workaround for freezing bug on bottle load
            fonts = self.config.External_Fonts

            GLib.idle_add(self.empty_list)

            if len(fonts) > 0:
                for font in fonts:
                    GLib.idle_add(new_font, font, plain=True)

        RunAsync(process_fonts)
