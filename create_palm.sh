#!/bin/bash
echo "Downloading palm"
wget https://gitlab.palm-model.org/releases/palm_model_system/-/archive/master/palm_model_system-master.tar.gz && tar -xf palm_model_system-master.tar.gz && cd palm_model_system-master/

echo "Compiling palm"
mkdir $HOME/palm && bash install -p $HOME/palm
export PATH=$HOME/palm/bin:${PATH}

echo "Copying basefile"
cd $HOME/palm && mkdir -p $HOME/palm/JOBS/example_cbl/INPUT 
cp $HOME/palm_model_system-master/packages/palm/model/tests/cases/example_cbl/INPUT/example_cbl_p3d $HOME/palm/JOBS/example_cbl/INPUT/

cd ..
echo "Creating zip file"
zip -r palm.zip palm palm_model_system-master
echo "Everything done"
