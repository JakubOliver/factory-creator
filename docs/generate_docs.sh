#!/bin/sh

make clean

#sphinx-apidoc -o source .
sphinx-apidoc -o source ../src/factory_creator

make html