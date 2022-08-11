# Examples to setup Spawn in GMT

## Installing Spawn in a container

`https://github.com/NREL/MegaBOP/blob/main/main/Dockerfile#L16-L22`

## Compiling a model

```spawn modelica --create-fmu mixed_loads.Districts.DistrictEnergySystem --jmodelica --modelica-path /home/kbenne/Desktop/modelica/mixed_loads /home/kbenne/Development/modelica-buildings/Buildings/```

- Note that both the MBL and the model folder are passed (with a space) to the `--modelica-path` parameter.
- Note that the MBL path includes `Buildings/` at the end, in addition to the path used in MODELICAPATH elsewhere in the GMT.

https://github.com/urbanopt/docker-spawn-modelica#running-the-examples
