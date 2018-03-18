## Installation
* Clone the repo.
### Docker based environment setup for ubuntu:
* For ubuntu 16.04+, `make install-deps`
* Copy `.env.sample` file to `.env` file and change values accordingly
* Run `make up` to start the server

* Run `make down` to bring down the server. This will not persist data right now. 

* See comment in `Makefile` to persist data.

* Container is hot reloaded in case of any change in code

### Docker based environment setup for Mac:
* Install docker engine from docker official website and rest of command is same.