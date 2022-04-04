ls ../data/playbooks/*.yml -1a |
while read -r LINE; do
  echo "$(tput setaf 4)CHECKING FILE: $LINE $(tput sgr 0)";
  if ansible-playbook --check ./$LINE | tail -n 3 | grep -q "failed=0";
  then
    echo "  $(tput setaf 2)OK$(tput sgr 0)";
  else
    echo "  $(tput setaf 1)FAILED$(tput sgr 0)";
  fi
done;
