#!/bin/bash
set -e

# Update system
sudo dnf update -y

# Install Python, pip, git
sudo dnf install -y python3 python3-pip git

# Clone your repo
cd /home/ec2-user
git clone https://github.com/ConnerDeFeo/PrettyGoodAI.git
cd PrettyGoodAI/server

# Install Python dependencies
pip3 install -r requirements.txt

# Fix ownership since user_data runs as root
chown -R ec2-user:ec2-user /home/ec2-user/PrettyGoodAI/server