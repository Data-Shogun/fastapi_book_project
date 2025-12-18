install:
	#Install dependencies
	python -m pip install --upgrade pip &&\
		pip install -r requirements.txt
format:
	#Format code with black
	black *.py routers/*.py
lint:
	#Lint code with pylint
	python -m pylint --disable=R,C *.py routers/*.py
test:
	#Run tests
build:
	#Build container
run:
	#Run container
deploy:
	#Deploy the project
all: install lint test deploy