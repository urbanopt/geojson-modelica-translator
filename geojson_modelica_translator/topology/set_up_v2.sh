#!/bin/bash -e
export MODELICAPATH=$PATH:'/usr/local/JModelica/ThirdParty/MSL:/opt/openstudio/server/modelica-buildings:opt/openstudio/server/modelica-buildings/Buildings:/opt/openstudio/server/geojson-modelica-translator/tests/management/data/sdk_project_scraps:/opt/openstudio/server/geojson-modelica-translator/tests/management/data/sdk_project_scraps/model_from_sdk'
export PATH=$PATH:'/opt/openstudio/server/Spawn-0.1.1-9dade2a577-Linux/bin'

apt-get update
apt-get install python3-pip -y
apt-get install python3.7-dev -y
apt-get install python3-setuptools python3.7-venv -y


python3.7 -m pip install cython
python3.7 -m pip install --upgrade --force-reinstall numpy
python3.7 -m pip install geojson-modelica-translator


pip install pandas
python3 -m pip install pandas


cd /opt/openstudio/server
git clone https://github.com/urbanopt/geojson-modelica-translator.git
cd geojson-modelica-translator
git checkout topology

cd /opt/openstudio/server/geojson-modelica-translator/tests/management/data/sdk_project_scraps
python3.7 -m venv py37-venv
python3.7 -m pip install poetry
poetry install
python3 -m pip install --upgrade Pillow
python3 -m pip install buildingspy
wget -c https://spawn.s3.amazonaws.com/builds/Spawn-0.1.1-9dade2a577-Linux.tar.gz  -O - | tar -xz

cp /opt/openstudio/server/geojson-modelica-translator/geojson_modelica_translator/topology/in.csv /opt/openstudio/server/geojson-modelica-translator/tests/management/data/sdk_project_scraps
cp /opt/openstudio/server/geojson-modelica-translator/geojson_modelica_translator/topology/post_processing.py /opt/openstudio/server/geojson-modelica-translator/tests/management/data/sdk_project_scraps


cd /opt/openstudio/server
git clone https://github.com/lbl-srg/modelica-buildings.git
cd modelica-buildings
git checkout issue2204_gmt_mbl
