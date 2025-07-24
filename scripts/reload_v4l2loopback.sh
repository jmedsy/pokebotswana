#!/bin/bash
# This script is required to be run before starting the virtual camera in OBS.
# It safely reloads the v4l2loopback kernel module, ensuring a fresh virtual camera device is available for OBS with a device ID specified in .env

set -e

# Unload if loaded
if lsmod | grep -q v4l2loopback; then
  echo "Unloading existing v4l2loopback module..."
  sudo modprobe -r v4l2loopback
fi

# Load with correct params
echo "Loading v4l2loopback module..."
set -a
source ../.env
set +a
sudo modprobe v4l2loopback devices=1 video_nr=$VC_DEVICE_IDX card_label='OBS Virtual Camera' exclusive_caps=1

echo "v4l2loopback reloaded successfully."
