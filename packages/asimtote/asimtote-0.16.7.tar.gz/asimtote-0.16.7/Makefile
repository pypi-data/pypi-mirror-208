.PHONY: all
all: asimtote

.PHONY: remake
remake: clean all

.PHONY: asimtote
asimtote:
	./setup.py sdist bdist_wheel

.PHONY: upload
upload:
	python3 -m twine upload dist/*

.PHONY: clean
clean:
	rm -rf build dist asimtote.egg-info

.PHONY: test_asimtote
test_asimtote:
	python3 -m test_asimtote
