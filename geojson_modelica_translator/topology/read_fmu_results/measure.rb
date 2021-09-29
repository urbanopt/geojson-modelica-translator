# insert your copyright here

# see the URL below for information on how to write OpenStudio measures
# http://nrel.github.io/OpenStudio-user-documentation/reference/measure_writing_guide/

require 'erb'

# start the measure
class ReadFMUResults < OpenStudio::Measure::ReportingMeasure

  require 'pycall'
  require 'pycall/import'
  include PyCall::Import
  # human readable name
  def name
    # Measure name should be the title case of the class name.
    return 'ReadFMUResults'
  end

  # human readable description
  def description
    return ' This measure runs an optimization analysis in which the variable is the connectivity status of the first building listed in the GeoJSON file, and the objective function is the district-level energy consumption. The measure calls Python scripts to create a district energy model through the GMT, compile and simulate the model as an FMU, and process the results.'
  end

  # human readable description of modeling approach
  def modeler_description
    return ' This measure runs an optimization analysis in which the variable is the connectivity status of the first building listed in the GeoJSON file, and the objective function is the district-level energy consumption. The measure calls Python scripts to create a district energy model through the GMT, compile and simulate the model as an FMU, and process the results.'
  end

  # define the arguments that the user will input
  def arguments
    args = OpenStudio::Measure::OSArgumentVector.new

	bldg1_con = OpenStudio::Measure::OSArgument.makeDoubleArgument('bldg1_con', true)
    bldg1_con.setDisplayName('Bldg1 Con Status')
    bldg1_con.setDescription('Connectivity status of 1st bldg ')
    args << bldg1_con

    return args
  end

  # define the outputs that the measure will create
  def outputs

    # this measure does not produce machine readable outputs with registerValue, return an empty list

    return outs
  end

  # return a vector of IdfObject's to request EnergyPlus objects needed by the run method
  # Warning: Do not change the name of this method to be snake_case. The method must be lowerCamelCase.
  def energyPlusOutputRequests(runner, user_arguments)
    super(runner, user_arguments)

    result = OpenStudio::IdfObjectVector.new

    # use the built-in error checking
    if !runner.validateUserArguments(arguments, user_arguments)
      return result
    end

    return result
  end

  # define what happens when the measure is run
  def run(runner, user_arguments)
    super(runner, user_arguments)

	bldg1_con=runner.getDoubleArgumentValue('bldg1_con', user_arguments)

    #Load packages.
    numpy=PyCall.import_module("numpy")
	pkg_resources=PyCall.import_module("pkg_resources")


    #Print output.
	runner.registerInfo("bldg 1 conn is #{bldg1_con}")

	#Set path.
	pyimport 'sys', as: :sys
	path="#{File.dirname(__FILE__)}/resources/"
	sys.path.append(path)
	sys.path.append("/opt/openstudio/server/PyFMI/OCT_install/tmpinstalldir/install/Python") ##AA added path within container
	sys.path.append("/opt/openstudio/server/geojson-modelica-translator/geojson_modelica_translator/topology")
	path=sys.path
	runner.registerInfo("path is #{path}")

	#Print Python version.
    version=sys.version
    runner.registerInfo("version is #{version}")


	#Load create fmu module.
	res=PyCall.import_module("create_fmu")
	res.configure(bldg1_con)
	PyCall.init('python2')
	ENV['PYTHON'] = '/usr/bin/python2' # change to python2
	ENV['JMODELICA_HOME'] = '/usr/local/JModelica'
	PyCall.init('python2')
	sys.path.append("/opt/openstudio/server/geojson-modelica-translator/geojson_modelica_translator/topology") #modify path again for py2

	#Print path for debugging.
	runner.registerInfo("path is #{path}")

	#Load compile and simulate module.
	res=PyCall.import_module("compile_and_simulate")
	res.compile_and_simulate(bldg1_con)

	#Switch to Python 3 and call post processing module.
	PyCall.init('python3')
	ENV['PYTHON'] = '/usr/bin/python3'
	PyCall.init('python3')
	result = `python3 post_processing.py #{bldg1_con}`  # Hack needed due to hiccup in loading buildingspy.
    energy_cons = Float(result.split("\n")[2])
    runner.registerValue("energy_cons", energy_cons, '')
    return true
  end
end

# register the measure to be used by the application
ReadFMUResults.new.registerWithApplication
