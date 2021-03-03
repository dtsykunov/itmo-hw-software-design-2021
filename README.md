# itmo-hw-software-design-2021

[Homeworks for Software Design course](http://hwproj.me/courses/62)

# Shell homework

## Running with Docker 

_Takes a while installing dependencies._

```sh
$ docker run -it $(docker build -q .)

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


## Supported commands

### cat [file ...]

    Concatenate contents of in each input file, or stdin.

### wc [file ...]

    Print number of words, lines and characters in each input file, or stdin.
    
### echo [arg ...]

   Print arguments with trailing '\n'. 
   
### pwd
    
    Print current working directory.

### a=b
    
    Add variable to environment
    
### exit

    Exit shell
