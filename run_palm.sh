export cwd=$(pwd)




export BASEDIR=/palmbase
cd $BASEDIR/palm
module load mpi/hpcx


mkdir -p $BASEDIR/palm/JOBS/gui_run/INPUT

find $cwd -name "*dynamic" -exec cp {} $BASEDIR/palm/JOBS/gui_run/INPUT/gui_run_dynamic \;
find $cwd -name "*static" -exec cp {} $BASEDIR/palm/JOBS/gui_run/INPUT/gui_run_static \;
find $cwd -name "*p3d" -exec cp {} $BASEDIR/palm/JOBS/gui_run/INPUT/gui_run_p3d \;




# here
# copy input files to certain folder
# with regex

./bin/palmrun -a "d3#" -X 20 -r gui_run_p3d