""" Management of the various versions of MEDCoupling.
Importing this module instead of MEDCoupling directly should allow C3PO to nicely
deal with all possible versions of MEDCoupling.
"""

try:
    # MC version 8 and higher:
    from medcoupling import *   # includes MEDLoader basic API and remapper

    try:
        InterpKernelDEC.release
        MC_VERSION = (9, 7)
    except:
        MC_VERSION = (8, 0)
except:
    # MC version 7
    from MEDLoader import *  # also loads all of MEDCoupling
    from MEDCouplingRemapper import MEDCouplingRemapper

    WriteField = MEDLoader.WriteField
    WriteFieldUsingAlreadyWrittenMesh = MEDLoader.WriteFieldUsingAlreadyWrittenMesh
    WriteUMesh = MEDLoader.WriteUMesh
    WriteMesh = MEDLoader.WriteMesh

    IntensiveConservation = RevIntegral
    IntensiveMaximum = ConservativeVolumic
    ExtensiveConservation = IntegralGlobConstraint
    ExtensiveMaximum = Integral

    DataArray.setContigPartOfSelectedValuesSlice = DataArray.setContigPartOfSelectedValues2

    MC_VERSION = (7, 0)
