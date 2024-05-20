#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# In[]:
# ########################################################################
# Libradtran disort Python Runner
# ########################################################################
"""
Created on Wed Jul 26 11:18:11 2023
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
# Function descritions
# ########################################################################

"""
################## General information ##################
This script provides two main ways to run libradtran and some other helper functions to work with it for example pmom.

Two main functions to run libradtran are run_libradtran and run_conf_files_libradtran.
For other functions there are run_pmom, profile_parser and array_to_string_parser.

################## Design and use philosophy ##################
The main design philosophy of this code is to provide a lightweight python interface with libradtran that can support full use 
of libradtrans disort solver through python. Because of this goal the program will need to know some settings which are
provided in the form of a output_format in either a init file or configure parser object.


################## Functions ##################

##### run_libradtran #####
run_libradtran script takes tree variables as libradtran_bin_file_loc, params and conf.

params is a string representing the standard libradtran outputfile.

conf tels the output parser what kind of format it needs to parse and it needs umu_length and output_format.

umu_length is the amount of viewing zenith angles

output_format tells the script the shape of output string so that parsing scripts 
can parse it correctly. Shapes are described in libRadtran User's Guide in section 
3.1.5. 
output_format = 0 corresponds to string shape were no umu or phi is specified. 
output_format = 1 corresponds to string shape were umu is specified but phi is not.
output_format = 2 corresponds to string shape were umu and phi are specified. 

libradtran_bin_file_loc is the location of users libradtran binary.


##### run_conf_files_libradtran #####
run_conf_files_libradtran takes in tree variables: libradtran_bin_file_loc, conf_file_list, verbose=True

libradtran_bin_file_loc is the location of libradtran binary.

conf_file_list is a list of either configparser objects or a list of locations of configparser .ini files.

configparser object and .ini files needs to be setup in following way:

There needs to be a parser_options and main_str key.

parser_options key needs to contain umu_length and output_format

umu_length is the amount of viewing zenith angles

output_format tells the script the shape of output string so that parsing scripts 
can parse it correctly. Shapes are described in libRadtran User's Guide in section 
3.1.5. 
output_format = 0 corresponds to string shape were no umu or phi is specified. 
output_format = 1 corresponds to string shape were umu is specified but phi is not.
output_format = 2 corresponds to string shape were umu and phi are specified. 

main_str key will contain the main input file for libradtran.

External files can also be added to main program by usesing key: temp_strs and so that
it contains the name of the variable in libradtran input file and then the file contents in string.


##### run_pmom #####
Can be used to run pmom in python.

Inputs needed for pmom are: libradtran_bin_file_loc, profile_string, moments

libradtran_bin_file_loc is the location of pmom binary.

profile_string is the profile string that must be provided as 2-column file, containing
the scattering angle grid in the first column and the phase function value in the second column.
String parser is porvided also in this library and it is called profile_parser.

moments is the number of moments used in pmom


##### profile_parser #####
Can be used to parse profiles, ergo libradtran files that contain two columns of data.


##### array_to_string_parser #####
This function takes in a numpy array of values user wants to incorporate to their libradtran
program and gives a string that can be used in the main input string.


################## NOTE ##################
In run_libradtran_example.py al the functions are used and explained.


################## Known issues ##################

##### zout SUR TOA #####
If zout is set in following way: zout SUR TOA
The code will only output solution to other one of these.
To avoid this problem, you can run two separate runs with single zout option.


"""
# In[]:
# ########################################################################
# Pakages
# ########################################################################

import tempfile

import numpy as np
import subprocess as sp

from io import StringIO
from configparser import ConfigParser

# In[]:
# ########################################################################
# run_libRadtran Related Functions
# ########################################################################

def output_format_1_parser(vals):
    outdata_basic = np.genfromtxt(StringIO(vals))
    umu = None
    phi = None
    u0u = None
    uu = None
    return outdata_basic, umu, phi, u0u, uu


def output_format_2_parser(vals):
    outdata_basic = np.genfromtxt(StringIO(vals[0]))
    for i, val in enumerate(vals[1:]):
        if not val:
            continue
        row = np.expand_dims(np.genfromtxt(StringIO(val)), axis=0)
        if i == 0:
            umu = row[0, 0]
            u0u = row[0, 1]
        else:
            umu = np.append(umu, row[0, 0])
            u0u = np.append(u0u, row[0, 1])
    uu = None
    phi = None
    return outdata_basic, umu, phi, u0u, uu


def output_format_3_parser(vals):
    outdata_basic = np.genfromtxt(StringIO(vals[0]))
    phi  = np.genfromtxt(StringIO(vals[1]))
    for i, val in enumerate(vals[2:]):
        if not val:
            continue
        row = np.expand_dims(np.genfromtxt(StringIO(val)), axis=0)
        if i == 0:
            umu = row[0, 0]
            u0u = row[0, 1]
            uu = np.expand_dims(row[0, 2:], axis=1)
        else:
            umu = np.append(umu, row[0, 0])
            u0u = np.append(u0u, row[0, 1])
            uu = np.append(uu, np.expand_dims(row[0, 2:], axis=1), axis=1)
    return outdata_basic, umu, phi, u0u, uu


# In[]:
# ########################################################################
# Main run_libRadtran Function
# ########################################################################

def run_libradtran(libradtran_bin_file_loc, params, conf):
    pros = sp.Popen(f"{libradtran_bin_file_loc}/uvspec", shell=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    vals, error = pros.communicate(input=str.encode(params))
    vals = vals.decode()
    error = error.decode()
    if pros.returncode != 0:
        return error
        #raise OSError(error)
    else:
        output = list()
        vals = vals.split("\n")        
        if int(conf["output_format"]) == 0:
            loop_row_count = float(len(vals) - 1)
        elif int(conf["output_format"]) == 1:
            loop_row_count = (len(vals) - 1)/(1 + int(conf["umu_length"]))
        elif int(conf["output_format"]) == 2:
            loop_row_count = (len(vals) - 1)/(2 + int(conf["umu_length"]))
        if not loop_row_count.is_integer():
            print("Something went wrong with row counting")
            print(loop_row_count)
        for ind in range(int(loop_row_count)):
            if int(conf["output_format"]) == 0:
                rows = vals[ind]
                outdata_basic, umu, phi, u0u, uu = output_format_1_parser(rows)
            elif int(conf["output_format"]) == 1:
                rows = vals[int(ind*(1 + int(conf["umu_length"]))): int((ind+1)*(1 + int(conf["umu_length"])))]                
                outdata_basic, umu, phi, u0u, uu = output_format_2_parser(rows)
            elif int(conf["output_format"]) == 2:
                rows = vals[int(ind*(2 + int(conf["umu_length"]))): int((ind+1)*(2 + int(conf["umu_length"])))]
                outdata_basic, umu, phi, u0u, uu = output_format_3_parser(rows)
            output_dict = {
                "lambda": outdata_basic[0], 
                "edir": outdata_basic[1],
                "edn": outdata_basic[2],
                "eup": outdata_basic[3],
                "uavgdir": outdata_basic[4],
                "uavgdn": outdata_basic[5],
                "uavup": outdata_basic[6],
                "umu": umu,
                "phi": phi,
                "u0u(umu)": u0u,
                "uu(umu,phi)": uu,
                "error/verbose message": error
                }
            output.append(output_dict)
        return output


# In[]:
# ########################################################################
# run_conf_files_libradtran Related Functions
# ########################################################################

def add_to_main_input_str(main_str, temp_file_var_name, temp_file_name):
    word = "disort"
    start_index = main_str.find(word)
    end_index = start_index + len(word)
    temp_str_to_add = f"\n{temp_file_var_name} {temp_file_name}" 
    main_str_modified = main_str[:end_index] + temp_str_to_add + main_str[end_index:]
    return main_str_modified


# In[]:
# ########################################################################
# Main Run libRadtran With Configurrations Function
# ########################################################################

def run_conf_files_libradtran(libradtran_bin_file_loc, conf_file_list, verbose=True):
    conf_results = list()
    for conf_file in conf_file_list:
        #print("Running with UVSPEC file:", conf_file.split("/")[-1])
        if isinstance(conf_file, str) and conf_file.endswith('.ini'):
            configuration = ConfigParser()
            configuration.read(conf_file)
        else:
            configuration = conf_file
        parser_conf = configuration["parser_options"]
        main_input_str = configuration["main_str"]["input_str"]
        temp_exist = False
        for key in configuration:
            if key == "temp_strs":
                temp_exist = True
        if temp_exist:
            temp_files = configuration["temp_strs"]
            with tempfile.TemporaryDirectory() as tmpdir:
                for key in temp_files:
                    temp = tempfile.NamedTemporaryFile(dir=tmpdir, delete=False)
                    temp.write(temp_files[key].encode())
                    temp.seek(0)
                    main_input_str = add_to_main_input_str(main_input_str, key, temp.name)
                results = run_libradtran(libradtran_bin_file_loc, main_input_str, parser_conf)
        else:
            results = run_libradtran(libradtran_bin_file_loc, main_input_str, parser_conf)
        conf_results.append(results)
    return conf_results


# In[]:
# ########################################################################
# PMOM To Create PMOM Files to Input Files
# ########################################################################

def run_pmom(libradtran_bin_file_loc, profile_string, moments):
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(profile_string.encode())
        proc = sp.Popen([f"{libradtran_bin_file_loc}/pmom", "-l", f"{moments}", "-r", "3", str.encode(tmp.name)], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        vals, error = proc.communicate()
    vals = np.genfromtxt(StringIO(vals.decode()))
    error = error.decode()
    if proc.returncode != 0:
        raise OSError(error)
    else:
        return vals
    

# In[]:
# ########################################################################
# Other functions To Create Input Files To libratran
# ########################################################################

def profile_parser(col1, col2):
    for ind, (hei, val) in enumerate(zip(col1, col2)):
        if ind == 0:
            ar_str = f"{hei} {val}\n"
        else:
            val_str = f"{hei} {val}\n"
            ar_str = f"{ar_str}{val_str}" 
    return ar_str


def array_to_string_parser(ar):
    if ar.size == 1:
        ar_str = str(ar)
    else:
        for ind, val in enumerate(ar):
            if ind == 0:
                ar_str = str(val)
            else:
                ar_str = f"{ar_str} {val}" 
    return ar_str
