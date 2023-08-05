#!/bin/bash

docker build -t viazoom .
docker run --rm -v $(pwd):/io viazoom maturin build --release --manylinux 
