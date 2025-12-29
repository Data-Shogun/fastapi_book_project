install:
	#Install dependencies
	python -m pip install --upgrade pip &&\
		pip install -r requirements.txt
format:
	#Format code with black
	black *.py routers/*.py tests/*.py
lint:
	#Lint code with pylint
	python -m pylint --disable=R,C *.py routers/*.py
run:
	#Run app
	uvicorn main:app --reload
test:
	#Run tests
	python -m pytest -vv --disable-warnings --cov=routers --cov=main tests/*
build:
	#Build container
	docker build -t fastapi-book-app .
deploy:
	#Deploy the project
all: install lint test run 