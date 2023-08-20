# external_font.py
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

from gi.repository import Gtk, Adw

from bottles.backend.models.config import BottleConfig

@Gtk.Template(resource_path='/com/usebottles/bottles/external-font-entry.ui')
class ExternalFontEntry(Adw.ActionRow):
    __gtype_name__ = 'ExternalFontEntry'

    # region Widgets
    btn_remove = Gtk.Template.Child()

    # endregion

    def __init__(self, window, parent, config: BottleConfig, font, plain=False, **kwargs):
        super().__init__(**kwargs)

        # common variables and references
        self.window = window
        self.parent = parent
        self.manager = window.manager
        self.config = config
        self.font = font
        self.queue = window.page_details.queue

        # populate widgets
        self.set_title(self.font[:-4])
        self.set_subtitle(self.font)

        if plain:
            '''
            If the font is plain, treat it as a placeholder, it
            can be used to display "fake" elements on the list
            '''
            self.btn_remove.set_visible(False)
            return

        # connect signals
        self.btn_remove.connect("clicked", self.uninstall_font)

    def uninstall_font(self, *xargs):
        self.parent.uninstall_font(config=self.config, font=self.font)
        self.config.External_Fonts.remove(self.font)
        self.config = self.manager.update_config(
            config=self.config,
            key="External_Fonts",
            value=self.config.External_Fonts,
        ).data["config"]
        self.parent.update(config=self.config)
