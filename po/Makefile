POTFILE=$(shell cat POTFILES.in)
SOURCES=$(addprefix ../, $(POTFILE))
POFILES=$(wildcard *.po)
MOFILES=$(patsubst %.po,%.mo,$(POFILES))
all: $(MOFILES)

pyfbdown.pot: $(SOURCES)
	intltool-update -g pyfbdown -p

%.mo: %.po
	msgfmt $*.po -o $*.mo
	mkdir -p ../locale/$*/LC_MESSAGES/ || :
	cp $*.mo ../locale/$*/LC_MESSAGES/pyfbdown.mo


%.po: pyfbdown.pot
	intltool-update -g pyfbdown -d $*
