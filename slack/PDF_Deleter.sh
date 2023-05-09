#!/bin/sh

#Default day is 10 days
start=$(date +%y-%m-%d-%H%M%m)
File=/static/delete_$start.txt
FilePath=/static

echo $File

if [ ! -n "$1" ];
then
    day=10
else
     day=$1
fi

#-mtime 10 表示文件修改时间距离当前为0天的文件，即距离当前时间不到1天（24小时）以内的文件
# Indicates a document that has been modified less than 1 day (24 hours) from the current time,
# i.e. a document that has been modified less than 0 days from the current time
echo "print the pdf file"
echo "find $FilePath -mtime +$day -name "*.pdf*" > $File"
find $FilePath -mtime +$day -name *.pdf* > $File

echo "delete the pdf file"
echo "find $FilePath -mtime +$day -name "*.pdf*"  -exec rm -rf {} \;"
find $FilePath -mtime +$day -name *.pdf*  -exec rm -rf {} \;