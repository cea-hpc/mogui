init:
	pip install -r requirements.txt

build:
	python3 -m build

ChangeLog:
	script/gitlog2changelog.py

install:
	pip install .

style:
	black mogui
	pylint mogui

distclean:
	rm -rf dist
	rm -rf build
	rm -rf modules_gui.egg-info

.PHONY: init build ChangeLog install style distclean
