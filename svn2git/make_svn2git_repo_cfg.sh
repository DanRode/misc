SVN_REPOS=`cat app_repos.cfg`
REPO_URL="mtdproducts@vs-ssh.visualstudio.com:v3/mtdproducts/Subv01_migration"
for i in $SVN_REPOS; do
  #`echo $i | sed s/.*\/(.*)$/`
  REPO_NAME=`echo $i | sed -e 's/.*\///g'`
  GIT="${REPO_URL}/${REPO_NAME}"
  echo "${i}::${GIT}"
  #REPO_NAME=`echo $status | sed -e s/http//`
 # sed -e 's/\..*//g'
done
