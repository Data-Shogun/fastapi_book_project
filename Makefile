install:
	#Install dependencies
	python -m pip install --upgrade pip &&\
		pip install -r requirements.txt
format:
	#Format code with black
	black *.py routers/*.py
lint:
	#Lint code with pylint
	pylint --ignore=R,C *.py router/*.py
test:
	#Run tests
build:
	#Build container
run:
	#Run container
deploy:
	#Deploy the project

