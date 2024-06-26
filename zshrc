# If you come from bash you might have to change your $PATH.
export PATH=$HOME/bin:/usr/local/bin:$PATH

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/robbyrussell/oh-my-zsh/wiki/Themes
ZSH_THEME="miloshadzic"

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in ~/.oh-my-zsh/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to automatically update without prompting.
# DISABLE_UPDATE_PROMPT="true"

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS=true

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in ~/.oh-my-zsh/plugins/*
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(git virtualenv) 

source $ZSH/oh-my-zsh.sh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"
unalias gc
alias shell-plus='./manage.py shell_plus'
alias django-s='./manage.py runserver'
alias das='shell-plus'
alias dc='docker compose'
alias k='kubectl'
alias evim='vim ~/dotfiles-local/vimrc.local'
alias ezsh='vim ~/dotfiles-local/zshrc.local'
alias gca='git commit --amend --no-edit'
alias s='rspec'
alias tctl="docker exec temporal-admin-tools tctl"

eval "$(/opt/homebrew/bin/brew shellenv)"

# Export root bin bash scripts
export PATH="$PATH:$HOME/bin"
export PATH="$PATH:/usr/local/bin"
export PATH="$PATH:/Users/evan.wheeler/go/bin"

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV="true"
export PATH="$HOME/.exenv/bin:$PATH"
eval "$(rbenv init -)"
eval "$(pyenv init -)"

export VIRTUAL_ENV_DISABLE_PROMPT=1
export ZSH_THEME_VIRTUALENV_PREFIX='('
export ZSH_THEME_VIRTUALENV_SUFFIX=')'
export WORKON_HOME=$HOME/.virtualenvs
pyenv virtualenvwrapper

export ANDROID_HOME=/Users/$USER/Library/Android/sdk
export ANDROID_SDK_ROOT=/Users/$USER/Library/Android/sdk
export ANDROID_SDK=/Users/$USER/Library/Android/sdk
export PATH=${PATH}:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

export PATH="$PATH:/Applications/IntelliJ IDEA.app/Contents/MacOS"
export PATH="$PATH:/Applications/PyCharm.app/Contents/MacOS"

# Grow stuff

export MY_REPO="/Users/workmac/grow/Grow-Dashboard"
export GROW_HOME=$MY_REPO
export FLASK_ENV="local"

# Peloton stuff

export API_CONFIG_YAML_FOLDER=./configurations

# Not sure what these are for
export TKITCH=048438595429
export PES1=429007243955

# login

export CWE_DEV=787201226158
export CWE_PROD=159653997934
export CWE_STAGE=214936853396
export CWE_INFRA=873230290044
export PELO_DEV=106877218800
export PELO_TEST=152245890419
export PELO_STAGE=486598304777
export PELO_PROD=386675210126
export FORCE_MFA="Duo Push"
export AWS_REGION="us-east-1"

s2al () { saml2aws login --skip-prompt --profile=${1} --duo-mfa-option $FORCE_MFA --role="arn:aws:iam::${2}:role/acquisition-rw"; }
s2a () { eval $(saml2aws script --shell=bash --skip-prompt --profile=${1}); }
awslogin () { saml2aws login --force --region $AWS_REGION --profile=${1} --duo-mfa-option $FORCE_MFA --role="arn:aws:iam::${2}:role/$3"; }
awsconfig () { eval $(saml2aws script --shell=bash --skip-prompt --region $AWS_REGION --profile=${1}); }
awswho () { aws sts get-caller-identity; }

kswap () {
  context=$1
  case $context in
    "cwe-dev")
      context_id=$CWE_DEV
      role="cwe-infra"
      ;;

    "cwe-prod")
      context_id=$CWE_PROD
      role="cwe-infra"
      ;;

    "cwe-stage")
      context_id=$CWE_STAGE
      role="cwe-infra"
      ;;

    "cwe-infra")
      context_id=$CWE_INFRA
      role="cwe-dev"
      ;;

    "pelo-test")
      context_id=$PELO_TEST
      role="acquisition-rw"
      ;;

    "pelo-dev")
      context_id=$PELO_DEV
      role="acquisition-rw"
      ;;

    "pelo-stage")
      context_id=$PELO_STAGE
      role="acquisition-rw"
      ;;

    "pelo-prod")
      context_id=$PELO_PROD
      role="acquisition-rw"
      ;;
  esac

  if [ $context_id ]; then
    awslogin $context $context_id $role && awsconfig $context
  fi

  kubectl config use-context $context
}

alias apc="s2al pc ${PELO_DEV}"
alias atest="s2al test ${PELO_TEST}"
alias astage="s2al stage ${PELO_STAGE}"
alias aprod="s2al prod ${PELO_PROD}"
# these are the aliases to trigger account login (if necessary) and switch
alias jpc="s2al pc ${PELO_DEV} && s2a pc"
alias jtest="s2al test ${PELO_TEST} && s2a test"
alias jstage="s2al stage ${PELO_STAGE} && s2a stage"
alias jprod="s2al prod ${PELO_PROD} && s2a prod"

alias api_up="./pelo-compose-ctl up"

source "/opt/homebrew/opt/kube-ps1/share/kube-ps1.sh"
KUBE_PS1_NS_ENABLE=false
KUBE_PS1_PREFIX=""
KUBE_PS1_SEPARATOR="("
KUBE_PS1_CTX_COLOR="blue"
PROMPT='$(virtualenv_prompt_info) $(kube_ps1) '$PROMPT

# The next line updates PATH for the Google Cloud SDK.
if [ -f '/Users/evan.wheeler/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/evan.wheeler/google-cloud-sdk/path.zsh.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/Users/evan.wheeler/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/evan.wheeler/google-cloud-sdk/completion.zsh.inc'; fi

#THIS MUST BE AT THE END OF THE FILE FOR SDKMAN TO WORK!!!
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"
