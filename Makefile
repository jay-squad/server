SHELL := /bin/bash
PASSWORD := password
python-install:
	pip3 install virtualenv
	virtualenv env
	source env/bin/activate && pip3 install -r requirements.txt

postgres-install: # TODO handle OSX install
	sudo apt install postgresql
	sudo -u postgres psql -c "create role admin with login createdb createrole password '$(PASSWORD)'"


install: python-install postgres-install

.PHONY: run
run:
	source env/bin/activate && python3 -m src.foodie.server


.PHONY: test
test:
	pytest
