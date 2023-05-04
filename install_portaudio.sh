#!/bin/bash

# Install build tools and PortAudio
apt-get update
apt-get install -y build-essential portaudio19-dev

# Install PyAudio
pip install pyaudio
