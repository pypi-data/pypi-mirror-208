#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2023 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
import numpy
import sys
cimport cython

from cython.operator cimport dereference as deref
from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from libcpp.map cimport map as std_map

from Beam cimport *
from Detector cimport *
from fisx.FisxCythonTools import toBytes, toBytesKeys, toBytesKeysAndValues, toString,  toStringKeys, toStringKeysAndValues, toStringList

cdef class PyBeam:
    cdef Beam *thisptr

    def __cinit__(self):
        self.thisptr = new Beam()

    def __dealloc__(self):
        del self.thisptr

    def setBeam(self, energies, weights=None):
        cdef std_vector[int] characteristic = std_vector[int]()
        cdef std_vector[double] divergency = std_vector[double]()
        if not hasattr(energies, "__len__"):
            energies = numpy.array([energies], dtype=numpy.float64)
        else:
            energies = numpy.array(energies, dtype=numpy.float64, copy=False)
        if weights:
            if not hasattr(weights, "__len__"):
                weights = numpy.array([weights], numpy.float64)
            else:
                weights = numpy.array(weights, dtype=numpy.float64, copy=False)
        else:
            weights = numpy.ones(energies.shape, dtype=numpy.float64)
        return self.thisptr.setBeam(energies,
                                    weights,
                                    characteristic,
                                    divergency)

    def getBeamAsDoubleVectors(self):
        output = self.thisptr.getBeamAsDoubleVectors()
        return output[0], output[1]
#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2020 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
import numpy
import sys
cimport cython

from cython.operator cimport dereference as deref
from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from libcpp.map cimport map as std_map

from Elements cimport *
from Detector cimport *
from fisx.FisxCythonTools import toBytes, toBytesKeys, toBytesKeysAndValues, toString,  toStringKeys, toStringKeysAndValues, toStringList

cdef class PyDetector:
    cdef Detector *thisptr

    def __cinit__(self, materialName, double density=1.0, double thickness=1.0, double funny=1.0):
        self.thisptr = new Detector(toBytes(materialName), density, thickness, funny)

    def __dealloc__(self):
        del self.thisptr

    def getTransmission(self, energies, PyElements elementsLib, double angle=90.):
        if not hasattr(energies, "__len__"):
            energies = numpy.array([energies], numpy.float64)
        return self.thisptr.getTransmission(energies, deref(elementsLib.thisptr), angle)

    def setActiveArea(self, double area):
        self.thisptr.setActiveArea(area)

    def setDiameter(self, double value):
        self.thisptr.setDiameter(value)

    def getActiveArea(self):
        return self.thisptr.getActiveArea()

    def getDiameter(self):
        return self.thisptr.getDiameter()

    def setDistance(self, double value):
        self.thisptr.setDistance(value)

    def getDistance(self):
        return self.thisptr.getDistance()

    def setMaximumNumberOfEscapePeaks(self, int n):
        self.thisptr.setMaximumNumberOfEscapePeaks(n)

    def getEscape(self, double energy, PyElements elementsLib, label="", int update=1):
        label_ = toBytes(label)
        if sys.version < "3.0":
            if update:
                return self.thisptr.getEscape(energy, deref(elementsLib.thisptr), label_, 1)
            else:
                return self.thisptr.getEscape(energy, deref(elementsLib.thisptr), label_, 0)
        else:
            if update:
                return toStringKeysAndValues(self.thisptr.getEscape(energy, deref(elementsLib.thisptr), label_, 1))
            else:
                return toStringKeysAndValues(self.thisptr.getEscape(energy, deref(elementsLib.thisptr), label_, 0))

    def getEscapePeakEnergyThreshold(self):
        return self.thisptr.getEscapePeakEnergyThreshold()

    def getEscapePeakIntensityThreshold(self):
        return self.thisptr.getEscapePeakIntensityThreshold()

    def getEscapePeakNThreshold(self):
        return self.thisptr.getEscapePeakNThreshold()

    def getEscapePeakAlphaIn(self):
        return self.thisptr.getEscapePeakAlphaIn()

    def getThickness(self):
        return self.thisptr.getThickness()

    def getDensity(self):
        return self.thisptr.getDensity()

    def getComposition(self, PyElements elementsLib):
        if sys.version < "3.0":
            return self.thisptr.getComposition(deref(elementsLib.thisptr))
        else:
            return toStringKeysAndValues(self.thisptr.getComposition(deref(elementsLib.thisptr)))
#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2016 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
cimport cython

from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from libcpp.map cimport map as std_map

from Element cimport *
    
cdef class PyElement:
    cdef Element *thisptr

    def __cinit__(self, name, z = 0):
        self.thisptr = new Element(toBytes(name), z)

    def __dealloc__(self):
        del self.thisptr

    def setName(self, name):
        self.thisptr.setName(toBytes(name))

    def setAtomicNumber(self, int z):
        self.thisptr.setAtomicNumber(z)

    def getAtomicNumber(self):
        return self.thisptr.getAtomicNumber()

    def setBindingEnergies(self, std_map[std_string, double] energies):
        self.thisptr.setBindingEnergies(energies)

    def getBindingEnergies(self):
        return self.thisptr.getBindingEnergies()
    
    def setMassAttenuationCoefficients(self,
                                       std_vector[double] energies,
                                       std_vector[double] photo,
                                       std_vector[double] coherent,
                                       std_vector[double] compton,
                                       std_vector[double] pair):
        self.thisptr.setMassAttenuationCoefficients(energies,
                                                    photo,
                                                    coherent,
                                                    compton,
                                                    pair)
    
    def _getDefaultMassAttenuationCoefficients(self):
        return self.thisptr.getMassAttenuationCoefficients()

    def _getSingleMassAttenuationCoefficients(self, double energy):
        return self.thisptr.getMassAttenuationCoefficients(energy)

    def getMassAttenuationCoefficients(self, energy=None):
        if energy is None:
            return self._getDefaultMassAttenuationCoefficients()
        elif hasattr(energy, "__len__"):
            return self._getMultipleMassAttenuationCoefficients(energy)
        else:
            return self._getMultipleMassAttenuationCoefficients([energy])

    def _getMultipleMassAttenuationCoefficients(self, std_vector[double] energy):
        return self.thisptr.getMassAttenuationCoefficients(energy)
                                       
    def setRadiativeTransitions(self, shell,
                                std_vector[std_string] labels,
                                std_vector[double] values):
        self.thisptr.setRadiativeTransitions(toBytes(shell), labels, values)

    def getRadiativeTransitions(self, shell):
        return self.thisptr.getRadiativeTransitions(toBytes(shell))

    def setNonradiativeTransitions(self, shell,
                                   std_vector[std_string] labels,
                                   std_vector[double] values):
        self.thisptr.setNonradiativeTransitions(toBytes(shell), labels, values)

    def getNonradiativeTransitions(self, shell):
        return self.thisptr.getNonradiativeTransitions(toBytes(shell))

    def setShellConstants(self, shell,
                          std_map[std_string, double] valuesDict):
        self.thisptr.setShellConstants(toBytes(shell), valuesDict)

    def getShellConstants(self, shell):
        return self.thisptr.getShellConstants(toBytes(shell))

    #def getXRayLines(self, std_string shell):
    #    return self.thisptr.getXRayLines(shell)
                          
    def getXRayLinesFromVacancyDistribution(self,
                            std_map[std_string, double] vacancyDict):
        return self.thisptr.getXRayLinesFromVacancyDistribution(\
                                vacancyDict)

#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2023 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
import sys
cimport cython

from operator import itemgetter
from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from libcpp.map cimport map as std_map

from Elements cimport *
from Material cimport *

__doc__ = """

Initialization with XCOM mass attenuation cross sections:

import os
from fisx import DataDir
dataDir = DataDir.FISX_DATA_DIR
bindingEnergies = os.path.join(dataDir, "BindingEnergies.dat")
xcomFile = os.path.join(dataDir, "XCOM_CrossSections.dat")
xcom = Elements(dataDir, bindingEnergies, xcomFile)

"""
cdef class PyElements:
    cdef Elements *thisptr

    def __cinit__(self, directoryName="",
                        bindingEnergiesFile="",
                        crossSectionsFile="",
                        pymca=0):
        if len(directoryName) == 0:
            from fisx import DataDir
            directoryName = DataDir.FISX_DATA_DIR
        directoryName = toBytes(directoryName)
        if pymca:
            pymca = 1
            self.thisptr = new Elements(directoryName, pymca)
        else:
            bindingEnergiesFile = toBytes(bindingEnergiesFile)
            crossSectionsFile = toBytes(crossSectionsFile)
            if len(bindingEnergiesFile):
                self.thisptr = new Elements(directoryName, bindingEnergiesFile, crossSectionsFile)
            else:
                self.thisptr = new Elements(directoryName)
                if len(crossSectionsFile):
                    self.thisptr.setMassAttenuationCoefficientsFile(crossSectionsFile)

    def initializeAsPyMca(self):
        """
        Configure the instance to use the same set of data as PyMca.
        """
        import os
        try:
            from PyMca5 import getDataFile
        except ImportError:
            # old fashion way with duplicated data in PyMca and in fisx
            return self.__initializeAsPyMcaOld()

        from fisx import DataDir
        directoryName = DataDir.FISX_DATA_DIR
        bindingEnergies = getDataFile("BindingEnergies.dat")
        xcomFile = getDataFile("XCOM_CrossSections.dat")
        del self.thisptr
        self.thisptr = new Elements(toBytes(directoryName), toBytes(bindingEnergies), toBytes(xcomFile))
        for shell in ["K", "L", "M"]:
            shellConstantsFile = getDataFile(shell+"ShellConstants.dat")
            self.thisptr.setShellConstantsFile(toBytes(shell),
                                               toBytes(shellConstantsFile))
        for shell in ["K", "L", "M"]:
            radiativeRatesFile = getDataFile(shell+"ShellRates.dat")
            self.thisptr.setShellRadiativeTransitionsFile(toBytes(shell), toBytes(radiativeRatesFile))

    def __initializeAsPyMcaOld(self):
        """
        Configure the instance to use the same set of data as PyMca.
        """
        import os
        try:
            from fisx import DataDir
            directoryName = DataDir.FISX_DATA_DIR
            from PyMca5 import PyMcaDataDir
            dataDir = PyMcaDataDir.PYMCA_DATA_DIR
        except ImportError:
            from fisx import DataDir
            directoryName = DataDir.FISX_DATA_DIR
            dataDir = directoryName
        bindingEnergies = os.path.join(dataDir, "BindingEnergies.dat")
        xcomFile = os.path.join(dataDir, "XCOM_CrossSections.dat")
        del self.thisptr
        self.thisptr = new Elements(toBytes(directoryName), toBytes(bindingEnergies), toBytes(xcomFile))
        for shell in ["K", "L", "M"]:
            shellConstantsFile = os.path.join(dataDir, shell+"ShellConstants.dat")
            self.thisptr.setShellConstantsFile(toBytes(shell), toBytes(shellConstantsFile))

        for shell in ["K", "L", "M"]:
            radiativeRatesFile = os.path.join(dataDir, shell+"ShellRates.dat")
            self.thisptr.setShellRadiativeTransitionsFile(toBytes(shell), toBytes(radiativeRatesFile))

    def getElementNames(self):
        return toStringList(self.thisptr.getElementNames())

    def getAtomicMass(self, element):
        return self.thisptr.getAtomicMass(toBytes(element))

    def getAtomicNumber(self, element):
        return self.thisptr.getAtomicNumber(toBytes(element))

    def getDensity(self, element):
        return self.thisptr.getDensity(toBytes(element))

    def getLongName(self, element):
        return toString(self.thisptr.getLongName(toBytes(element)))

    def getColumn(self, element):
        return self.thisptr.getColumn(toBytes(element))

    def getRow(self, std_string element):
        return self.thisptr.getRow(toBytes(element))

    def getMaterialNames(self):
        return toStringList(self.thisptr.getMaterialNames())

    def getComposition(self, materialOrFormula):
        if sys.version < "3.0":
            return self.thisptr.getComposition(toBytes(materialOrFormula))
        else:
            return toStringKeys(self.thisptr.getComposition(toBytes(materialOrFormula)))

    def __dealloc__(self):
        del self.thisptr

    def addMaterial(self, PyMaterial material, int errorOnReplace=1):
        self.thisptr.addMaterial(deref(material.thisptr), errorOnReplace)

    def setShellConstantsFile(self, mainShellName, fileName):
        """
        Load main shell (K, L or M) constants from file (fluorescence and Coster-Kronig yields)
        """
        self.thisptr.setShellConstantsFile(toBytes(mainShellName), toBytes(fileName))

    def getShellConstantsFile(self, mainShellName):
        if sys.version < "3.0":
            return self.thisptr.getShellConstantsFile(mainShellName)
        else:
            return toString(self.thisptr.getShellConstantsFile(toBytes(mainShellName)))

    def setShellRadiativeTransitionsFile(self, mainShellName, fileName):
        """
        Load main shell (K, L or M) X-ray emission rates from file.
        The library normalizes internally.
        """
        self.thisptr.setShellRadiativeTransitionsFile(toBytes(mainShellName), toBytes(fileName))

    def getShellRadiativeTransitionsFile(self, mainShellName):
        if sys.version < "3.0":
            return self.thisptr.getShellRadiativeTransitionsFile(mainShellName)
        else:
            return toString(self.thisptr.getShellRadiativeTransitionsFile(toBytes(mainShellName)))

    def getShellNonradiativeTransitionsFile(self, mainShellName):
        if sys.version < "3.0":
            return self.thisptr.getShellNonradiativeTransitionsFile(mainShellName)
        else:
            return toString(self.thisptr.getShellNonradiativeTransitionsFile(toBytes(mainShellName)))

    def setMassAttenuationCoefficients(self,
                                       std_string element,
                                       std_vector[double] energies,
                                       std_vector[double] photo,
                                       std_vector[double] coherent,
                                       std_vector[double] compton,
                                       std_vector[double] pair):
        self.thisptr.setMassAttenuationCoefficients(element,
                                                    energies,
                                                    photo,
                                                    coherent,
                                                    compton,
                                                    pair)
    def setMassAttenuationCoefficientsFile(self, crossSectionsFile):
        self.thisptr.setMassAttenuationCoefficientsFile(toBytes(crossSectionsFile))

    def _getSingleMassAttenuationCoefficients(self, std_string element,
                                                     double energy):
        if sys.version < "3.0":
            return self.thisptr.getMassAttenuationCoefficients(element, energy)
        else:
            return toStringKeys(self.thisptr.getMassAttenuationCoefficients(element, energy))

    def _getElementDefaultMassAttenuationCoefficients(self, std_string element):
        if sys.version < "3.0":
            return self.thisptr.getMassAttenuationCoefficients(element)
        else:
            return toStringKeys(self.thisptr.getMassAttenuationCoefficients(element))

    def getElementMassAttenuationCoefficients(self, element, energy=None):
        if energy is None:
            return self._getElementDefaultMassAttenuationCoefficients(toBytes(element))
        elif hasattr(energy, "__len__"):
            return self._getMultipleMassAttenuationCoefficients(toBytes(element),
                                                                       energy)
        else:
            return self._getMultipleMassAttenuationCoefficients(toBytes(element),
                                                                       [energy])

    def _getMultipleMassAttenuationCoefficients(self, std_string element,
                                                       std_vector[double] energy):
        if sys.version < "3.0":
            return self.thisptr.getMassAttenuationCoefficients(element, energy)
        else:
            return toStringKeys(self.thisptr.getMassAttenuationCoefficients(element, energy))

    def getMassAttenuationCoefficients(self, name, energy=None):
        """
        name can be an element, a formula or a material composition given as a dictionary:
            key is the element name
            fraction is the mass fraction of the element.

        WARNING: The library renormalizes in order to make sure the sum of mass
                 fractions is 1.

        It gives back the mass attenuation coefficients at the given energies as a map where
        the keys are the different physical processes and the values are lists of the
        calculated values via log-log interpolation in the internal table.
        """
        if hasattr(name, "keys"):
            return self._getMaterialMassAttenuationCoefficients(toBytes(name), energy)
        elif energy is None:
            return self._getElementDefaultMassAttenuationCoefficients(toBytes(name))
        elif hasattr(energy, "__len__"):
            return self._getMultipleMassAttenuationCoefficients(toBytes(name), energy)
        else:
            # do not use the "single" version to have always the same signature
            return self._getMultipleMassAttenuationCoefficients(toBytes(name), [energy])

    def getExcitationFactors(self, name, energy, weight=None):
        """
        getExcitationFactors(name, energy, weight=None)
        Given energy(s) and (optional) weight(s), for the specfified element, this method returns
        the emitted X-ray already corrected for cascade and fluorescence yield.
        It is the equivalent of the excitation factor in D.K.G. de Boer's paper.
        """
        if hasattr(energy, "__len__"):
            if weight is None:
                weight = [1.0] * len(energy)
            return self._getExcitationFactors(toBytes(name), energy, weight)[0]
        else:
            energy = [energy]
            if weight is None:
                weight = [1.0]
            else:
                weight = [weight]
            return self._getExcitationFactors(toBytes(name), energy, weight)

    def _getMaterialMassAttenuationCoefficients(self, elementDict, energy):
        """
        elementDict is a dictionary of the form:
        elmentDict[key] = fraction where:
            key is the element name
            fraction is the mass fraction of the element.

        WARNING: The library renormalizes in order to make sure the sum of mass
                 fractions is 1.
        """

        if hasattr(energy, "__len__"):
            return self._getMassAttenuationCoefficients(elementDict, energy)
        else:
            return self._getMassAttenuationCoefficients(elementDict, [energy])

    def _getMassAttenuationCoefficients(self, std_map[std_string, double] elementDict,
                                              std_vector[double] energy):
        return self.thisptr.getMassAttenuationCoefficients(elementDict, energy, 0)

    def _getExcitationFactors(self, std_string element,
                                   std_vector[double] energies,
                                   std_vector[double] weights):
        if sys.version < "3.0":
            return self.thisptr.getExcitationFactors(element, energies, weights)
        else:
            return [toStringKeysAndValues(x) for x in self.thisptr.getExcitationFactors(element, energies, weights)]

    def getPeakFamilies(self, nameOrVector, energy):
        """
        getPeakFamilies(nameOrVector, energy)

        Given an energy and a reference to an elements library return dictionarys.
        The key is the peak family ("Si K", "Pb L1", ...) and the value the binding energy.
        """
        if type(nameOrVector) in [type([]), type(())]:
            if sys.version < "3.0":
                return sorted(self._getPeakFamiliesFromVectorOfElements(nameOrVector, energy), key=itemgetter(1))
            else:
                nameOrVector = [toBytes(x) for x in nameOrVector]
                return [(toString(x[0]), x[1]) for x in \
                        sorted(self._getPeakFamiliesFromVectorOfElements(nameOrVector, energy), key=itemgetter(1))]
        else:
            if sys.version < "3.0":
                return sorted(self._getPeakFamilies(toBytes(nameOrVector), energy), key=itemgetter(1))
            else:
                return [(toString(x[0]), x[1]) for x in \
                        sorted(self._getPeakFamilies(toBytes(nameOrVector), energy), key=itemgetter(1))]

    def _getPeakFamilies(self, std_string name, double energy):
        return self.thisptr.getPeakFamilies(name, energy)

    def _getPeakFamiliesFromVectorOfElements(self, std_vector[std_string] elementList, double energy):
        return self.thisptr.getPeakFamilies(elementList, energy)

    def getBindingEnergies(self, elementName):
        if sys.version < "3.0":
            return self.thisptr.getBindingEnergies(elementName)
        else:
            return toStringKeys(self.thisptr.getBindingEnergies(toBytes(elementName)))

    def getEscape(self, composition, double energy, double energyThreshold=0.010,
                                        double intensityThreshold=1.0e-7,
                                        int nThreshold=4 ,
                                        double alphaIn=90.,
                                        double thickness=0.0):
        if sys.version_info < (3, ):
            return self.thisptr.getEscape(toBytesKeys(composition), energy, energyThreshold, intensityThreshold, nThreshold,
                                         alphaIn, thickness)
        else:
            result = toStringKeys(self.thisptr.getEscape(toBytesKeys(composition), energy, energyThreshold,
                                intensityThreshold, nThreshold, alphaIn, thickness))
            keyList =list(result.keys())
            for key in keyList:
                result[key] = toStringKeys(result[key])
            return result

    def updateEscapeCache(self, composition, std_vector[double] energyList, double energyThreshold=0.010,
                                        double intensityThreshold=1.0e-7,
                                        int nThreshold=4 ,
                                        double alphaIn=90.,
                                        double thickness=0.0):
        self.thisptr.updateEscapeCache(toBytesKeys(composition), energyList, energyThreshold, intensityThreshold, nThreshold,
                                      alphaIn, thickness)

    def getShellConstants(self, elementName, subshell):
        if sys.version < "3.0":
            return self.thisptr.getShellConstants(elementName, subshell)
        else:
            return toStringKeys(self.thisptr.getShellConstants(toBytes(elementName), toBytes(subshell)))

    def getEmittedXRayLines(self, elementName, double energy=1000.):
        if sys.version < "3.0":
            return self.thisptr.getEmittedXRayLines(elementName, energy)
        else:
            return toStringKeys(self.thisptr.getEmittedXRayLines(toBytes(elementName), energy))

    def getRadiativeTransitions(self, elementName, subshell):
        if sys.version < "3.0":
            return self.thisptr.getRadiativeTransitions(elementName, subshell)
        else:
            return toStringKeys(self.thisptr.getRadiativeTransitions(toBytes(elementName), toBytes(subshell)))

    def getNonradiativeTransitions(self, elementName, subshell):
        if sys.version < "3.0":
            return self.thisptr.getNonradiativeTransitions(elementName, subshell)
        else:
            return toStringKeys(self.thisptr.getNonradiativeTransitions(toBytes(elementName), toBytes(subshell)))

    def setElementCascadeCacheEnabled(self, elementName, int flag = 1):
        self.thisptr.setElementCascadeCacheEnabled(toBytes(elementName), flag)

    def emptyElementCascadeCache(self, elementName):
        self.thisptr.emptyElementCascadeCache(toBytes(elementName))

    def fillCache(self, elementName, std_vector[double] energy):
        """
        Optimization methods to keep the calculations at a set of energies
        in cache.
        Clear the calculation cache of given element and fill it at the
        selected energies
        """
        self.thisptr.fillCache(toBytes(elementName), energy)

    def updateCache(self, elementName, std_vector[double] energy):
        """
        Update the element cache with those energy values not already present.
        The existing values will be kept.
        """
        self.thisptr.updateCache(toBytes(elementName), energy)

    def setCacheEnabled(self, elementName, int flag = 1):
        """
        Enable or disable the use of the stored calculations (if any).
        It does not clear the cache when disabling.
        """
        self.thisptr.setCacheEnabled(toBytes(elementName), flag)

    def setEscapeCacheEnabled(self, int flag = 1):
        """
        Enable or disable the use of the stored calculations (if any).
        It does not clear the cache when disabling.
        """
        self.thisptr.setEscapeCacheEnabled(flag)

    def clearCache(self, elementName):
        """
        Clear the calculation cache
        """
        self.thisptr.clearCache(toBytes(elementName))

    def isCacheEnabled(self, elementName):
        """
        Return 1 or 0 if the calculation cache is enabled or not
        """
        return self.thisptr.isCacheEnabled(toBytes(elementName))

    def isEscapeCacheEnabled(self):
        """
        Return 1 or 0 if the calculation cache is enabled or not
        """
        return self.thisptr.isEscapeCacheEnabled()

    def getCacheSize(self, elementName):
        """
        Return the number of energies for which the calculations are stored
        """
        return self.thisptr.getCacheSize(toBytes(elementName))

    def removeMaterials(self):
        self.thisptr.removeMaterials()

    def getInitialPhotoelectricVacancyDistribution(self, elementName, energy):
        """
        Given one energy, give the initial distribution of vacancies (before cascade) due to
        photoelectric effect.
        The output map keys correspond to the different subshells and the values are just
        mu_photoelectric(shell, E)/mu_photoelectric(total, E).
        """
        return toStringKeys(self.thisptr.getInitialPhotoelectricVacancyDistribution( \
                                    toBytes(elementName), energy))
    
    def getCascadeModifiedVacancyDistribution(self, elementName, distribution):
        return self._getCascadeModifiedVacancyDistribution(toBytes(elementName),
                                                    toBytesKeys(distribution))

    def _getCascadeModifiedVacancyDistribution(self, std_string elementName,
                                                    std_map[std_string, double] distribution):
        return toStringKeysAndValues(self.thisptr.getCascadeModifiedVacancyDistribution( \
                                    elementName, distribution))

    def getXRayLinesFromVacancyDistribution(self, elementName, distribution,
                                            cascade=1, useFluorescenceYield=1):
        """ 
        Given an initial vacancy distribution, returns the emitted X-rays.

        Input:
        distribution - Map[key, double] of the form [(sub)shell][amount of vacancies]
        cascade - Consider de-excitation cascade (default is 1 = true)
        useFluorescenceYield - Correct by fluorescence yield (default is 1 = true)

        Output:
        map[key]["rate"] - emission rate where key is the transition line (ex. KL3)
        map[key]["energy"] - emission energy where key is the transition line (ex. KL3)
        """
        return self._getXRayLinesFromVacancyDistribution(toBytes(elementName),
                                                         toBytesKeysAndValues(distribution),
                                                         cascade,
                                                         useFluorescenceYield)

    def _getXRayLinesFromVacancyDistribution(self, std_string elementName,
                                             std_map[std_string, double] distribution,
                                             int cascade=1, int useFluorescenceYield=1):
        return toStringKeysAndValues(self.thisptr.getXRayLinesFromVacancyDistribution( \
                                            elementName,
                                            distribution,
                                            cascade,
                                            useFluorescenceYield))

#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2016 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
#import numpy as np
#cimport numpy as np
cimport cython

from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from libcpp.map cimport map as std_map

from EPDL97 cimport *
    
cdef class PyEPDL97:
    cdef EPDL97 *thisptr

    def __cinit__(self, name=None):
        if name is None:
            from fisx import DataDir
            name = DataDir.FISX_DATA_DIR
        self.thisptr = new EPDL97(toBytes(name))

    def __dealloc__(self):
        del self.thisptr

    def setDataDirectory(self, name):
        self.thisptr.setDataDirectory(toBytes(name))

    def setBindingEnergies(self, int z, std_map[std_string, double] energies):
        self.thisptr.setBindingEnergies(z, energies)

    def getBindingEnergies(self, int z):
        return toStringKeys(self.thisptr.getBindingEnergies(z))
    
    def getMassAttenuationCoefficients(self, z, energy=None):
        if energy is None:
            return toStringKeys(self._getDefaultMassAttenuationCoefficients(z))
        elif hasattr(energy, "__len__"):
            return toStringKeys(self._getMultipleMassAttenuationCoefficients(z, energy))
        else:
            return toStringKeys(self._getMultipleMassAttenuationCoefficients(z, [energy]))

    def _getDefaultMassAttenuationCoefficients(self, int z):
        return self.thisptr.getMassAttenuationCoefficients(z)

    def _getSingleMassAttenuationCoefficients(self, int z, double energy):
        return self.thisptr.getMassAttenuationCoefficients(z, energy)

    def _getMultipleMassAttenuationCoefficients(self, int z, std_vector[double] energy):
        return self.thisptr.getMassAttenuationCoefficients(z, energy)
                                       
    def getPhotoelectricWeights(self, z, energy):
        if hasattr(energy, "__len__"):
            return toStringKeys(self._getMultiplePhotoelectricWeights(z, energy))
        else:
            return toStringKeys(self._getMultiplePhotoelectricWeights(z, [energy]))

    def _getSinglePhotoelectricWeights(self, int z, double energy):
        return self.thisptr.getPhotoelectricWeights(z, energy)

    def _getMultiplePhotoelectricWeights(self, int z, std_vector[double] energy):
        return self.thisptr.getPhotoelectricWeights(z, energy)
#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2023 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
import numpy
#cimport numpy as np
cimport cython

from cython.operator cimport dereference as deref
from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from libcpp.map cimport map as std_map
from libcpp.map cimport pair as std_pair
from operator import itemgetter

from Elements cimport *
from Material cimport *
from Layer cimport *

cdef class PyLayer:
    cdef Layer *thisptr

    def __cinit__(self, materialName, double density=1.0, double thickness=1.0, double funny=1.0):
        self.thisptr = new Layer(toBytes(materialName), density, thickness, funny)

    def __dealloc__(self):
        del self.thisptr

    def getComposition(self, PyElements elementsLib):
        """
        getComposition(elementsLib)

        Given a reference to an elements library, it gives back a dictionary where the keys are the
        elements and the values the mass fractions.
        """
        return toStringKeys(self.thisptr.getComposition(deref(elementsLib.thisptr)))

    def getTransmission(self, energies, PyElements elementsLib, double angle=90.):
        """
        getTransmission(energies, ElementsLibraryInstance, angle=90.)

        Given a list of energies and a reference to an elements library returns
        the layer transmission according to the incident angle (default 90.)
        """
        if not hasattr(energies, "__len__"):
            energies = numpy.array([energies], numpy.float64)
        return self.thisptr.getTransmission(energies, deref(elementsLib.thisptr), angle)

    def setMaterial(self, PyMaterial material):
        """
        setMaterial(MaterialInstance)

        Set the material of the layer. It has to be an instance!
        """
        self.thisptr.setMaterial(deref(material.thisptr))

    def getPeakFamilies(self, double energy, PyElements elementsLib):
        """
        getPeakFamilies(energy, ElementsLibraryInstance)

        Given an energy and a reference to an elements library return a list of pairs.
        First is the peak family ("Si K", "Pb L1", ...) and second the value the binding energy.
        """
        tmpResult = self.thisptr.getPeakFamilies(energy, deref(elementsLib.thisptr))
        return [(toString(x[0]), x[1]) for x in sorted(tmpResult, key=itemgetter(1))]

#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2018 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
import sys
cimport cython

from cython.operator cimport dereference as deref
from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from libcpp.map cimport map as std_map

from Material cimport *

cdef class PyMaterial:
    cdef Material *thisptr

    def __cinit__(self, materialName, double density=1.0, double thickness=1.0, comment=""):
        materialName = toBytes(materialName)
        comment = toBytes(comment)
        self.thisptr = new Material(materialName, density, thickness, comment)

    def __dealloc__(self):
        del self.thisptr

    def getName(self):
        return toString(self.thisptr.getName())

    def setName(self, name):
        name = toBytes(name)
        self.thisptr.setName(name)

    def setCompositionFromLists(self, elementList, std_vector[double] massFractions):
        if sys.version > "3.0":
            elementList = [toBytes(x) for x in elementList]
        self.thisptr.setComposition(elementList, massFractions)

    def setComposition(self, composition):
        if sys.version > "3.0":
            composition = toBytesKeys(composition)
        self.thisptr.setComposition(composition)

    def getComposition(self):
        return toStringKeys(self.thisptr.getComposition())
#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2017 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
import numpy
#cimport numpy as np
cimport cython

from libcpp.vector cimport vector as std_vector

from Math cimport *

cdef class PyMath:
    cdef Math *thisptr

    def __cinit__(self):
        self.thisptr = new Math()

    def __dealloc__(self):
        del self.thisptr

    def E1(self, double x):
        return self.thisptr.E1(x)

    def En(self, int n, double x):
        return self.thisptr.En(n, x)

    def deBoerD(self, double x):
        return self.thisptr.deBoerD(x)

    def deBoerL0(self, double mu1, double mu2, double muj, double density = 0.0, double thickness = 0.0):
        """
        The case the product density * thickness is 0.0 is for calculating the thick target limit
        """
        return self.thisptr.deBoerL0(mu1, mu2, muj, density, thickness)

    def deBoerX(self, double p, double q, double d1, double d2, double mu_1_j, double mu_2_j, double mu_b_d_t = 0.0):
        """
        static double deBoerX(const double & p, const double & q, \
                              const double & d1, const double & d2, \
                              const double & mu_1_j, const double & mu_2_j, \
                              const double & mu_b_j_d_t = 0.0);
        For multilayers
        p and q following article
        d1 is the product density * thickness of fluorescing layer
        d2 is the product density * thickness of layer j originating the secondary excitation
        mu_1_j is the mass attenuation coefficient of fluorescing layer at j excitation energy
        mu_2_j is the mass attenuation coefficient of layer j at j excitation energy
        mu_b_d_t is the sum of the products mu * density * thickness of layers between layer i and j
        """
        return self.thisptr.deBoerX(p, q, d1, d2, mu_1_j, mu_2_j, mu_b_d_t)

    def erf(self, double x):
        """
        Calculate the error function erf(x)
        """
        return self.thisptr.erf(x)

    def erfc(self, double x):
        """
        Calculate the complementary error function erfc(x)
        """
        return self.thisptr.erfc(x)
#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2016 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
import sys
cimport cython

#from libcpp.string cimport string as std_string
#from libcpp.vector cimport vector as std_vector
#from libcpp.map cimport map as std_map

from Shell cimport *

cdef class PyShell:
    cdef Shell *thisptr

    def __cinit__(self, name):
        name = toBytes(name)
        self.thisptr = new Shell(name)

    def __dealloc__(self):
        del self.thisptr

    def setRadiativeTransitions(self, transitions, std_vector[double] values):
        if sys.version > "3.0":
            transitions = [toBytes(x) for x in transitions]
        self.thisptr.setRadiativeTransitions(transitions, values)

    def setNonradiativeTransitions(self, transitions, std_vector[double] values):
        if sys.version > "3.0":
            transitions = [toBytes(x) for x in transitions]
        self.thisptr.setNonradiativeTransitions(transitions, values)

    def getAugerRatios(self):
        return self.thisptr.getAugerRatios()

    def getCosterKronigRatios(self):
        return self.thisptr.getCosterKronigRatios()

    def getFluorescenceRatios(self):
        return self.thisptr.getFluorescenceRatios()

    def getRadiativeTransitions(self):
        return self.thisptr.getRadiativeTransitions()

    def getNonradiativeTransitions(self):
        return self.thisptr.getNonradiativeTransitions()

    def getDirectVacancyTransferRatios(self, subshell):
        return self.thisptr.getDirectVacancyTransferRatios(toBytes(subshell))

    def setShellConstants(self, shellConstants):
        if sys.version > "3.0":
            shellConstants = toBytesKeys(shellConstants)
        self.thisptr.setShellConstants(shellConstants)

    def getShellConstants(self):
        return self.thisptr.getShellConstants()
#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2016 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
#import numpy as np
#cimport numpy as np
cimport cython

from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from libcpp.map cimport map as std_map

from SimpleIni cimport *
    
cdef class PySimpleIni:
    cdef SimpleIni *thisptr

    def __cinit__(self, name):
        name = toBytes(name)
        self.thisptr = new SimpleIni(name)

    def __dealloc__(self):
        del self.thisptr

    def getKeys(self):
        return self.thisptr.getSections()

    def readKey(self, key):
        key = toBytes(key)
        return self.thisptr.readSection(key)
#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2016 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
#import numpy as np
#cimport numpy as np
cimport cython

from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from libcpp.map cimport map as std_map

from SimpleSpecfile cimport *
    
cdef class PySimpleSpecfile:
    cdef SimpleSpecfile *thisptr

    def __cinit__(self, name):
        name = toBytes(name)
        self.thisptr = new SimpleSpecfile(name)

    def __dealloc__(self):
        del self.thisptr

    def getNumberOfScans(self):
        return self.thisptr.getNumberOfScans()

    #def getScanHeader(self, int scanIndex):
    #    return self.thisptr.getScanHeader(scanIndex)

    def getScanLabels(self, int scanIndex):
        if sys.version < '3':
            return self.thisptr.getScanLabels(scanIndex)
        else:
            bytesLabels = self.thisptr.getScanLabels(scanIndex)
            return [toString(x) for x in bytesLabels]

    def getScanData(self, int scanIndex):
        return self.thisptr.getScanData(scanIndex)
#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2020 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
import sys
cimport cython

from cython.operator cimport dereference as deref
from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from libcpp.map cimport map as std_map

from TransmissionTable cimport *

cdef class PyTransmissionTable:
    cdef TransmissionTable *thisptr

    def __cinit__(self):
        self.thisptr = new TransmissionTable()

    def __dealloc__(self):
        del self.thisptr

    def getName(self):
        return toString(self.thisptr.getName())

    def setName(self, name):
        name = toBytes(name)
        self.thisptr.setName(name)

    def getComment(self):
        return toString(self.thisptr.getComment())

    def setComment(self, comment):
        comment = toBytes(comment)
        self.thisptr.setComment(comment)

    def setTransmissionTableFromLists(self,
                             std_vector[double] energy, \
                             std_vector[double] transmission, \
                             name="",
                             comment=""):
        name = toBytes(name)
        comment = toBytes(comment)
        self.thisptr.setTransmissionTable(energy,
                                          transmission, \
                                          name,
                                          comment)

    def setTransmissionTable(self,
                             std_map[double, double] transmissionTable, \
                             name="",
                             comment=""):
        name = toBytes(name)
        comment = toBytes(comment)
        self.thisptr.setTransmissionTable(transmissionTable,
                                          name,
                                          comment)

    def getTransmissionTable(self):
        return self.thisptr.getTransmissionTable()

    def getTransmission(self, energy):
        if hasattr(energy, "__len__"):
            return self._getTransmissionMultiple(energy)
        else:
            return self._getTransmissionSingle(energy)
        
    def _getTransmissionSingle(self, double energy):
        return self.thisptr.getTransmission(energy)

    def _getTransmissionMultiple(self, std_vector[double] energy):
        return self.thisptr.getTransmission(energy)
#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2016 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
cimport cython

#from libcpp.string cimport string as std_string

from Version cimport fisxVersion as _fisxVersion

def fisxVersion():
    return toString(_fisxVersion())
#/*##########################################################################
#
# The fisx library for X-Ray Fluorescence
#
# Copyright (c) 2014-2023 European Synchrotron Radiation Facility
#
# This file is part of the fisx X-ray developed by V.A. Sole
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
#import numpy as np
#cimport numpy as np
cimport cython

from cython.operator cimport dereference as deref
from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from libcpp.map cimport map as std_map

from XRF cimport *
from Layer cimport *
from TransmissionTable cimport *
from Beam cimport *

cdef class PyXRF:
    cdef XRF *thisptr

    def __cinit__(self, std_string configurationFile=""):
        if len(configurationFile):
            self.thisptr = new XRF(configurationFile)
        else:
            self.thisptr = new XRF()

    def __dealloc__(self):
        del self.thisptr

    def readConfigurationFromFile(self, fileName):
        """
        Read the configuration from a PyMca .cfg ot .fit file
        """
        self.thisptr.readConfigurationFromFile(toBytes(fileName))

    def setBeam(self, energies, weights=None, characteristic=None, divergency=None):
        if not hasattr(energies, "__len__"):
            if divergency is None:
                divergency = 0.0
            self._setSingleEnergyBeam(energies, divergency)
        else:
            if weights is None:
                weights = [1.0] * len(energies)
            elif not hasattr(weights, "__len__"):
                weights = [weights]
            if characteristic is None:
                characteristic = [1] * len(energies)
            if divergency is None:
                divergency = [0.0] * len(energies)

            self._setBeam(energies, weights, characteristic, divergency)

    def _setSingleEnergyBeam(self, double energy, double divergency):
        self.thisptr.setSingleEnergyBeam(energy, divergency)

    def _setBeam(self, std_vector[double] energies, std_vector[double] weights, \
                       std_vector[int] characteristic, std_vector[double] divergency):
        self.thisptr.setBeam(energies, weights, characteristic, divergency)

    def setBeamFilters(self, layerList):
        """
        Due to wrapping constraints, the filter list must have the form:
        [[Material name or formula0, density0, thickness0, funny factor0],
         [Material name or formula1, density1, thickness1, funny factor1],
         ...
         [Material name or formulan, densityn, thicknessn, funny factorn]]

        Unless you know what you are doing, the funny factors must be 1.0
        """
        cdef std_vector[Layer] container
        if len(layerList):
            if isinstance(layerList[0], PyLayer):
                for layer in layerList:
                    self._addLayerToLayerVector(layer, container)
            elif len(layerList[0]) == 4:
                for name, density, thickness, funny in layerList:
                    container.push_back(Layer(toBytes(name), density, thickness, funny))
            else:
                for name, density, thickness in layerList:
                    container.push_back(Layer(toBytes(name), density, thickness, 1.0))
        self.thisptr.setBeamFilters(container)

    def setUserBeamFilters(self, pyTransmissionTableList):
        """
        Provide a list of already instantiated transmision tables to be used
        as filters between beam and sample
        """
        self._fillTransmissionTable(pyTransmissionTableList, "filter")

    def _fillTransmissionTable(self, pyTransmissionTableList, function):
        if function not in ["filter", "attenuator"]:
            raise ValueError("Please specify usage as filter or as attenuator")
        if len(pyTransmissionTableList):
            if hasattr(pyTransmissionTableList[0], "getTransmissionTable"):
                instantiated = True
            else:
                instantiated = False
        else:
            instantiated = True
        cdef std_vector[TransmissionTable] container
        cdef TransmissionTable t
        if instantiated:
            for item in pyTransmissionTableList:
                name = item.getName()
                comment = item.getComment()
                table = item.getTransmissionTable()
                t = TransmissionTable()
                t.setTransmissionTable(table, name, comment)
                container.push_back(t)
        else:
            for item in pyTransmissionTableList:
                t = TransmissionTable()
                if len(item) == 4:
                    t.setTransmissionTable(item[0],
                                           item[1],
                                           toBytes(item[2]),
                                           toBytes(item[3]))
                elif hasattr(item[0], "keys"):
                    t.setTransmissionTable(item[0],
                                           toBytes(item[1]),
                                           toBytes(item[2]))
                else:
                    raise ValueError("Not appropriate input type or length")
                container.push_back(t)
        if function == "filter":
            self.thisptr.setUserBeamFilters(container)
        else:
            self.thisptr.setUserAttenuators(container)

    def setSample(self, layerList, referenceLayer=0):
        """
        Due to wrapping constraints, the list must have the form:
        [[Material name or formula0, density0, thickness0, funny factor0],
         [Material name or formula1, density1, thickness1, funny factor1],
         ...
         [Material name or formulan, densityn, thicknessn, funny factorn]]

        Unless you know what you are doing, the funny factors must be 1.0
        """
        cdef std_vector[Layer] container
        if len(layerList):
            if isinstance(layerList[0], PyLayer):
                for layer in layerList:
                    self._addLayerToLayerVector(layer, container)
            elif len(layerList[0]) == 4:
                for name, density, thickness, funny in layerList:
                    container.push_back(Layer(toBytes(name), density, thickness, funny))
            else:
                for name, density, thickness in layerList:
                    container.push_back(Layer(toBytes(name), density, thickness, 1.0))
        self.thisptr.setSample(container, referenceLayer)


    def setAttenuators(self, layerList):
        """
        Due to wrapping constraints, the filter list must have the form:
        [[Material name or formula0, density0, thickness0, funny factor0],
         [Material name or formula1, density1, thickness1, funny factor1],
         ...
         [Material name or formulan, densityn, thicknessn, funny factorn]]

        Unless you know what you are doing, the funny factors must be 1.0
        """
        cdef std_vector[Layer] container
        if len(layerList):
            if isinstance(layerList[0], PyLayer):
                for layer in layerList:
                    self._addLayerToLayerVector(layer, container)
            elif len(layerList[0]) == 4:
                for name, density, thickness, funny in layerList:
                    container.push_back(Layer(toBytes(name), density, thickness, funny))
            else:
                for name, density, thickness in layerList:
                    container.push_back(Layer(toBytes(name), density, thickness, 1.0))
        return self.thisptr.setAttenuators(container)

    cdef void _addLayerToLayerVector(self, PyLayer layer, std_vector[Layer]& container):
        container.push_back(deref(layer.thisptr))

    def setUserAttenuators(self, pyTransmissionTableList):
        """
        Provide a list of in which each item is either an already instantiated
        PyTransmissionTable or each item is a list of the arguments of the
        PyTransmissionTable method setTransmissionTable.
        This transmission tables will be used as filters between sample and
        detector
        """
        self._fillTransmissionTable(pyTransmissionTableList, "attenuator")

    def setDetector(self, PyDetector detector):
        self.thisptr.setDetector(deref(detector.thisptr))

    def setGeometry(self, double alphaIn, double alphaOut, double scatteringAngle = -90.0):
        if scatteringAngle < 0.0:
            self.thisptr.setGeometry(alphaIn, alphaOut, alphaIn + alphaOut)
        else:
            self.thisptr.setGeometry(alphaIn, alphaOut, scatteringAngle)

    def getLayerComposition(self, PyLayer layerInstance, PyElements elementsLibrary):
        return toStringKeys(self.thisptr.getLayerComposition(deref(layerInstance.thisptr),
                                                deref(elementsLibrary.thisptr)))

    def getLayerMassAttenuationCoefficients(self, PyLayer layerInstance, energies, \
                                            PyElements elementsLibrary):
        if not hasattr(energies, "__len__"):
            return toStringKeys(self._getLayerMassAttenuationCoefficientsSingle( \
                                    layerInstance, \
                                    energies, elementsLibrary))
        else:
            return toStringKeys(self._getLayerMassAttenuationCoefficientsMultiple( \
                                    layerInstance,
                                    energies,
                                    elementsLibrary))

    def _getLayerMassAttenuationCoefficientsSingle(self, PyLayer layerInstance, \
                                            double energy, \
                                            PyElements elementsLibrary):
        cdef std_map[std_string, double] composition
        composition.clear()
        return self.thisptr.getLayerMassAttenuationCoefficients( \
                                    deref(layerInstance.thisptr), \
                                    energy, deref(elementsLibrary.thisptr), \
                                    composition)

    def _getLayerMassAttenuationCoefficientsMultiple(self, PyLayer layerInstance, \
                                            std_vector[double] energies, \
                                            PyElements elementsLibrary):
        cdef std_map[std_string, double] composition
        composition.clear()
        return self.thisptr.getLayerMassAttenuationCoefficients( \
                                    deref(layerInstance.thisptr), \
                                    energies, deref(elementsLibrary.thisptr), \
                                    composition)

    def getLayerTransmission(self, PyLayer layerInstance, energies, \
                             PyElements elementsLibrary, angle=90.):
        if not hasattr(energies, "__len__"):
            return self._getLayerTransmissionSingle( \
                                    layerInstance, \
                                    energies, \
                                    elementsLibrary, \
                                    angle)
        else:
            return self._getLayerTransmissionMultiple( \
                                    layerInstance, \
                                    energies, \
                                    elementsLibrary, \
                                    angle)

    def _getLayerTransmissionSingle(self, PyLayer layerInstance, double energy, \
                             PyElements elementsLibrary, double angle):
        cdef std_map[std_string, double] composition
        composition.clear()
        return self.thisptr.getLayerTransmission( \
                                    deref(layerInstance.thisptr), \
                                    energy, \
                                    deref(elementsLibrary.thisptr), \
                                    angle, \
                                    composition)

    def _getLayerTransmissionMultiple(self, PyLayer layerInstance, \
                             std_vector[double] energies, \
                             PyElements elementsLibrary, double angle):
        cdef std_map[std_string, double] composition
        composition.clear()
        return self.thisptr.getLayerTransmission( \
                                    deref(layerInstance.thisptr), \
                                    energies, \
                                    deref(elementsLibrary.thisptr), \
                                    angle, \
                                    composition)

    def getLayerPeakFamilies(self, PyLayer layerInstance, double energy, \
                             PyElements elementsLibrary):
        cdef std_map[std_string, double] composition
        composition.clear()
        return toStringKeys(self.thisptr.getLayerPeakFamilies( \
                                    deref(layerInstance.thisptr), \
                                    energy, deref(elementsLibrary.thisptr), \
                                    composition))

    def getMultilayerFluorescence(self, elementFamilyLayer, PyElements elementsLibrary, \
                            int secondary = 0, int useGeometricEfficiency = 1, int useMassFractions = 0, \
                            double secondaryCalculationLimit = 0.0, PyBeam overwritingBeam=PyBeam()):
        """
        Input
        elementFamilyLayer - Vector of strings. Each string represents the information we are interested on.
        "Cr"     - We want the information for Cr, for all line families and sample layers
        "Cr K"   - We want the information for Cr, for the family of K-shell emission lines, in all layers.
        "Cr K 0" - We want the information for Cr, for the family of K-shell emission lines, in layer 0.
        elementsLibrary - Instance of library to be used for all the Physical constants
        secondary - Flag to indicate different levels of secondary excitation to be considered.
                    0 Means not considered
                    1 Consider only intralayer secondary excitation
                    2 Consider intralayer and interlayer secondary excitation
        useGeometricEfficiency - Take into account solid angle or not. Default is 1 (yes)

        useMassFractions - If 0 (default) the output corresponds to the requested information if the mass
        fraction of the element would be one on each calculated sample layer. To get the actual signal, one
        has to multiply bthe rates by the actual mass fraction of the element on each sample layer.
                           If set to 1 the rate will be already corrected by the actual mass fraction.

        Return a complete output of the form
        [Element Family][Layer][line]["energy"] - Energy in keV of the emission line
        [Element Family][Layer][line]["primary"] - Primary rate prior to correct for detection efficiency
        [Element Family][Layer][line]["secondary"] - Secondary rate prior to correct for detection efficiency
        [Element Family][Layer][line]["rate"] - Overall rate
        [Element Family][Layer][line]["efficiency"] - Detection efficiency
        [Element Family][Layer][line][element line layer] - Secondary rate (prior to correct for detection efficiency)
        due to the fluorescence from the given element, line and layer index composing the map key.
        """
        cdef std_vector[std_string] elementFamilyLayerVector
        cdef std_map[std_string, std_map[int, std_map[std_string, std_map[std_string, double]]]] result
        if sys.version > "3.0":
            for x in elementFamilyLayer:
                elementFamilyLayerVector.push_back(toBytes(x))
            with nogil:
                result = self.thisptr.getMultilayerFluorescence( \
                            elementFamilyLayerVector, \
                            deref(elementsLibrary.thisptr), \
                            secondary, useGeometricEfficiency, \
                            useMassFractions, secondaryCalculationLimit, \
                            deref(overwritingBeam.thisptr))
            return toStringKeysAndValues(result)
        else:
            return self.thisptr.getMultilayerFluorescence(elementFamilyLayer, \
                            deref(elementsLibrary.thisptr), \
                            secondary, useGeometricEfficiency, \
                            useMassFractions, secondaryCalculationLimit, deref(overwritingBeam.thisptr))

    def getFluorescence(self, elementNames, PyElements elementsLibrary, \
                            sampleLayer = 0, lineFamily="K", int secondary = 0, \
                            int useGeometricEfficiency = 1, int useMassFractions = 0, \
                            double secondaryCalculationLimit = 0.0,
                            PyBeam overwritingBeam=PyBeam()):

        """
        Input
        elementNames - Single string or Vector of strings. Each string represents the information we are interested on.
        "Cr"         - We want the information for Cr
        ["Cr", "Fe"] - We want the information for Cr and Fe.
        elementsLibrary - Instance of library to be used for all the Physical constants
        sampleLayer - Single integer or vector of integers representing the layers where the calculation has to take place.
                      A negative value implies the calculation will take places in all layers
                      0 Means calculation on top layer, 1 the second, and so on
                      The program expects either a single index or as many indices as element names provided.
        lineFamily - Single string or Vector of strings representing the peak families to calculate.
                     The program expects as many peak families as element names provided.
        secondary  - Flag to indicate different levels of secondary excitation to be considered.
                     0 Means not considered
                     1 Consider only intralayer secondary excitation
                     2 Consider intralayer and interlayer secondary excitation
        useGeometricEfficiency - Take into account solid angle or not. Default is 1 (yes)

        useMassFractions - If 0 (default) the output corresponds to the requested information if the mass
        fraction of the element would be one on each calculated sample layer. To get the actual signal, one
        has to multiply bthe rates by the actual mass fraction of the element on each sample layer.
                           If set to 1 the rate will be already corrected by the actual mass fraction.

        Return a complete output of the form
        [Element Family][Layer][line]["energy"] - Energy in keV of the emission line
        [Element Family][Layer][line]["primary"] - Primary rate prior to correct for detection efficiency
        [Element Family][Layer][line]["secondary"] - Secondary rate prior to correct for detection efficiency
        [Element Family][Layer][line]["rate"] - Overall rate
        [Element Family][Layer][line]["efficiency"] - Detection efficiency
        [Element Family][Layer][line][element line layer] - Secondary rate (prior to correct for detection efficiency)
        due to the fluorescence from the given element, line and layer index composing the map key.
        """
        cdef std_vector[std_string] elementNamesVector
        cdef std_vector[int] sampleLayerIndicesVector
        cdef std_vector[std_string] lineFamiliesVector
        cdef std_map[std_string, std_map[int, std_map[std_string, std_map[std_string, double]]]] result
        cdef Beam beamInstance = Beam();
        cdef std_vector[double] beamEnergies
        cdef std_vector[double] beamWeights
        cdef std_vector[int] dummyIntVec
        cdef std_vector[double] dummyDoubleVec

        if hasattr(elementNames[0], "__len__"):
            # we have received a list of elements
            pass
        else:
            # we have a single element, convert to list
            elementNames = [elementNames]

        if hasattr(sampleLayer, "__len__"):
            # we have received a list of layer indices
            pass
        else:
            # we should have received an integer, convert to list
            sampleLayer = [sampleLayer]

        if len(lineFamily) and hasattr(lineFamily, "__len__"):
            # we have received a list of peak families
            pass
        else:
            # we should have a peak family, convert to list
            lineFamily = [lineFamily]

        # check the sizes match
        if len(lineFamily) != len(elementNames):
            raise IndexError("Number of elements should match the number of requested peak families")

        if len(sampleLayer) > 1:
            if len(sampleLayer) != len(elementNames):
                raise IndexError("Provide a single layer index or as many indices as elements")

        # fill the vectors
        for x in elementNames:
            elementNamesVector.push_back(toBytes(x))

        for x in sampleLayer:
            sampleLayerIndicesVector.push_back(x)

        for x in lineFamily:
            lineFamiliesVector.push_back(toBytes(x))

        with nogil:
            result = self.thisptr.getMultilayerFluorescence(elementNamesVector, deref(elementsLibrary.thisptr), \
                            sampleLayerIndicesVector, lineFamiliesVector, secondary, useGeometricEfficiency, useMassFractions, \
                            secondaryCalculationLimit, deref(overwritingBeam.thisptr))

        return toStringKeysAndValues(result)

    def getGeometricEfficiency(self, int layerIndex = 0):
        return self.thisptr.getGeometricEfficiency(layerIndex)
