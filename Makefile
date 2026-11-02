PYTHON ?= python3

all: database review figures test

database:
	$(PYTHON) scripts/rebuild.py

review: database
	$(PYTHON) scripts/recurate_natural.py
	$(PYTHON) scripts/recompute_conservation.py
	$(PYTHON) scripts/recompute_structure.py
	$(PYTHON) scripts/recheck_overlap.py
	$(PYTHON) scripts/review_natural.py

figures: database
	$(PYTHON) scripts/make_figures.py

test: review figures
	$(PYTHON) -m unittest discover -s tests -v
