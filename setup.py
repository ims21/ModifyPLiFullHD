from distutils.core import setup
import setup_translate

pkg = 'Extensions.ModifyPLiFullHD'
setup (name = 'enigma2-plugin-extensions-modifyplifullhd',
	version = '1.47',
	description = 'modify font and colors for PLi-FullHD and PLi-HD1 skins',
	packages = [pkg],
	package_dir = {pkg: 'plugin'},
	package_data = {pkg: ['win2k/*.png','png/*.png', 'locale/*.pot', 'locale/*/LC_MESSAGES/*.mo']},
	cmdclass = setup_translate.cmdclass, # for translation
	)
