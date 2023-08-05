#!/bin/bash
python ./batch_files/setup.py clean --all
python ./batch_files/setup.py bdist_wheel "${1}"
