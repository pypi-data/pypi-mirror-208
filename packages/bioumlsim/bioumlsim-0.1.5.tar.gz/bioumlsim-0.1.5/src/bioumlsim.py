import jpype
import jpype.imports

def loadSBMLModel(file):
    """
    Loads SBML file and transforms it into object which represents mathematical model.
    Args:
        file (str): path to file
    Returns:
        model
    """
    init()
    print(f"SBML file is loading: {file}.")
    diagram = jpype.JClass("biouml.plugins.sbml.SbmlModelFactory").readDiagram(file)
    return diagram

def init():
    bioUMLPath = 'C:/BioUML_2023.1';
    jpype.startJVM(classpath=[bioUMLPath+'/plugins/*',bioUMLPath+'/plugins/cern.jet.random_1.3.0/colt.jar'])