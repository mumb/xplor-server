## Installation
* Clone the repo.

## Installation
### Docker based environment setup:
* For ubuntu 16.04+, `make install-deps`
* Copy `.env.sample` file to `.env` file and change values accordingly
* Run `make up` to start the server

* Run `make down` to bring down the server. This will not persist data right now. 

* See comment in `Makefile` to persist data.

* Container is hot reloaded in case of any change in code


* For MacOs, install docker engine from their site and rest of command is same.