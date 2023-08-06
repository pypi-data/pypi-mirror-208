build:
	python3 -m pip install --upgrade build
	python3 -m build

install:
	python3 -m pip install .

upload-test:
	python3 -m pip install --upgrade twine
	python3 -m twine upload --repository testpypi dist/*

upload:
	python3 -m pip install --upgrade twine
	python3 -m twine upload dist/*

clean:
	rm -rf build dist iqrfpy.egg-info .pytest_cache
	find . -type d -name  "__pycache__" -exec rm -r {} +

codestyle:
	pycodestyle iqrfpy
	pydocstyle iqrfpy

lint:
	pylint iqrfpy

pytest:
	python3 -m pytest -v tests

test: pytest codestyle lint

cov-html:
	python3 -m pytest --cov=iqrfpy --cov-report=term-missing --cov-report=html

cov-xml:
	python3 -m pytest --cov=iqrfpy --cov-report=term-missing --cov-report=xml

