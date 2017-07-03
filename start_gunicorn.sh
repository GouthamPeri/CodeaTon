APPNAME=contest
APPDIR=/home/ubuntu/codeaton/$APPNAME/

LOGFILE=$APPDIR'gunicorn.log'
ERRORFILE=$APPDIR'gunicorn-error.log'

NUM_WORKERS=3

ADDRESS=localhost:8000

echo "hi"

cd $APPDIR

exec gunicorn $APPNAME.wsgi:application \
-w $NUM_WORKERS --bind=$ADDRESS \
--log-level=debug\
--log-file=$LOGFILE 2>>$LOGFILE 1>>$ERRORFILE &
