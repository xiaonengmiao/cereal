#! /bin/bash

node_address="http://localhost"
rest_api_port="9922"
deploy_height_test_number=3
deploy_height_test_wait_time=2
port="9921 9922 9923"
server_name="ubuntu"
server_project_dir="/home/$server_name/ssd/v-systems-main"
server_log_file=$server_project_dir/"node.log"
last_height=10000
status_count=0

function show_help() {
  echo "-v Show detailed logs"
  echo "-q Supress all warnings, also unset -v"
  echo "-d <DPI> Set the DPI value in .Xresources (default to be 100)."
  echo "         A rule of thumb is to set this value such that 11pt font looks nice."
  echo "-f <file> Set log file"
  echo "-c <path> Set conforg path"
  echo "-g <file> Set global gitignore file"
  echo "-a <file> Set which alarm sound to use under contrib/sounds"
  echo "-p Plain install (do not set up credentials with pass)"
  echo "-m Minimal install (for servers, without additional bells and whistles)"
}

while getopts "h?vd:a:f:qc:g:pm" opt; do
  case "$opt" in
    h|\?)
      show_help
      exit 0
      ;;
    v)
      VERBOSE=1;;
    a)
      ALARM_SOUND=$OPTARG;;
    d)
      DPI=$OPTARG;;
    f)
      LOGFILE=$OPTARG;;
    q)
      QUIET=0;;
    c)
      DEFAULT_CONFORG_DIR=$OPTARG;;
    g)
      GITIGNORE_OUT=$OPTARG;;
    p)
      PASSWORD_STORE=false;;
    m)
      MINIMAL_INSTALL=true;;
    : )
      echo "Option -"$OPTARG" requires an argument." >&2
      exit 1;;
  esac
done

function box_out() {
  if [[ $VERBOSE == 0 ]]; then
    return
  fi
  local s="$*"
  tput setaf 3
  echo " -${s//?/-}-
| ${s//?/ } |
| $(tput setaf 4)$s$(tput setaf 3) |
| ${s//?/ } |
 -${s//?/-}-"
  tput sgr 0
}

function box_warn()
{
  if [[ $QUIET == 0 ]]; then
    return
  fi
  local s=("$@") b w
  for l in "${s[@]}"; do
    ((w<${#l})) && { b="$l"; w="${#l}"; }
  done
  tput setaf 5
  echo "  **${b//?/*}**"
  for l in "${s[@]}"; do
    printf '  * %s%*s%s *\n' "$(tput setaf 6)" "-$w" "$l" "$(tput setaf 5)"
  done
  echo "  **${b//?/*}**"
  tput sgr 0
}

function cecho()
{
    bold=$(tput bold);
    green=$(tput setaf 2);
    reset=$(tput sgr0);
    # shellcheck disable=SC2145
    # shellcheck disable=SC2027
    echo "$bold""$green""$@""$reset";
}

box_out "Detecting your OS.."

PLATFORM='unknown'
# shellcheck disable=SC2006
UNAMESTR=`uname`
if [[ "$UNAMESTR" == 'Linux' ]]; then
   PLATFORM='linux'
elif [[ "$UNAMESTR" == 'Darwin' ]]; then
   PLATFORM='mac'
elif [[ "$UNAMESTR" == 'FreeBSD' ]]; then
   PLATFORM='freebsd'
fi

if [[ $VERBOSE != 0 ]]; then
  echo "+ Running on $PLATFORM"
fi

for i in $port; do
  echo " > Checking progress on port $i"
  if [[ "$PLATFORM" == 'mac' ]]; then
    pid_str=$(lsof -n -i4TCP:"$i" | grep LISTEN | awk '{print $2}')
  else
    pid_str=$(netstat -ltnp | grep -w ":$i"| awk '{print $7}')
  fi
  if [[ -z ${pid_str} ]]; then
    echo " > > The port $i does not in any process"
  else
    echo " > > pid string is $pid_str"
  fi
done

function fetch_local_file {
  local file=$1
  local name=$2

  if [[ -f $file ]]; then
    echo "Fetch the local file $file"
  else
    cecho "Error: The local $name file does not exist! Exit!"
    exit
  fi
}

function kill_old_process_by_port {
  for i in $port; do
    echo " > Checking progress on port $i"
    if [[ "$PLATFORM" == 'mac' ]]; then
      pid_str=$(lsof -n -i4TCP:"$i" | grep LISTEN | awk '{print $2}')
    else
      pid_str=$(netstat -ltnp | grep -w ":$i"| awk '{print $7}')
    fi
    if [[ -z ${pid_str} ]]; then
      echo " > > The port $i not in any process"
    else
      echo " > > pid string is $pid_str"
    fi
    # shellcheck disable=SC2236
    if [[ ! -z ${pid_str} ]]; then
      IFS='/' read -r -a temp_array <<< ${pid_str}
      # shellcheck disable=SC2128
      pid=$temp_array
      echo " > > To kill pid: $pid"
      # shellcheck disable=SC2157
      if [ ! -z \$pid ]; then
        sudo kill -9 \$pid
        while sudo kill -0 \$pid; do
          sleep 1
        done
      fi
    fi
  done
  echo " > All port checked! Kill done!"
}

function json_extract {
  local key=$1
  local json=$2

  local string_regex='"([^"\]|\\.)*"'
  local number_regex='-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?'
  local value_regex="${string_regex}|${number_regex}|true|false|null"
  local pair_regex="\"${key}\"[[:space:]]*:[[:space:]]*(${value_regex})"

  if [[ ${json} =~ ${pair_regex} ]]; then
    # shellcheck disable=SC2001
    # shellcheck disable=SC2155
    local result=$(sed 's/^"\|"$//g' <<< "${BASH_REMATCH[1]}")
    echo "$result"
  else
    return 0
  fi
}

function height_comparison {
  local height_max=$1
  local height_current=$2
  local change_time=$3

  # shellcheck disable=SC2004
  if [[ $(( $height_max - $height_current )) -ge 0 ]]; then
    echo "${height_max}" "$change_time"
  else
    echo "${height_current}" $(( $change_time + 1 ))
  fi
}

function timestamp {
  date +"%Y:%m:%d-%H:%M:%S"
}

function clean_replace_folder {
  local folder1=$1
  local folder2=$2

  if [[ $(ls -A "$folder2") ]]; then
    echo "Detect files in folder $folder2"
    echo " > Clear all files and subfolders..."
    # shellcheck disable=SC2115
    rm -r "$folder2"/*
  fi
  cp -R "$folder1/" "$folder2/"
}

cecho "======================= prepare to start ======================="

# Read
while true; do
  box_out "$server_project_dir"
  # shellcheck disable=SC2162
  read -p "Is this your server project dir which contents jar and conf file? " yn
  case $yn in
    [Yy]* ) dir_status="yes"; break;;
    [Nn]* ) dir_status="no"; break;;
    * ) echo "Please answer [y]es or [n]o.";;
  esac
done

if [[ ${dir_status} == "no" ]]; then
  # shellcheck disable=SC2162
  read -p "Please input server project dir: " server_project_dir
fi

box_out "your server project dir which contents jar and conf file is $server_project_dir"

fetch_local_file $server_project_dir/*.jar "jar"
fetch_local_file $server_project_dir/*.conf "conf"

for (( i = 1; i < 4; i++ )); do
  if [[ ! -d "folder$i" ]]; then
    echo "making folder$i"
    mkdir -p "$server_project_dir/folder$i"
  fi
done

while true; do
  echo "To test the HEIGHT of blockchain in $node_address"
  rest_api_address="$node_address:$rest_api_port"
  echo " > Rest API is through" "$rest_api_address"

  height_max=0
  change_time=0
  height=0
  # shellcheck disable=SC2004
  for (( i=1; i<=$deploy_height_test_number; i++))
  do

    result=$(curl -X GET --header 'Accept: application/json' -s "$rest_api_address/blocks/height")
    height=$(json_extract "height" "$result")

    if [[ -n "$height" ]]; then
      echo " > The height for the blockchain in the $i-th check is: $height"
      # shellcheck disable=SC2162
      read height_max change_time < <(height_comparison "$height_max" "$height" "$change_time")
    else
      echo " > The height for the blockchain in the \"$i\"-th check is: empty"
    fi

    sleep ${deploy_height_test_wait_time}

  done

  if [[ ${change_time} -gt 1 ]]; then
    node_status="Normal"
    status_count=0
  else
    node_status="Abnormal"
  fi

  if [[ "$node_status" == "Normal" ]]; then
    echo " > Max height of the blockchain is: $height_max"
    timestamp
    echo "The status of the blockchain is: $node_status ($(( change_time - 1 )) times with height change out of $deploy_height_test_number checks)"
    echo "========================================================================================="
    if [[ $height_max -gt $last_height ]]; then
      # shellcheck disable=SC2004
      last_height=$(( $last_height+10000 ))
      kill_old_process_by_port
      clean_replace_folder "${server_project_dir}/folder1" "${server_project_dir}/folder2"
      # shellcheck disable=SC2125
      target_file=${server_project_dir}/*.jar
      # shellcheck disable=SC2125
      config_file=${server_project_dir}/*.conf
      server_log_file=${server_project_dir}/node.log
      nohup java -jar ${target_file} ${config_file} > ${server_log_file} &
      echo " > Deploy command has been run!"
      echo "========================================================================================="
      echo "To test the HEIGHT of blockchain in $node_address"
      echo " > Rest API is through" "$rest_api_address"

      height_max=0
      change_time=0
      height=0
      # shellcheck disable=SC2004
      for (( i=1; i<=$deploy_height_test_number; i++))
      do

        result=$(curl -X GET --header 'Accept: application/json' -s "$rest_api_address/blocks/height")
        height=$(json_extract "height" "$result")

        if [[ -n "$height" ]]; then
          echo " > The height for the blockchain in the $i-th check is: $height"
          # shellcheck disable=SC2162
          read height_max change_time < <(height_comparison "$height_max" "$height" "$change_time")
        else
          echo " > The height for the blockchain in the \"$i\"-th check is: empty"
        fi

        sleep ${deploy_height_test_wait_time}

      done

      if [[ ${change_time} -gt 1 ]]; then
        node_status="Normal"
        clean_replace_folder "${server_project_dir}/folder2" "${server_project_dir}/folder3"
        status_count=0
      else
        node_status="Abnormal"
        kill_old_process_by_port
        clean_replace_folder "${server_project_dir}/folder3" "${server_project_dir}/folder1"
        # shellcheck disable=SC2125
        target_file=${server_project_dir}/*.jar
        # shellcheck disable=SC2125
        config_file=${server_project_dir}/*.conf
        server_log_file=${server_project_dir}/node.log
        nohup java -jar ${target_file} ${config_file} > ${server_log_file} &
        echo " > Deploy command has been run!"
        echo "========================================================================================="
      fi
      timestamp
    fi
  else
    echo " > Max height of the blockchain is: $height_max"
    timestamp
    echo "The status of the blockchain is: $node_status"
    # shellcheck disable=SC2004
    status_count=$(( $status_count+1 ))
    if [[ $status_count -ge 2 ]]; then
      exit
    fi
    kill_old_process_by_port
    clean_replace_folder "${server_project_dir}/folder3" "${server_project_dir}/folder1"
    # shellcheck disable=SC2125
    target_file=${server_project_dir}/*.jar
    # shellcheck disable=SC2125
    config_file=${server_project_dir}/*.conf
    server_log_file=${server_project_dir}/node.log
    nohup java -jar ${target_file} ${config_file} > ${server_log_file} &
    echo " > Deploy command has been run!"
    echo "========================================================================================="
    timestamp
  fi
  echo "Sleep for 5 minutes..."
  count=0
  total=600
  pstr="[=======================================================================]"

  while [[ $count -lt $total ]]; do
    sleep 0.5 # this is work
    # shellcheck disable=SC2004
    count=$(( $count + 1 ))
    # shellcheck disable=SC2004
    pd=$(( $count * 73 / $total ))
    printf "\r%3d.%1d%% %.${pd}s" $(( $count * 100 / $total )) $(( ($count * 1000 / $total) % 10 )) $pstr
  done
  printf "\n"
done
