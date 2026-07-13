#!/bin/bash
parent_dir=$(dirname $(realpath "$0"))
cd $parent_dir
uv run WordleHelper.py
