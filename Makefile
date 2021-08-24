deps:
	pip install -r requirements.txt

test:
	PYTHONPATH=$(shell pwd)/src coverage run -m nose test/
	PYTHONPATH=$(shell pwd)/src coverage report


sdist:
	python3 setup.py sdist
	(cd dist/ && shasum lintforbrains-$(VERSION).tar.gz > lintforbrains-$(VERSION).tar.gz.sha)

bdist:
	python3 setup.py bdist_wheel --universal
	(cd dist/ && shasum lintforbrains-$(VERSION)-py2.py3-none-any.whl > lintforbrains-$(VERSION)-py2.py3-none-any.whl.sha)

clean:
	rm -rf build/ dist/ src/*.egg-info src/*.egg
	find . \( -name '*.pyc' -or -name '*.pyo' \) -print -delete
	find . -name '__pycache__' -print -delete

docker-build:
	docker build . -t kippandrew/lintforbrains

docker-test:
	docker run --rm kippandrew/lintforbains "bash -x -c 'make test'"

.PHONY: dist bdist sdist clean test docker-build docker-test
