@echo off
cd /d F:\TRACKRECORD
python daily_commit.py --push >> commit_log.txt 2>&1