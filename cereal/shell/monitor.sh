#! /bin/bash

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

port="9921 9922 9923 9928 9929"

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
  if [[ ! -z ${pid_str} ]]; then
    IFS='/' read -r -a temp_array <<< ${pid_str}
    pid=$temp_array
    echo " > > To monitor pid: $pid"
    if [[ ! -z ${pid} ]]; then
      if [[ "$PLATFORM" == 'mac' ]]; then
        top -pid "${pid}"
      else
        top -p "${pid}"
      fi
    fi
  fi
done