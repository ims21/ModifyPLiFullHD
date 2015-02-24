# for localized messages
from . import _
#################################################################################
#
#    Plugin for Enigma2
#    version:
VERSION = "1.05"
#    Coded by ims (c)2015
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#################################################################################

from Plugins.Plugin import PluginDescriptor

def main(session,**kwargs):
	import ui
	session.open(ui.ModifyPLiFullHD)

def Plugins(path, **kwargs):
	name = _("Modify PLi-FullHD")
	descr = _("Change regular font and colors in PLi-FullHD/PLi-HD1 skin")
	return PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_PLUGINMENU, icon = 'plugin.png', fnc=main)
