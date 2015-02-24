# for localized messages
from . import _

from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigIP, NoSave, ConfigSubsection, config, ConfigSelection
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from plugin import VERSION
import os

config.plugins.ModifyPLiFullHD = ConfigSubsection()
config.plugins.ModifyPLiFullHD.skin = NoSave(ConfigSelection(default = "fullhd", choices = [("fullhd",_("PLi-FullHD")),("hd1",_("PLi-HD1"))]))
config.plugins.ModifyPLiFullHD.font = NoSave(ConfigSelection(default = "nmsbd", choices = [
	("nmsbd",_("Nemesis Bold Regular")),
	("LiberationSans-Regular",_("LiberationSans Regular")),
	("LiberationSans-Italic",_("LiberationSans Italic")),
	("LiberationSans-Bold",_("LiberationSans Bold")),
	("LiberationSans-BoldItalic",_("LiberationSans Bold Italic"))
	]))
config.plugins.ModifyPLiFullHD.toptemplatecolor = NoSave(ConfigIP(default=[0,0,0,48]))
config.plugins.ModifyPLiFullHD.basictemplatecolor = NoSave(ConfigIP(default=[0,0,0,32]))
config.plugins.ModifyPLiFullHD.selectorcolor = NoSave(ConfigIP(default=[0,0,0,48]))
config.plugins.ModifyPLiFullHD.transponderinfocolor = NoSave(ConfigIP(default=[0,0,144,240]))
config.plugins.ModifyPLiFullHD.selectedfgcolor = NoSave(ConfigIP(default=[0,252,192,0]))
config.plugins.ModifyPLiFullHD.yellowcolor = NoSave(ConfigIP(default=[0,255,192,0]))
config.plugins.ModifyPLiFullHD.secondfgcolor = NoSave(ConfigIP(default=[0,252,192,0]))

cfg = config.plugins.ModifyPLiFullHD

NAME = "/etc/enigma2/skin_user_PLi-FullHD"

class ModifyPLiFullHD(Screen, ConfigListScreen):
	skin = """
	<screen name="ModifyPLiFullHD" position="center,center" size="610,298" title="Modify PLi-FullHD - setup font and colors" backgroundColor="#31000000">
		<widget name="config" position="10,10" size="590,225" zPosition="1" backgroundColor="#31000000" scrollbarMode="showOnDemand"/>
		<ePixmap pixmap="skin_default/div-h.png" position="5,263" zPosition="2" size="600,2"/>
		<widget name="key_red"   position="005,269" zPosition="2" size="150,28" valign="center" halign="center" font="Regular;22" foregroundColor="red" transparent="1"/>
		<widget name="key_green" position="155,269" zPosition="2" size="150,28" valign="center" halign="center" font="Regular;22" foregroundColor="green" transparent="1"/>
		<widget name="key_blue"  position="455,269" zPosition="2" size="150,28" valign="center" halign="center" font="Regular;22" foregroundColor="blue" transparent="1"/>
		<widget name="info" position="5,237" size="600,25" font="Regular;20" halign="center" transparent="1"/>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		self.list = []
		self.onChangedEntry = []

		ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry )

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.keyCancel,
				"red": self.keyCancel,
				"green": self.keySave,
				"blue": self.recreate,
				"ok": self.keySave,
			}, -2)

		self["key_green"] = Label(_("Ok"))
		self["key_red"] = Label(_("Cancel"))
		self["key_blue"] = Label(_("Recreate"))
		self["info"]= Label(_("For new version must be used \"recreate\" at first"))
		self.title = _("Modify PLi-FullHD - setup font and colors") + _(" v%s") % VERSION
		self.setTitle(self.title)
		
		self.current_skin = config.skin.primary_skin.value.split('/')[0]
		self.setMenu()

	def setMenu(self):
		self.setSkinPath()
		if self.testFile():
			cfg.font.value = self.readFont()
			self.getColors()
		self.list = []
		self.skin_name = _("Skin")
		self.list.append(getConfigListEntry(self.skin_name, cfg.skin ))
		self.list.append(getConfigListEntry(_("Regular font"), cfg.font))
		self.list.append(getConfigListEntry(_("Top color (a,r,g,b)"), cfg.toptemplatecolor))
		self.list.append(getConfigListEntry(_("Bottom color (a,r,g,b)"), cfg.basictemplatecolor))
		self.list.append(getConfigListEntry(_("Selector color (a,r,g,b)"), cfg.selectorcolor))
		self.list.append(getConfigListEntry(_("TransponderInfo color (a,r,g,b)"), cfg.transponderinfocolor))
		self.list.append(getConfigListEntry(_("SelectedFG color (a,r,g,b)"), cfg.selectedfgcolor))
		self.list.append(getConfigListEntry(_("Yellow color (a,r,g,b)"), cfg.yellowcolor))
		self.list.append(getConfigListEntry(_("SecondFG color (a,r,g,b)"), cfg.secondfgcolor))

		self["config"].list = self.list

	def changedEntry(self):
		if self["config"].getCurrent()[0] is self.skin_name:
			self.setMenu()

	def setSkinPath(self):
		global NAME
		if cfg.skin.value == "hd1":
			NAME = "/etc/enigma2/skin_user_PLi-HD1"
		else:
			NAME = "/etc/enigma2/skin_user_PLi-FullHD"

	def testFile(self):
		try:
			fi = open("%s.xml" % NAME, "r")
		except:
			self.createUserSkinFile()
			return False
		else:
			fi.close()
			return True

	def setNewParameters(self):
		used_font = self.readFont()
		print "[ModifyPLiFullHD] set font %s instead of %s (%s)" % (cfg.font.value, used_font, cfg.font.description[used_font])
		os.rename("%s.xml" % NAME, "%s.tmp" % NAME)
		fi = open("%s.tmp" % NAME, "r")
		fo = open("%s.xml" % NAME, "w")
		top, bas, sel, tinfo, selfg, yellow, secfg = self.cfg2hexstring()
		for line in fi:
			if "<font name=\"Regular\" filename=" in line:
				line = line.replace(used_font, cfg.font.value)

			if "<color name=\"toptemplatecolor\" value=\"#" in line:
				pos = line.find("\"#")
				colors = line[pos+2:pos+10]
				line = line.replace("%s" %colors ,"%s" % top)
			if "<color name=\"basictemplatecolor\" value=\"#" in line:
				pos = line.find("\"#")
				colors = line[pos+2:pos+10]
				line = line.replace("%s" %colors ,"%s" % bas)
			if "<color name=\"selectorcolor\" value=\"#" in line:
				pos = line.find("\"#")
				colors = line[pos+2:pos+10]
				line = line.replace("%s" %colors ,"%s" % sel)
			if "<color name=\"transponderinfo\" value=\"#" in line:
				pos = line.find("\"#")
				colors = line[pos+2:pos+10]
				line = line.replace("%s" %colors ,"%s" % tinfo)
			if "<color name=\"selectedFG\" value=\"#" in line:
				pos = line.find("\"#")
				colors = line[pos+2:pos+10]
				line = line.replace("%s" %colors ,"%s" % selfg)
			if "<color name=\"yellow\" value=\"#" in line:
				pos = line.find("\"#")
				colors = line[pos+2:pos+10]
				line = line.replace("%s" %colors ,"%s" % yellow)
			if "<color name=\"secondFG\" value=\"#" in line:
				pos = line.find("\"#")
				colors = line[pos+2:pos+10]
				line = line.replace("%s" %colors ,"%s" % secfg)
			fo.write(line)
		fo.close()
		fi.close()
		os.unlink("%s.tmp" % NAME)

	def readFont(self):
		for line in open("%s.xml" % NAME, "r"):
			if "<font name=\"Regular\" filename=" in line:
				if "nmsbd.ttf" in line:
					return "nmsbd"
				if "LiberationSans-Regular.ttf" in line:
					return "LiberationSans-Regular"
				if "LiberationSans-Italic.ttf" in line:
					return "LiberationSans-Italic"
				if "LiberationSans-Bold.ttf" in line:
					return "LiberationSans-Bold"
				if "LiberationSans-BoldItalic.ttf" in line:
					return "LiberationSans-BoldItalic"
		return "nmsbd"

	def readColors(self):
		tcolors = None
		bcolors = None
		scolors = None
		ticolors = None
		selfgcolors = None
		yelcolors = None
		secfgcolors = None
		for line in open("%s.xml" % NAME, "r"):
			if "<color name=\"toptemplatecolor\" value=\"#" in line:
				pos = line.find("\"#")
				tcolors = line[pos+2:pos+10]
			if "<color name=\"basictemplatecolor\" value=\"#" in line:
				pos = line.find("\"#")
				bcolors = line[pos+2:pos+10]
			if "<color name=\"selectorcolor\" value=\"#" in line:
				pos = line.find("\"#")
				scolors = line[pos+2:pos+10]
			if "<color name=\"transponderinfo\" value=\"#" in line:
				pos = line.find("\"#")
				ticolors = line[pos+2:pos+10]
			if "<color name=\"selectedFG\" value=\"#" in line:
				pos = line.find("\"#")
				selfgcolors = line[pos+2:pos+10]
			if "<color name=\"yellow\" value=\"#" in line:
				pos = line.find("\"#")
				yelcolors = line[pos+2:pos+10]
			if "<color name=\"secondFG\" value=\"#" in line:
				pos = line.find("\"#")
				secfgcolors = line[pos+2:pos+10]
		return tcolors, bcolors, scolors, ticolors, selfgcolors, yelcolors, secfgcolors

	def getColors(self):
		top, bas, selector, t_info, selfg, yellow, secfg = self.readColors()
		if top is not None:
			cfg.toptemplatecolor.value = self.mapping(top)
		if bas is not None:
			cfg.basictemplatecolor.value = self.mapping(bas)
		if selector is not None:
			cfg.selectorcolor.value = self.mapping(selector)
		if t_info is not None:
			cfg.transponderinfocolor.value = self.mapping(t_info)
		if selfg is not None:
			cfg.selectedfgcolor.value = self.mapping(selfg)
		if yellow is not None:
			cfg.yellowcolor.value = self.mapping(yellow)
		if secfg is not None:
			cfg.secondfgcolor.value = self.mapping(secfg)

	def mapping(self, colorstring):
		return [int(colorstring[0:2],16),int(colorstring[2:4],16),int(colorstring[4:6],16),int(colorstring[6:8],16)]

	def cfg2hexstring(self):
		top = ""
		bas = ""
		sel = ""
		ti = ""
		selfg = ""
		yel = ""
		secfg = ""
		for i in range(0,4):
			top += "%02x" % cfg.toptemplatecolor.value[i]
			bas += "%02x" % cfg.basictemplatecolor.value[i]
			sel += "%02x" % cfg.selectorcolor.value[i]
			ti += "%02x" % cfg.transponderinfocolor.value[i]
			selfg += "%02x" % cfg.selectedfgcolor.value[i]
			yel += "%02x" % cfg.yellowcolor.value[i]
			secfg += "%02x" % cfg.secondfgcolor.value[i]
		return top, bas, sel, ti, selfg, yel, secfg

	def keySave(self):
		self.setSkinPath()
		self.setNewParameters()
		if self.current_skin == cfg.skin.description[cfg.skin.value] and self["config"].isChanged():
			restartbox = self.session.openWithCallback(self.applyCallback, MessageBox, _("GUI needs a restart to apply a new skin\nDo you want to restart the GUI now?"))
			restartbox.setTitle(self.title)
		else:
			self.close()

	def applyCallback(self, answer):
		if answer:
			self.session.open(TryQuitMainloop, 3)
		self.close()

	def keyCancel(self):
		if self["config"].isChanged():
			restartbox = self.session.openWithCallback(self.cancelCallback, MessageBox, _("Really close without apply changes?"))
			restartbox.setTitle(self.title)
		else:
			self.close()

	def cancelCallback(self, answer):
		if answer:
			for x in self["config"].list:
				x[1].cancel()
			self.close()

	def recreate(self):
		restartbox = self.session.openWithCallback(self.callbackRecreate, MessageBox, _("Are you sure delete and create new:\n%s?") % (NAME+".xml"))
		restartbox.setTitle(_("Modify PLi-FullHD - recreate user skin file"))

	def callbackRecreate(self, answer):
		if answer:
			os.rename("%s.xml" % NAME, "%s.bak" % NAME)
			self.setMenu()
		
	def createUserSkinFile(self):
		fi=open("%s.xml" % NAME, "w")
		fi.write(self.skinBegin())
		fi.write(self.fontsBegin())
		fi.write(self.fontName())
		fi.write(self.fontsEnd())
		fi.write(self.colorsBegin())
		fi.write(self.toptemplateColor())
		fi.write(self.basictemplateColor())
		fi.write(self.selectorColor())
		fi.write(self.transponderinfoColor())
		fi.write(self.selectedFGColor())
		fi.write(self.yellowColor())
		fi.write(self.secondFGColor())
		fi.write(self.colorsEnd())
		fi.write(self.windowStyleCode())
		fi.write(self.skinEnd())
		fi.close()

	def deleteUserSkinFile(self):
		os.unlink("%s.xml" % NAME)

	def skinBegin(self):
		return "<skin>\n"
	def skinEnd(self):
		return "</skin>\n"
	def fontsBegin(self):
		return("	<fonts>\n")
	def fontsEnd(self):
		return("	</fonts>\n")
	def fontName(self):
		return "		<font name=\"Regular\" filename=\"nmsbd.ttf\" scale=\"100\"/>\n"
	def colorsBegin(self):
		return("	<colors>\n")
	def colorsEnd(self):
		return("	</colors>\n")
	def toptemplateColor(self):
		return "		<color name=\"toptemplatecolor\" value=\"#00000030\"/>\n"
	def basictemplateColor(self):
		return "		<color name=\"basictemplatecolor\" value=\"#00000020\"/>\n"
	def selectorColor(self):
		return "		<color name=\"selectorcolor\" value=\"#00000030\"/>\n"
	def transponderinfoColor(self):
		return "		<color name=\"transponderinfo\" value=\"#000090f0\"/>\n"
	def selectedFGColor(self):
		return "		<color name=\"selectedFG\" value=\"#00fcc000\"/>\n"
	def yellowColor(self):
		return "		<color name=\"yellow\" value=\"#00ffc000\"/>\n"
	def secondFGColor(self):
		return "		<color name=\"secondFG\" value=\"#00fcc000\"/>\n"
	def windowStyleCode(self):
		return 	"	<windowstyle id=\"0\" type=\"skinned\">\n \
		<title offset=\"20,10\" font=\"Regular;20\"/>\n \
		<color name=\"Background\" color=\"background\"/>\n \
		<color name=\"LabelForeground\" color=\"foreground\"/>\n \
		<color name=\"ListboxBackground\" color=\"background\"/>\n \
		<color name=\"ListboxForeground\" color=\"foreground\"/>\n \
		<color name=\"ListboxSelectedBackground\" color=\"selectorcolor\"/>\n \
		<color name=\"ListboxSelectedForeground\" color=\"selectedFG\"/>\n \
		<color name=\"ListboxMarkedBackground\" color=\"un40a0aa0\"/>\n \
		<color name=\"ListboxMarkedForeground\" color=\"red\"/>\n \
		<color name=\"ListboxMarkedAndSelectedBackground\" color=\"un4a00a0a\"/>\n \
		<color name=\"ListboxMarkedAndSelectedForeground\" color=\"red\"/>\n \
		<color name=\"WindowTitleForeground\" color=\"foreground\"/>\n \
		<color name=\"WindowTitleBackground\" color=\"background\"/>\n \
		<borderset name=\"bsWindow\">\n \
			<pixmap filename=\"PLi-HD/window/top_left_corner.png\" pos=\"bpTopLeft\"/>\n \
			<pixmap filename=\"PLi-HD/window/top_edge.png\" pos=\"bpTop\"/>\n \
			<pixmap filename=\"PLi-HD/window/top_right_corner.png\" pos=\"bpTopRight\"/>\n \
			<pixmap filename=\"PLi-HD/window/left_edge.png\" pos=\"bpLeft\"/>\n \
			<pixmap filename=\"PLi-HD/window/right_edge.png\" pos=\"bpRight\"/>\n \
			<pixmap filename=\"PLi-HD/window/bottom_left_corner.png\" pos=\"bpBottomLeft\"/>\n \
			<pixmap filename=\"PLi-HD/window/bottom_edge.png\" pos=\"bpBottom\"/>\n \
			<pixmap filename=\"PLi-HD/window/bottom_right_corner.png\" pos=\"bpBottomRight\"/>\n \
		</borderset>\n \
		<borderset name=\"bsListboxEntry\">\n \
		<pixmap filename=\"PLi-FullHD/border/line.png\" pos=\"bpTop\"/>\n \
		<pixmap filename=\"PLi-FullHD/border/line.png\" pos=\"bpBottom\"/>\n \
		<pixmap filename=\"PLi-FullHD/border/vline.png\" pos=\"bpLeft\"/>\n \
		<pixmap filename=\"PLi-FullHD/border/vline.png\" pos=\"bpRight\"/>\n \
		</borderset>\n \
	</windowstyle>\n"

	def isWindowsStyle(self):
		fi = open("%s.xml" % NAME, "r")
		for line in fi:
			if "<windowstyle id=\"0\" type=\"skinned\">" in line:
				return True
		return False
