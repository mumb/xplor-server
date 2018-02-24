up: check-pre-requisites
	docker-compose build
	docker-compose up -d

down: check-pre-requisites
	docker-compose down
	rm -rf volumes # remove this line for data persistence between restarts

check-pre-requisites:
	@command -v docker || (echo "Docker not installed!" && exit 1)
	@command -v docker-compose || (echo "Docker compose not installed!" && exit 1)