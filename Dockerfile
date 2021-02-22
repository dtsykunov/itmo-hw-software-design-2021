from python:3.9.1

copy ./requirements.txt .
run pip install -r ./requirements.txt

workdir /cli
copy . .
run pip install .
run make test && make install
cmd make run
