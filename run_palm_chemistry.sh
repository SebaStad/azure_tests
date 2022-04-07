if [ -f /etc/profile.d/modules.sh ]; then
        . /etc/profile.d/modules.sh
fi

export cwd=$(pwd)
export BASEDIR=/palmbase
export DIR=$BASEDIR/LIBRARIES
export LD_LIBRARY_PATH=$DIR/lib:$LD_LIBRARY_PATH

unzip test.zip

mkdir -p $BASEDIR/palm/JOBS/gui_chemistry_run/INPUT

find $cwd -name "*dynamic" -exec cp {} $BASEDIR/palm/JOBS/gui_chemistry_run/INPUT/gui_chemistry_run_dynamic \;
find $cwd -name "*static" -exec cp {} $BASEDIR/palm/JOBS/gui_chemistry_run/INPUT/gui_chemistry_run_static \;
find $cwd -name "*p3d" -exec cp {} $BASEDIR/palm/JOBS/gui_chemistry_run/INPUT/gui_chemistry_run_p3d \;

cd $BASEDIR/palm
module load mpi/hpcx


# here
# copy input files to certain folder
# with regex

./bin/palmrun -a "d3#" -X 20 -r gui_chemistry_run