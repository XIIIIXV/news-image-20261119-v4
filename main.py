#!/usr/bin/env python3
"""Entrypoint: render the front page and copy it to the output directory.

Reads stories.json, draws entry.png with gen_image.py, then copies it to
$MAKEFUN_OUTPUT_DIR (default /output/entry.png).
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gen_image import render, load_data


def main():
    data = load_data()
    entry = os.path.join(HERE, "entry.png")
    render(data, entry)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(entry, os.path.join(out_dir, "entry.png"))
    print("wrote", os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
