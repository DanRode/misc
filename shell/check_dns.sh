#! /usr/bin/evn bash
ADDRESS = $1

while [ true ]; do
    nscd restart

    nslookup $ADDRESS
    if [ $? == 0 ]; then
        exit 0
    fi

    counter = $((counter + 1))
    if [ $counter >= 10 ]
        exit 1
    else
        sleep 30
    fi
done
