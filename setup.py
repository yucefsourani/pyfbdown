#!/usr/bin/python3
# -*- coding: utf-8 -*-
from distutils.core import setup
from glob import glob


doc_files  = ['LICENSE',  'README.md']
data_files = [
              ('share/applications/', ['com.github.yucefsourani.pyfbdown.desktop']),
              ('share/doc/pyfbdown', doc_files),
              ('share/icons/hicolor/8x8/apps/', ['icons/hicolor/8x8/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/16x16/apps/', ['icons/hicolor/16x16/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/22x22/apps/', ['icons/hicolor/22x22/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/24x24/apps/', ['icons/hicolor/24x24/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/32x32/apps/', ['icons/hicolor/32x32/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/36x36/apps/', ['icons/hicolor/36x36/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/48x48/apps/', ['icons/hicolor/48x48/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/64x64/apps/', ['icons/hicolor/64x64/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/72x72/apps/', ['icons/hicolor/72x72/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/96x96/apps/', ['icons/hicolor/96x96/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/128x128/apps/',['icons/hicolor/128x128/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/256x256/apps/',['icons/hicolor/256x256/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/icons/hicolor/512x512/apps/',['icons/hicolor/512x512/apps/com.github.yucefsourani.pyfbdown.png']),
              ('share/pixmaps/',['pixmaps/com.github.yucefsourani.pyfbdown.png']),
              ('share/pyfbdown-data/images',glob('pyfbdown-data/images/*'))
              ]
locales=map(lambda i: ('share/'+i,[''+i+'/pyfbdown.mo',]),glob('locale/*/LC_MESSAGES'))
data_files.extend(locales)

setup(
      name="pyfbdown",
      description='Facebook Videos Downloader',
      long_description='Facebook Videos Downloader.',
      version="1.0",
      author='Youcef Sourani',
      author_email='youssef.m.sourani@gmail.com',
      url="https://github.com/yucefsourani/pyfbdown",
      license='GPLv3 License',
      platforms='Linux',
      scripts=['pyfbdown.py'],
      keywords=['downloader', 'video', 'audio' , 'facebook'],
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: POSIX :: Linux',
          'Development Status :: 4 - Beta ',
          'Intended Audience :: End Users/Desktop',
            ],
      data_files=data_files
)
