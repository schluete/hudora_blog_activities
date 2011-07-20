# setting the PATH seems only to work in GNUmake not in BSDmake
PATH := ./pythonenv/bin:$(PATH)

default: dependencies

run:
	./pythonenv/bin/python ./blog_activities.py

dependencies:
	virtualenv pythonenv
	pip install -E pythonenv -r requirements.txt

.PHONY: dependencies run
