#! /bin/bash

node_address="http://localhost"
rest_api_port="9922"
deploy_height_test_number=3
deploy_height_test_wait_time=15
port="9921 9922 9923"
server_name="ubuntu"
server_project_dir="/home/$server_name/ssd/v-systems-main"
server_log_file="node.log"
PLATFORM='unknown'
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
    if [[ ! -z ${pid_str} ]]; then
      IFS='/' read -r -a temp_array <<< ${pid_str}
      pid=$temp_array
      echo " > > To kill pid: $pid"
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
    local result=$(sed 's/^"\|"$//g' <<< "${BASH_REMATCH[1]}")
    echo $result
  else
    return 0
  fi
}

function height_comparison {
  local height_max=$1
  local height_current=$2
  local change_time=$3

  if [[ $(( $height_max - $height_current )) -ge 0 ]]; then
    echo ${height_max} $change_time
  else
    echo ${height_current} $(( $change_time + 1 ))
  fi
}

# Read
while true; do
  echo "$server_project_dir"
  read -p "Is this your server project dir which contents jar and conf file? " yn
  case $yn in
    [Yy]* ) dir_status="yes"; break;;
    [Nn]* ) dir_status="no"; break;;
    * ) echo "Please answer [y]es or [n]o.";;
  esac
done

if [[ ${dir_status} == "no" ]]; then
  read -p "Please input server project dir: " server_project_dir
fi

while true; do
  echo "To test the HEIGHT of blockchain in $node_address"
  rest_api_address="$node_address:$rest_api_port"
  echo " > Rest API is through" $rest_api_address

  height_max=0
  change_time=0
  height=0
  for (( i=1; i<=$deploy_height_test_number; i++))
  do

    result=$(curl -X GET --header 'Accept: application/json' -s "$rest_api_address/blocks/height")
    height=$(json_extract "height" "$result")

    if [[ -n "$height" ]]; then
      echo " > The height for the blockchain in the $i-th check is: $height"
      read height_max change_time < <(height_comparison "$height_max" "$height" "$change_time")
    else
      echo " > The height for the blockchain in the \"$i\"-th check is: empty"
    fi

    sleep ${deploy_height_test_wait_time}

  done

  if [[ ${change_time} -gt 1 ]]; then
    node_status="Normal"
  else
    node_status="Abnormal"
  fi

  if [[ "$node_status" == "Normal" ]]; then
    echo " > Max height of the blockchain is: $height_max"
    echo "The status of the blockchain is: $node_status ($(( change_time - 1 )) times with height change out of $deploy_height_test_number checks)"
    echo "========================================================================================="
  else
    echo " > Max height of the blockchain is: $height_max"
    echo "The status of the blockchain is: $node_status"
    kill_old_process_by_port
    target_file=$(echo ${server_project_dir}/*.jar)
    config_file=$(echo ${server_project_dir}/*.conf)
    server_log_file="node.log"
    nohup java -jar ${target_file} ${config_file} > ./${server_log_file} &
    echo " > Deploy command has been run!"
    echo "========================================================================================="
  fi
  echo "Sleep for 5 minutes..."
  count=0
  total=600
  pstr="[=======================================================================]"

  while [[ $count -lt $total ]]; do
    sleep 0.5 # this is work
    count=$(( $count + 1 ))
    pd=$(( $count * 73 / $total ))
    printf "\r%3d.%1d%% %.${pd}s" $(( $count * 100 / $total )) $(( ($count * 1000 / $total) % 10 )) $pstr
  done
  printf "\n"
done
