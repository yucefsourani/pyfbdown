DESTDIR?=/
PREFIX?=$(DESTDIR)/usr
datadir?=$(PREFIX)/share
INSTALL=install
PYTHON=/usr/bin/python3

all:  icons pos

icons:
	for i in 8  16 22 24 32 36 48 64 72  96 128 256 512; do\
        mkdir -p icons/hicolor/$${i}x$${i}/apps;\
	convert pixmaps/com.github.yucefsourani.pyfbdown.png -resize $${i}x$${i} icons/hicolor/$${i}x$${i}/apps/com.github.yucefsourani.pyfbdown.png;done
pos:
	make -C po all
pot:
	make -C po pyfbdown.pot

installall: all
	$(PYTHON) setup.py install --prefix=$(PREFIX)

install: 
	$(PYTHON) setup.py install --prefix=$(PREFIX)

clean:
	rm -fr  icons

