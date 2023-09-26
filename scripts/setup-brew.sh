#!/bin/bash
set -x #echo on

# Check if Homebrew is installed
if [ ! -f "`which brew`" ]; then
  echo 'Installing homebrew'
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  brew tap homebrew/bundle  # Install Homebrew Bundle
else
  echo 'Updating homebrew'
  brew update
fi
