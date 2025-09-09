#!/bin/bash
# Script to read an SD card to an image file
# Usage: ./SDCardWriter.sh <image file> <sd card device>
sudo dd if=$2 of=$1 bs=4M status=progress conv=fsync

