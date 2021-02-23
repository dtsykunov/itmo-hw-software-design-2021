# itmo-hw-software-design-2021
Homeworks for Software Design course

# Running with Docker (takes a while to install dependencies)

```sh
$ docker run -it $(docker build .)

/cli $
```

# Running locally
1. Install python 3.9.1

2. Install dependencies

```sh
$ pip install -r ./requirements.txt
```

3. _(OPT)_ Check with linter

Requires GNU Make

```sh
$ make check
```

4. _(OPT)_ Run tests

```sh
$ make test
```

5. Install *cli* package

```sh
$ make install
```

6. Run *cli* shell

```sh
$ make run
```
