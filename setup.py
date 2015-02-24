from distutils.core import setup
import setup_translate

pkg = 'Extensions.ModifyPLiFullHD'
setup (name = 'enigma2-plugin-extensions-modifyplifullhd',
       version = '1.04',
       description = 'modify font and colors in pli-fullhd and pli-hd1 skins',
       packages = [pkg],
       package_dir = {pkg: 'plugin'},
       package_data = {pkg: ['locale/*/LC_MESSAGES/*.mo']},
       cmdclass = setup_translate.cmdclass, # for translation
      )
