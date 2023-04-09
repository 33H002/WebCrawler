#!/bin/sh

SENTRY_RELEASE=$(git rev-parse HEAD)
export SENTRY_RELEASE

python main.py --q "웹크롤링" --save_path "."
python youtube_main.py --q "웹크롤링" --save_path "."