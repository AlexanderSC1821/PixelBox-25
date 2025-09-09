#!/bin/bash
# Script to write an image file to an SD card
# Usage: ./SDCardWriter.sh <image file> <sd card device>
sudo dd if=$1 of=$2 bs=4M status=progress conv=fsync
