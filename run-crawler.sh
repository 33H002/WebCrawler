#!/bin/bash

python3 main.py --q "현대카드" --save_path "." >> log.log
python3 youtube_main.py --q "현대카드" --save_path "." >> youtube_log.log