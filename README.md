# itmo-hw-software-design-2021

[Homeworks for Software Design course](http://hwproj.me/courses/62)

# Shell homework

## Running with Docker 

_Takes a while installing dependencies._

```sh
$ docker run -it $(docker build .)

/cli $
```

## Running locally
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

## Architecture

Cli shell consists of two parts:

1. Parser
   Parses and syntactically validates the input string.
2. Executor
   Executes the parsed input for desired side-effects.
3. Interlayer (i.e. "Common")
   Specifies data structures used by both Parser and Executor.
   

### Project structure

```sh
~/sd-cli$ tree .
.
├── Dockerfile 
├── Makefile
├── README.md
├── cli                   # application source code directory
│   ├── __init__.py
│   ├── __main__.py       # entrypoint
│   ├── builtins          # source code directory for builtin commands
│   │   ├── =.py
│   │   ├── __init__.py
│   │   ├── cat.py
│   │   ├── echo.py
│   │   ├── exit.py
│   │   ├── pwd.py
│   │   └── wc.py
│   ├── common.py         # interlayer
│   ├── executor.py 
│   └── parser.py
├── requirements.txt
├── setup.py
└── tests
    ├── test.sh
    ├── test.txt
    ├── test_executor.py
    ├── test_parser.py
    └── test_sanity.py
```

