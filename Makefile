up: check-pre-requisites
    docker-compose build
    docker-compose -f docker-compose-prod.yml up -d

down: check-pre-requisites
    docker-compose -f docker-compose-prod.yml down
    rm -rf volumes # remove this line for data persistence between restarts

check-pre-requisites:
    @command -v docker || (echo "Docker not installed!" && exit 1)
    @command -v docker-compose || (echo "Docker compose not installed!" && exit 1)

install-deps:
    # Install linux images
    sudo apt-get remove docker docker-engine docker.io
    sudo apt-get update
    sudo apt-get install \
                apt-transport-https \
                ca-certificates \
                curl \
                software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

    sudo add-apt-repository \
        "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) \
        stable"
    
    # Install docker-compose
    sudo apt-get pip
    sudo pip install docker-compose
