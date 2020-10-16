
COMMAND=$1

while :
do 
  clear
  date
  #task priority:H or priority:M list
  #echo $COMMAND
  $COMMAND
  sleep 15
done


