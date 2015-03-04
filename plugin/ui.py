# for localized messages
from . import _

from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigIP, NoSave, ConfigSubsection, config, ConfigSelection, ConfigYesNo
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from plugin import VERSION
import os
import skin
import enigma
from Tools.Directories import resolveFilename, SCOPE_CONFIG
import xml.etree.cElementTree as ET

cfg = config.plugins.ModifyPLiFullHD
cfg.skin = NoSave(ConfigSelection(default = "PLi-FullHD", choices = [("PLi-FullHD","PLi-FullHD"),("PLi-HD1","PLi-HD1")]))
cfg.font = NoSave(ConfigSelection(default = "nmsbd.ttf", choices = [
	("nmsbd.ttf","Nemesis Bold Regular"),
	("LiberationSans-Regular.ttf","LiberationSans Regular"),
	("LiberationSans-Italic.ttf","LiberationSans Italic"),
	("LiberationSans-Bold.ttf","LiberationSans Bold"),
	("LiberationSans-BoldItalic.ttf","LiberationSans Bold Italic")
	]))
cfg.toptemplatecolor = NoSave(ConfigIP(default=[0,0,0,48]))
cfg.basictemplatecolor = NoSave(ConfigIP(default=[0,0,0,32]))
cfg.selectorcolor = NoSave(ConfigIP(default=[0,0,0,48]))
cfg.transponderinfocolor = NoSave(ConfigIP(default=[0,0,144,240]))
cfg.selectedfgcolor = NoSave(ConfigIP(default=[0,252,192,0]))
cfg.yellowcolor = NoSave(ConfigIP(default=[0,255,192,0]))
cfg.redcolor = NoSave(ConfigIP(default=[0,250,64,16]))
cfg.secondfgcolor = NoSave(ConfigIP(default=[0,252,192,0]))
cfg.fallbackcolor = NoSave(ConfigIP(default=[0,176,176,192]))
cfg.notavailablecolor = NoSave(ConfigIP(default=[0,94,94,94]))
cfg.selector_vertical = ConfigSelection(default = "both", choices = [("both",_("both")),("left",_("left only")),("right",_("right only")),("no",_("none"))])

XML_NAME = "PLi-FullHD_Pars.xml"
XML_FILE = resolveFilename(SCOPE_CONFIG, XML_NAME)

reload_skin_on_start = True

class ModifyPLiFullHD(Screen, ConfigListScreen):
	skin = """
	<screen name="ModifyPLiFullHD" position="center,center" size="610,323" title="Modify PLi-FullHD - setup font and colors" backgroundColor="#31000000">
		<widget name="config" position="10,10" size="590,250" zPosition="1" backgroundColor="#31000000" scrollbarMode="showOnDemand"/>
		<ePixmap pixmap="skin_default/div-h.png" position="5,288" zPosition="2" size="600,2"/>
		<widget name="key_red"   position="005,294" zPosition="2" size="150,28" valign="center" halign="center" font="Regular;22" foregroundColor="red" transparent="1"/>
		<widget name="key_green" position="155,294" zPosition="2" size="150,28" valign="center" halign="center" font="Regular;22" foregroundColor="green" transparent="1"/>
		<widget name="key_yellow" position="305,294" zPosition="2" size="150,28" valign="center" halign="center" font="Regular;22" foregroundColor="yellow" transparent="1"/>
		<widget name="key_blue"  position="455,294" zPosition="2" size="150,28" valign="center" halign="center" font="Regular;22" foregroundColor="blue" transparent="1"/>
		<widget name="info" position="5,262" size="600,25" font="Regular;20" halign="center" transparent="1"/>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		self.list = []
		self.onChangedEntry = []
		self.session = session
		ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry )

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.keyCancel,
				"red": self.keyCancel,
				"green": self.keySave,
				"yellow": self.applyFont,
				"blue": self.showFileOptions,
			}, -2)
		self.selection = 0

		self["key_green"] = Label(_("Ok"))
		self["key_red"] = Label(_("Cancel"))
		self["key_yellow"] = Label(_("Now"))
		self["key_blue"] = Label(_("Options"))
		self["info"]= Label()

		self.title = _("Modify PLi-FullHD - setup font and colors") + _(" - v.%s") % VERSION
		self.wrong_xml = False

		self.setTitle(self.title)
		self.current_skin = config.skin.primary_skin.value.split('/')[0]

		cfg.skin.value = self.current_skin
		self.onLayoutFinish.append(self.loadMenu)

	def loadMenu(self):
		self.list = []
		self["info"].setText("")

		self.setSkinPath()

		if self.testFile():
			if self.isParseable():
				cfg.font.value = self.parseFont()
				self.parseColors()
			else:
				self["info"].setText(_("!!! Invalid format: %s, not used !!!") % XML_NAME)
		else:
			self["info"].setText(_("Was created new config file, restart for apply."))
			self.createDefaultCfgFile()

		self.skin_enabled = _("Use modify skin")
		self.skin_name = _("Skin")
		self.list.append(getConfigListEntry(self.skin_enabled ,cfg.enabled))
		if cfg.enabled.value:
			self.list.append(getConfigListEntry(self.skin_name, cfg.skin ))
			self.list.append(getConfigListEntry(_("Regular font"), cfg.font))
			self.list.append(getConfigListEntry(_("Top color  (a,r,g,b)"), cfg.toptemplatecolor))
			self.list.append(getConfigListEntry(_("Selector color  (a,r,g,b)"), cfg.selectorcolor))
			self.list.append(getConfigListEntry(_("Bottom color  (a,r,g,b)"), cfg.basictemplatecolor))
			self.list.append(getConfigListEntry(_("Vertical selector's lines"), cfg.selector_vertical))
			self.list.append(getConfigListEntry(_("SelectedFG color  (a,r,g,b)"), cfg.selectedfgcolor))
			self.list.append(getConfigListEntry(_("SecondFG color  (a,r,g,b)"), cfg.secondfgcolor))
			self.list.append(getConfigListEntry(_("Yellow color  (a,r,g,b)"), cfg.yellowcolor))
			self.list.append(getConfigListEntry(_("TransponderInfo color  (a,r,g,b)"), cfg.transponderinfocolor))
			self.list.append(getConfigListEntry(_("Red color  (a,r,g,b)"), cfg.redcolor))
			self.list.append(getConfigListEntry(_("Fallback color  (a,r,g,b)"), cfg.fallbackcolor))
			self.list.append(getConfigListEntry(_("Notavailable color  (a,r,g,b)"), cfg.notavailablecolor))

		self["config"].list = self.list

	def changedEntry(self):
		if self["config"].getCurrent()[0] in (self.skin_name, self.skin_enabled):
			self.loadMenu()

	def setSkinPath(self):
		global XML_NAME, XML_FILE
		XML_NAME = "PLi-FullHD_Pars.xml"
		if cfg.skin.value == "PLi-HD1":
			XML_NAME = "PLi-HD1_Pars.xml"
		XML_FILE = resolveFilename(SCOPE_CONFIG, XML_NAME)

	def testFile(self):
		try:
			fi = open(XML_FILE, "r")
		except:
			return False
		else:
			fi.close()
			return True

	def saveParametersToFile(self):
		toptemplate, basictemplate, selector, transponderinfo, selectedfg, yellow, red, secondfg, fallback, notavailable = self.getColorsFromCfg()

		def addMark(value):
			return "#" + value

		tree = ET.ElementTree()
		tree.parse(XML_FILE)
		colors = tree.find('colors')
		for color in colors:
			name = color.attrib.get('name', None)
			if name == "toptemplatecolor":
				color.set('value', addMark(toptemplate))
			if name == "basictemplatecolor":
				color.set('value', addMark(basictemplate))
			if name == "selectorcolor":
				color.set('value', addMark(selector))
			if name == "transponderinfo":
				color.set('value', addMark(transponderinfo))
			if name == "selectedFG":
				color.set('value', addMark(selectedfg))
			if name == "yellow":
				color.set('value', addMark(yellow))
			if name == "red":
				color.set('value', addMark(red))
			if name == "secondFG":
				color.set('value', addMark(secondfg))
			if name == "fallback":
				color.set('value', addMark(fallback))
			if name == "notavailable":
				color.set('value', addMark(notavailable))
		fonts = tree.find('fonts')
		for font in fonts:
			name = font.attrib.get('name', None)
			if name == "Regular":
				font.set('filename', cfg.font.value)
				print "[ModifyPLiFullHD] set font %s instead of %s" % (cfg.font.value, self.parseFont())

		fo = open(XML_FILE, "w")
		tree.write(fo, encoding='utf-8', xml_declaration=None, default_namespace=None, method="xml")

	def parseFont(self):
		root = ET.parse(XML_FILE).getroot()
		fonts = root.find('fonts')
		for font in fonts:
			name = font.attrib.get('name', None)
			if name == "Regular":
				filename = font.attrib.get('filename', None)
				if filename:
					return filename
		return "nmsbd.ttf"

	def parseColors(self):
		root = ET.parse(XML_FILE).getroot()
		colors = root.find('colors')
		for color in colors:
			name = color.attrib.get('name', None)
			value = color.attrib.get('value', None).lstrip('#')

			if name == "toptemplatecolor":
				cfg.toptemplatecolor.value = self.map(value)
			if name == "basictemplatecolor":
				cfg.basictemplatecolor.value = self.map(value)
			if name == "selectorcolor":
				cfg.selectorcolor.value = self.map(value)
			if name == "transponderinfo":
				cfg.transponderinfocolor.value = self.map(value)
			if name == "selectedFG":
				cfg.selectedfgcolor.value = self.map(value)
			if name == "yellow":
				cfg.yellowcolor.value = self.map(value)
			if name == "red":
				cfg.redcolor.value = self.map(value)
			if name == "secondFG":
				cfg.secondfgcolor.value = self.map(value)
			if name == "fallback":
				cfg.fallbackcolor.value = self.map(value)
			if name == "notavailable":
				cfg.notavailablecolor.value = self.map(value)

	def map(self, colorstring):
		return [int(colorstring[0:2],16),int(colorstring[2:4],16),int(colorstring[4:6],16),int(colorstring[6:8],16)]

	def getColorsFromCfg(self):
		toptemplate = self.l2h(cfg.toptemplatecolor.value)
		basictemplate = self.l2h(cfg.basictemplatecolor.value)
		selector = self.l2h(cfg.selectorcolor.value)
		transponderinfo = self.l2h(cfg.transponderinfocolor.value)
		selectedfg = self.l2h(cfg.selectedfgcolor.value)
		yellow = self.l2h(cfg.yellowcolor.value)
		red = self.l2h(cfg.redcolor.value)
		secondfg = self.l2h(cfg.secondfgcolor.value)
		fallback = self.l2h(cfg.fallbackcolor.value)
		notavailable = self.l2h(cfg.notavailablecolor.value)

		return toptemplate, basictemplate, selector, transponderinfo, selectedfg, yellow, red, secondfg, fallback, notavailable

	def l2h(self, l):
		return "%02x%02x%02x%02x" % (l[0],l[1],l[2],l[3])

	def keySave(self):
		self.setSkinPath()
		self.saveParametersToFile()
		if self["config"].isChanged() and self.current_skin == cfg.skin.value:
			self.saveConfig()
			restartbox = self.session.openWithCallback(self.applyCallback, MessageBox, _("GUI needs a restart to apply a new skin\nDo you want to restart the GUI now?"))
			restartbox.setTitle(self.title)
		else:
			self.saveConfig()
			self.close()

	def applyCallback(self, answer):
		if answer:
			self.session.open(TryQuitMainloop, 3)
		self.close()

	def saveConfig(self):
		cfg.enabled.save()
		cfg.selector_vertical.save()

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

	def deleteParseFile(self, name):
		os.unlink(name)

	def isParseable(self):
		try:
			root = ET.parse(XML_FILE).getroot()
		except:
			print "[ModifyPLiFullHD] ERROR - file %s corrupted ?" % XML_FILE
			self.wrong_xml = True
			return False
		else:
			self.wrong_xml = False
			return True

	def applyFont(self):
		self.saveConfig()
		self.setSkinPath()
		self.saveParametersToFile()
		self.reloadSkin()
		self.reloadChanellSelection()
		self.close()

	def reloadChanellSelection(self):
		import Screens.InfoBar
		screen = Screens.InfoBar.InfoBar.instance.servicelist
		screen.applySkin()
		screen.setMode()

	def applyAutorun(self):
		self.disableAutorun()
		self.setSkinPath()
		if self.testFile():
			if self.isParseable():
				self.reloadSkin()
		else:
			self.createDefaultCfgFile()
			if self.isParseable():
				self.reloadSkin()

	def disableAutorun(self):
		global reload_skin_on_start
		reload_skin_on_start = False

	def reloadSkin(self):
		path = os.path.dirname(XML_FILE) + "/"
		print "[ModifyPLiFullHD] parsing %s" % XML_FILE

		# remove disabled items in plugin's setup from xml before reloading skin
		root = ET.parse(XML_FILE).getroot()
		windowstyle = root.find('windowstyle')
		for borderset in windowstyle.findall("borderset"):
			for pixmap in borderset.findall("pixmap"):
				if borderset.attrib.get("name", None) == "bsListboxEntry":
					if pixmap.attrib.get("pos") == "bpLeft":
						if cfg.selector_vertical.value in ("no", "right"):
							borderset.remove(pixmap)
					if pixmap.attrib.get("pos") ==  "bpRight":
						if cfg.selector_vertical.value in ("no", "left"):
							borderset.remove(pixmap)
		# call reload skin
		skin.loadSingleSkinData(enigma.getDesktop(0), root, path)
		for elem in root:
			if elem.tag == 'screen':
				name = elem.attrib.get('name', None)
				if name:
					sid = elem.attrib.get('id', None)
					if sid and (sid != skin.display_skin_id):
						elem.clear()
						continue
					if name in skin.dom_screens:
						skin.dom_screens[name][0].clear()
					skin.dom_screens[name] = (elem, path)
				else:
					elem.clear()
			else:
				elem.clear()

	def line(self, name):
		return "%s/border/%s.png" % (cfg.skin.value, name)

	def createDefaultCfgFile(self):

		def indent(elem, level=0):
			i = "\n" + level*"  "
			if len(elem):
				if not elem.text or not elem.text.strip():
					elem.text = i + "  "
				if not elem.tail or not elem.tail.strip():
					elem.tail = i
				for elem in elem:
					indent(elem, level+1)
				if not elem.tail or not elem.tail.strip():
					elem.tail = i
			else:
				if level and (not elem.tail or not elem.tail.strip()):
					elem.tail = i

		root = ET.Element('skin')

		fonts = ET.SubElement(root, 'fonts')
		ET.SubElement( fonts, 'font', filename="LiberationSans-Regular.ttf", name="Regular", scale="100")

		colors = ET.SubElement(root, 'colors')
		ET.SubElement( colors, 'color', name="toptemplatecolor", value="#00000030")
		ET.SubElement( colors, 'color', name="basictemplatecolor", value="#00000020")
		ET.SubElement( colors, 'color', name="selectorcolor", value="#00000030")
		ET.SubElement( colors, 'color', name="transponderinfo", value="#000090f0")
		ET.SubElement( colors, 'color', name="selectedFG", value="#00fcc000")
		ET.SubElement( colors, 'color', name="yellow", value="#00ffc000")
		ET.SubElement( colors, 'color', name="red", value="#00fa4010")
		ET.SubElement( colors, 'color', name="secondFG", value="#00fcc000")
		ET.SubElement( colors, 'color', name="fallback", value="#00b0b0c0")
		ET.SubElement( colors, 'color', name="notavailable", value="#005e5e5e")

		windowstyle = ET.SubElement(root, 'windowstyle', id="0", type="skinned")
		ET.SubElement( windowstyle, 'title', offset="20,10", font="Regular;20")
		ET.SubElement( windowstyle, 'color', name="Background", color="background")
		ET.SubElement( windowstyle, 'color', name="LabelForeground", color="foreground")
		ET.SubElement( windowstyle, 'color', name="ListboxBackground", color="background")
		ET.SubElement( windowstyle, 'color', name="ListboxForeground", color="foreground")
		ET.SubElement( windowstyle, 'color', name="ListboxSelectedBackground", color="selectorcolor")
		ET.SubElement( windowstyle, 'color', name="ListboxSelectedForeground", color="selectedFG")
		ET.SubElement( windowstyle, 'color', name="ListboxMarkedBackground", color="un40a0aa0")
		ET.SubElement( windowstyle, 'color', name="ListboxMarkedForeground", color="red")
		ET.SubElement( windowstyle, 'color', name="ListboxMarkedAndSelectedBackground", color="un4a00a0a")
		ET.SubElement( windowstyle, 'color', name="ListboxMarkedAndSelectedForeground", color="red")
		ET.SubElement( windowstyle, 'color', name="WindowTitleForeground", color="foreground")
		ET.SubElement( windowstyle, 'color', name="WindowTitleBackground", color="background")

		bswindow = ET.SubElement( windowstyle, 'borderset', name="bsWindow")
		ET.SubElement( bswindow, 'pixmap', filename="PLi-HD/window/top_left_corner.png", pos="bpTopLeft")
		ET.SubElement( bswindow, 'pixmap', filename="PLi-HD/window/top_edge.png", pos="bpTop")
		ET.SubElement( bswindow, 'pixmap', filename="PLi-HD/window/top_right_corner.png", pos="bpTopRight")
		ET.SubElement( bswindow, 'pixmap', filename="PLi-HD/window/left_edge.png", pos="bpLeft")
		ET.SubElement( bswindow, 'pixmap', filename="PLi-HD/window/right_edge.png", pos="bpRight")
		ET.SubElement( bswindow, 'pixmap', filename="PLi-HD/window/bottom_left_corner.png", pos="bpBottomLeft")
		ET.SubElement( bswindow, 'pixmap', filename="PLi-HD/window/bottom_edge.png", pos="bpBottom")
		ET.SubElement( bswindow, 'pixmap', filename="PLi-HD/window/bottom_right_corner.png", pos="bpBottomRight")

		bslistboxentry = ET.SubElement( windowstyle, 'borderset', name="bsListboxEntry")
		ET.SubElement( bslistboxentry, 'pixmap', filename=self.line("line"), pos="bpTop")
		ET.SubElement( bslistboxentry, 'pixmap', filename=self.line("line"), pos="bpBottom")
		ET.SubElement( bslistboxentry, 'pixmap', filename=self.line("vline"), pos="bpLeft")
		ET.SubElement( bslistboxentry, 'pixmap', filename=self.line("vline"), pos="bpRight")

		indent(root)
		et = ET.ElementTree(root)
		fo = open(XML_FILE, "w")
		et.write(fo, encoding='utf-8', xml_declaration=None, default_namespace=None, method="xml")
		self.wrong_xml = False

	def showFileOptions(self):
		menu = []
		menu.append((_("Create new file with default values") ,0))
		menu.append((_("Save current parameters"),1))
		menu.append((_("Delete file with parameters and close plugin"),2))
		self.session.openWithCallback(self.fileOptionsCallback, ChoiceBox, title=_("Operations with configuration file"), list=menu, selection = self.selection)

	def fileOptionsCallback(self, choice):
		if choice is None:
			return
		selected = int(choice[1])
		if selected == 0:
			self.createDefaultCfgFile()
		elif selected == 1:
			self.saveParametersToFile()
		elif selected == 2:
			self.deleteParseFile(XML_FILE)
			self.close()
		else:
			return
		self.selection = selected

# not used, may be for future:
	def colorDict(self):
		# 2 lines to init
		self.newColors = {}
		self.newColorsKeys = self.newColors.keys()

		toptemplatecolor, basictemplatecolor, selectorcolor, transponderinfo, selectedFG, yellow, red, secondFG, fallback, notavailable = self.getColorsFromCfg()
		self.newColors = {
			'toptemplatecolor': toptemplatecolor,
			'basictemplatecolor': basictemplatecolor,
			'selectorcolor': selectorcolor,
			'transponderinfo': transponderinfo,
			'selectedFG': selectedFG,
			'yellow': yellow,
			'red': red,
			'secondFG': secondFG,
			'fallback': fallback,
			'notavailable': notavailable
		}
		self.newColorsKeys = self.newColors.keys()

	def changeColorsOnline(self):
		self.setSkinPath()
		self.saveParametersToFile()
		import skin
		import enigma
		self.colorDict()
		for n in skin.colorNames:
			if n in self.newColors.keys():
				skin.colorNames[n] = enigma.gRGB(int(self.newColors[n], 0x10))
###

modifyskin = ModifyPLiFullHD(Screen)
