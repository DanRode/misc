if [ -n "$BASH_VERSION" ]; then
   complete -C /usr/bin/aws_completer aws
elif [ -n "$ZSH_VERSION" ]; then
   source /usr/share/zsh/site-functions/aws_zsh_completer.sh
fi
