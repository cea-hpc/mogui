init:
	pip install -r requirements.txt

build:
	python3 -m build

install:
	pip install .

distclean:
	rm -rf dist
	rm -rf build
	rm -rf mogui.egg-info

.PHONY: init build install distclean
