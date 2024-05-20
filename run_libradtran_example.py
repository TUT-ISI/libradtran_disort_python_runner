#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# In[]:
# ########################################################################
# Run Libradtran example
# ########################################################################
"""
Created on Mon May  6 10:57:19 2024
@author: Arttu Väisänen
FMI: Finnish Meteorological Institute

################## License ##################

MIT License

Copyright (c) 2024 Arttu Väisänen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
# In[]:
# ########################################################################
# Pakages
# ########################################################################

import configparser
import glob
import numpy as np
import run_libradtran_extended as libis

# In[]:
# ########################################################################
# Example 1 simple case
# ########################################################################

"""
This example shows simple case how to use the libradtran runner.
Runner function: run_libradtran needs a dict that contains the inputs 
for libradtran and some settings options as well.

The main input for libradtran uvspec is presented in input_str.

The parser options need to bee specified.
output_format tells the script the shape of output string so that parsing scripts 
can parse it correctly. Shapes are described in libRadtran User's Guide in section 
3.1.5.
In short they are:
output_format = 0 corresponds to string shape were no umu or phi is specified. 
output_format = 1 corresponds to string shape were umu is specified but phi is not.
output_format = 2 corresponds to string shape were umu and phi are specified. 

umu_lenght is just the length of umu vector/array used in program.

In this case no umu is present in input_str so we can but both parser_options to zero

"""

# For this example the you need to specify the libradtran data files path
print("\nRemember to specify the libradtran data files path")
libradtran_data_files_path = "libRadtran-2.0.5/data"

# Main input file in a python string format
input_str = f"data_files_path {libradtran_data_files_path}\n\
    wavelength 550 \n\
    aerosol_vulcan 1\n\
    aerosol_haze 6\n\
    aerosol_season 1\n\
    aerosol_visibility 20.0\n\
    aerosol_angstrom 1.1 0.2\n\
    aerosol_modify ssa scale 0.85\n\
    aerosol_modify gg set 0.70\n\
    rte_solver disort"

# Parser options for the python script
parser_options_dict = {"output_format": 0,
                   "umu_lenght": 0}

# Script needs the location of you libradtran binary
print("\nRemember to specify libradtran binary location!!!")
libradtran_bin_file_loc = "libRadtran-2.0.5/bin"

# Calling the run_libradtran producess the results in format list(configparser object; wavelength)
results_example_1 = libis.run_libradtran(libradtran_bin_file_loc, input_str, parser_options_dict)

print("\nResults are presented in a dict format. User can then create their own code to pick the relevatn information. Result Dict:")
print(results_example_1)


# In[]:
# ########################################################################
# Example 2 Advanced usecase
# ########################################################################

"""
For more advanced input cases, run_conf_files_libradtran function needs to be used.

For this usecase the whole input needs to be set to one configparser object. 

Further you can also run multiple cases as well with this function.

For code to work the main configparser object and sub configparser object need to contain
following variables: 
libradtran_input:: parser_options, main_str
parser_options:: output_format, umu_lenght

Previous example is now set to a configparser object: configuration_simple
"""

# For this example the you need to specify the libradtran data files path
print("\nRemember to specify the libradtran data files path")
libradtran_data_files_path = "libRadtran-2.0.5/data"

# Main input file in a python string format
simple_input_str = f"data_files_path {libradtran_data_files_path}\n\
    wavelength 550 \n\
    aerosol_vulcan 1\n\
    aerosol_haze 6\n\
    aerosol_season 1\n\
    aerosol_visibility 20.0\n\
    aerosol_angstrom 1.1 0.2\n\
    aerosol_modify ssa scale 0.85\n\
    aerosol_modify gg set 0.70\n\
    rte_solver disort"

# Create a configuration object
configuration_simple = configparser.ConfigParser()

# Set parser options to configuration object
configuration_simple["parser_options"] = {"output_format": 0,
                                          "umu_lenght": 0}

# Set main string to configuration object
configuration_simple["main_str"] = {"input_str": simple_input_str}


"""
If other files are needed you can add them by adding temp_strs to the configparser object.

The temp_strs format is the following: it need to contain the name of the variable 
in libradtran input file and then the file contents in string.

A new configparser has been created called: configuration_external_files_1
"""

# Create a configuration object
configuration_external_files_1 = configparser.ConfigParser()

# Set parser options to configuration object
configuration_external_files_1["parser_options"] = {"output_format": 0,
                                                    "umu_lenght": 0}
# Lets create a aerosol profile
heigth = np.array([7, 6, 5, 4, 3, 2, 1, 0])
value = np.array([0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2])

# Library contains a Profile parser
aerosol_profile = libis.profile_parser(heigth, value)

# Include external files to main program
configuration_external_files_1["temp_strs"] = {"aerosol_file tau": aerosol_profile}


"""
NOTE: THE FILES WILL BE BUT UNDER THE rte_solver disort LINE
This can have an effect to the input. Check libradtran manual.
"""

# Main input file in a python string format
input_str_1 = f"data_files_path {libradtran_data_files_path}\n\
    wavelength 450 \n\
    atmosphere_file US-standard\n\
    aerosol_default\n\
    aerosol_modify tau set 0.1\n\
    rte_solver disort\n\
    verbose"

# Set main string to configuration object
configuration_external_files_1["main_str"] = {"input_str": input_str_1}


"""
Now with two different inputs we can run them by setting them to list and and giving to function.
If you want to run a single input it still needs to be but in a list
"""

# Setting inputs to list
inputs_list = list([configuration_simple, configuration_external_files_1])

# Script needs the location of you libradtran binary
print("\nRemember to specify libradtran binary location!!!")
libradtran_bin_file_loc = "libRadtran-2.0.5/bin"

# Run libradtran with multiple inputs and other files
results_list = libis.run_conf_files_libradtran(libradtran_bin_file_loc, inputs_list)



# In[]:
# ########################################################################
# Example 3 .ini files and PMOM
# ########################################################################

"""
This example will give an error as a result because values given to libradtran are not valid. 
This examples purpose is to demostrate use of .ini files as source of inputs.
Also use of multiple external files is demonstrated as well  as some parser that the library provides.

"""

# For this example the you need to specify the libradtran data files path
libradtran_bin_file_loc = "libRadtran-2.0.5/bin"

# Phase function Example
phangle = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180])
phase_function = np.array([51.9,  9.0, 6.8, 4.9, 3.0, 1.6, 1.3, 1.0, 0.9, 0.9, 0.7, 0.4, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])

# Creating a profile file for PMOM
input_file = libis.profile_parser(phangle, phase_function)

# Number of moments for PMOM
moments = 1024

# Run PMOM
phase_moments = libis.run_pmom(libradtran_bin_file_loc, input_file, moments)

# Parsing phase moments to stirng
moments_str = libis.array_to_string_parser(phase_moments)

# Lets create a aerosol profile
heigth = np.array([7, 6, 5, 4, 3, 2, 1, 0])
value = np.array([0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2])

# Library contains a Profile parser
aerosol_profile = libis.profile_parser(heigth, value)

# Main input file in a python string format
input_str_2 = f"data_files_path {libradtran_data_files_path}\n\
    wavelength 450 \n\
    atmosphere_file US-standard\n\
    aerosol_default\n\
    aerosol_modify tau set 0.1\n\
    rte_solver disort\n\
    verbose"

# Create a configparser
general_config = configparser.ConfigParser()
general_config["parser_options"] = {
    "output_format": 0,
    "umu_length": 0,
    }
general_config["main_str"] = {
    "input_str": input_str_2,
    }
general_config["temp_strs"] = {
    "aerosol_file moments": moments_str,
    "aerosol_file tau": aerosol_profile
    }

# Saving run configuration
with open("example_libradtran_run.ini", "w") as f:
    general_config.write(f)

# Selecting .ini files
input_files_list = glob.glob("*.ini")

# Run libradtran with multiple inputs and other files
results_from_ini_files_list = libis.run_conf_files_libradtran(libradtran_bin_file_loc, input_files_list)

