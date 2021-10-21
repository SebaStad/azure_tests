#!/bin/bash
echo "Downloading palm"
wget https://gitlab.palm-model.org/releases/palm_model_system/-/archive/master/palm_model_system-master.tar.gz && tar -xf palm_model_system-master.tar.gz && cd palm_model_system-master/

echo "Compiling palm"
mkdir $HOME/palm && bash install -p $HOME/palm
export PATH=/home/batch-explorer-user/palm/bin:${PATH}
cd $HOME/palm && mkdir -p $HOME/palm/JOBS/example_cbl/INPUT && cp /home/batch-explorer-user/palm_model_system-master/packages/palm/model/tests/cases/example_cbl/INPUT/example_cbl_p3d /home/batch-explorer-user/palm/JOBS/example_cbl/INPUT/

cd ..
echo "Creating zip file"
zip -r palm.zip palm
