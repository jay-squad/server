SHELL := /bin/bash

install:
	pip3 install virtualenv
	virtualenv env
	source env/bin/activate && pip3 install -r requirements.txt

.PHONY: run
run:
	source env/bin/activate && python3 server.py
