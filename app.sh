#!/bin/sh


case $1 in
run)
    flask --app slack run --debug
;;
init-db)
    flask --app slack init-db 
;;
*)
    echo "./app.sh run|init-db"
;;
esac

