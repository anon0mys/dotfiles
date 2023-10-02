#!/bin/bash
set -x #echo on

# Check if zsh is installed
if [ ! -d "~/.oh-my-zsh" ]; then
  echo 'Installing zsh'
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
  exit
fi
