
LOG="${HOME}/shift.log"

timediff() {
    d1=$(date -d "$1" +%s)
    d2=$(date -d "$2" +%s)
    DIFFSEC=$((d1 - d2))
    DIFFHR=$((DIFFSEC / 3600))
    DIFFTIME="${DIFFHR}:$(((DIFFSEC - (3600 * DIFFHR)) / 60))"
    echo $DIFFTIME

    # d1=$(date -d "$1" +%s)
    # d2=$(date -d "$2" +%s)
    # DIFFSEC=$((d1 - d2))
    # DIFFHR=$((DIFFSEC / 60))
    # DIFFTIME="${DIFFHR}:$(((DIFFSEC - (60 * DIFFHR)) / 60))"
    # echo $DIFFTIME
}

time_since_login(){
    DATE=$(date)
    LOGGEDIN=$(grep 'Logging in' $LOG | tail -1 | cut -d' ' -f3-)
    STARTSEC=$(date -d "${LOGGEDIN}" +%s)
    result=$(timediff "${DATE}" "${LOGGEDIN}")
    echo $result
}

basic_report(){
    SHIFTHOURS=$(time_since_login)
    CHECK=$(echo $SHIFTHOURS | head -c 2 | tail -c 1)
    if [ $CHECK == ':' ]
    then
        HR=$(echo "${SHIFTHOURS}" | cut -c1-1)
    else
        HR=$(echo "${SHIFTHOURS}" | cut -c1-2)
    fi
    echo "Tasks completed in the last ${HR} hrs"
    task end.after:today-${HR}h completed
}

if [ $# -eq 0 ]; then
    echo '  Shift arguments'
    echo '      -on............Starts starts shift processies'
    echo '      -clock-in......Starts starts shift processies'
    echo '      -off...........Starts end shift processies '
    echo '      -clock-out.....Starts end shift processies '
    echo '      -status........Returns the status of the shift'
    echo '      -report........Sends the current of shift report without clocking out'
    echo '      -report-full...Sends the current day, week, month report'
else
    # ARGS="$*"
    # echo $ARGS
    for ARG in $*
    do
        # echo $ARG
        if [ $ARG == '-on' ] || [ $ARG == '-clock-in' ] || [ $ARG == '-in' ]
        then
            DATE=$(date)
            echo "Logging in ${DATE}" >> $LOG
            mate-terminal -e 'ssh -X snarf2'
            firefox &
            echo "\nActive Containers\n"
            docker ps -a | grep -v "Exited ("
            google-chrome "https://task-manager-ui.apps.prod.pcf1.us-gov-west-1.dg-govcloud-prod-01.satcloud.us/ui#/task-manager" &
            # mate-terminal -e 'watch"docker ps -a"'
        fi

        if [ $ARG == '-off' ] || [ $ARG == '-clock-out' ] || [ $ARG == '-out' ]
        then
            DATE=$(date)
            echo "Logging out ${DATE}" >> $LOG
            LOGGEDIN=$(grep 'Logging in' $LOG | tail -1 | cut -d' ' -f3-)
            STARTSEC=$(date -d "${LOGGEDIN}" +%s)
            result=$(timediff "${DATE}" "${LOGGEDIN}")
            echo "Shift durration(h:m) ${result}"
            basic_report
        fi

        if [ $ARG == '-status' ]
        then
            LASTLOGGING=$(grep Logging $LOG | tail -1)
            echo "Last logging line: ${LASTLOGGING}"
            result=$(time_since_login)
            echo "Time since shift started(h:m) ${result}"
        fi

        if [ $ARG == '-report' ]
        then
            LASTLOGGING=$(grep Logging $LOG | tail -1)
            echo "Last logging line: ${LASTLOGGING}"
            result=$(time_since_login)
            echo "Time since shift started(h:m) ${result}"
            basic_report
        fi

        if [ $ARG == '-report-full' ]
        then
            echo 'run reports all of em'
            echo 'Month burndown'
            task burndown.daily
            task ghistory.monthly
            task history.monthly
            echo 'Completed past 14 days'
            task end.after:today-14d all
        fi
    done
fi
