# loads configuration files, converts their values to appropriate data types, and obtains the processed data in different representations


### pip install configparser2dtypes


The load_config_file_vars function is useful when you need to load a configuration file, 
convert its values to appropriate data types, and obtain the processed data in different 
representations. It simplifies the process of handling configuration files and allows 
you to access the data in the desired format for further analysis or usage 
within your application.



```python
Function: load_config_file_vars(cfgfile:str, onezeroasboolean:bool, force_dtypes:dict|None=None) -> Tuple[Dict, List, Dict]

This function is designed to load and process a configuration file, extracting the values and converting them to appropriate data types. It takes the following parameters:

cfgfile (str): The path or filename of the configuration file to be loaded.
onezeroasboolean (bool): A flag indicating whether to treat the values '0' and '1' as boolean values.
force_dtypes (dict|None): A dictionary that maps specific keys to desired data types for force-conversion.
Returns:

A tuple containing three outputs:
cfgdictcopy (Dict): The configuration file values stored in a nested dictionary structure, where each section and key is a nested dictionary key.
cfgdictcopyaslist (List): A modified list representation of the configuration file values, where each item is a tuple consisting of the section, key, and value.
cfgdictcopysorted (Dict): A grouped dictionary where the values are grouped based on the first item encountered in the cfgdictcopyaslist output.
```

## Usage:



```python
# Import the necessary modules and functions:
from configparser import ConfigParser
from pprint import pprint as pp
from load_config import load_config_file_vars
# Specify the path or filename of the configuration file to be loaded:
cfgfile = "path/to/config.ini"


# Example - content 
r"""
[proc1]
path_or_pid_or_dict={"path": r"some_installer.exe","path_re": "some_installer.exe",}
path2search=C:\
savepath=e:\check2
sleeptime_psutil=1
check_files=False
check_reg=False
regexcheck=^some_installer\.exe
attrbs_of_files_2_check=("aa_path","aa_name","aa_size_on_disk","aa_created","aa_last_written","aa_last_accessed",)
suspend_hotkeys=ctrl+alt+x
folder_for_modified_files=None
copybuffer=1024000

[proc2]
path_or_pid_or_dict={"path": r"HD-Player.exe", "path_re": "HD-Player.exe"}
path2search=C:\ProgramData\BlueStacks_nxt
savepath=e:\check1
sleeptime_psutil=1
check_files=True
check_reg=False
regexcheck=check\d+
attrbs_of_files_2_check=("aa_path","aa_name","aa_size_on_disk","aa_created","aa_last_written","aa_last_accessed",)
suspend_hotkeys=ctrl+alt+q
folder_for_modified_files=None
copybuffer=1024000
"""


# Call the load_config_file_vars function to load and process the configuration file:

from  configparser2dtypes import load_config_file_vars

import re
(
    cfg_dict,
    cfg_dict_as_list,
    cfg_dict_sorted,
) = load_config_file_vars(
    cfgfile=r"path/to/config.ini",
    onezeroasboolean=False,
    force_dtypes={"regexcheck": re.compile},
)

from pprint import pprint as pp

print('\n----------cfg_dict----------\n')
pp(cfg_dict)
print('\n----------cfg_dict_as_list----------\n')

pp(cfg_dict_as_list)
print('\n----------cfg_dict_sorted----------\n')

pp(cfg_dict_sorted)

----------cfg_dict----------
{'proc1': {'attrbs_of_files_2_check': ('aa_path',
                                       'aa_name',
                                       'aa_size_on_disk',
                                       'aa_created',
                                       'aa_last_written',
                                       'aa_last_accessed'),
           'check_files': False,
           'check_reg': False,
           'copybuffer': 1024000,
           'folder_for_modified_files': None,
           'path2search': 'C:\\',
           'path_or_pid_or_dict': {'path': 'some_installer.exe',
                                   'path_re': 'some_installer.exe'},
           'regexcheck': re.compile('^some_installer\\.exe'),
           'savepath': 'e:\\check2',
           'sleeptime_psutil': 1,
           'suspend_hotkeys': 'ctrl+alt+x'},
 'proc2': {'attrbs_of_files_2_check': ('aa_path',
                                       'aa_name',
                                       'aa_size_on_disk',
                                       'aa_created',
                                       'aa_last_written',
                                       'aa_last_accessed'),
           'check_files': True,
           'check_reg': False,
           'copybuffer': 1024000,
           'folder_for_modified_files': None,
           'path2search': 'C:\\ProgramData\\BlueStacks_nxt',
           'path_or_pid_or_dict': {'path': 'HD-Player.exe',
                                   'path_re': 'HD-Player.exe'},
           'regexcheck': re.compile('check\\d+'),
           'savepath': 'e:\\check1',
           'sleeptime_psutil': 1,
           'suspend_hotkeys': 'ctrl+alt+q'}}
		   


		   
----------cfg_dict_as_list----------
[({'path': 'some_installer.exe', 'path_re': 'some_installer.exe'},
  ('proc1', 'path_or_pid_or_dict')),
 ('C:\\', ('proc1', 'path2search')),
 ('e:\\check2', ('proc1', 'savepath')),
 (1, ('proc1', 'sleeptime_psutil')),
 (False, ('proc1', 'check_files')),
 (False, ('proc1', 'check_reg')),
 (re.compile('^some_installer\\.exe'), ('proc1', 'regexcheck')),
 (('aa_path',
   'aa_name',
   'aa_size_on_disk',
   'aa_created',
   'aa_last_written',
   'aa_last_accessed'),
  ('proc1', 'attrbs_of_files_2_check')),
 ('ctrl+alt+x', ('proc1', 'suspend_hotkeys')),
 (None, ('proc1', 'folder_for_modified_files')),
 (1024000, ('proc1', 'copybuffer')),
 ({'path': 'HD-Player.exe', 'path_re': 'HD-Player.exe'},
  ('proc2', 'path_or_pid_or_dict')),
 ('C:\\ProgramData\\BlueStacks_nxt', ('proc2', 'path2search')),
 ('e:\\check1', ('proc2', 'savepath')),
 (1, ('proc2', 'sleeptime_psutil')),
 (True, ('proc2', 'check_files')),
 (False, ('proc2', 'check_reg')),
 (re.compile('check\\d+'), ('proc2', 'regexcheck')),
 (('aa_path',
   'aa_name',
   'aa_size_on_disk',
   'aa_created',
   'aa_last_written',
   'aa_last_accessed'),
  ('proc2', 'attrbs_of_files_2_check')),
 ('ctrl+alt+q', ('proc2', 'suspend_hotkeys')),
 (None, ('proc2', 'folder_for_modified_files')),
 (1024000, ('proc2', 'copybuffer'))]
----------cfg_dict_sorted----------
{'proc1': [('proc1',
            ({'path': 'some_installer.exe', 'path_re': 'some_installer.exe'},
             ('proc1', 'path_or_pid_or_dict'))),
           ('proc1', ('C:\\', ('proc1', 'path2search'))),
           ('proc1', ('e:\\check2', ('proc1', 'savepath'))),
           ('proc1', (1, ('proc1', 'sleeptime_psutil'))),
           ('proc1', (False, ('proc1', 'check_files'))),
           ('proc1', (False, ('proc1', 'check_reg'))),
           ('proc1',
            (re.compile('^some_installer\\.exe'), ('proc1', 'regexcheck'))),
           ('proc1',
            (('aa_path',
              'aa_name',
              'aa_size_on_disk',
              'aa_created',
              'aa_last_written',
              'aa_last_accessed'),
             ('proc1', 'attrbs_of_files_2_check'))),
           ('proc1', ('ctrl+alt+x', ('proc1', 'suspend_hotkeys'))),
           ('proc1', (None, ('proc1', 'folder_for_modified_files'))),
           ('proc1', (1024000, ('proc1', 'copybuffer')))],
 'proc2': [('proc2',
            ({'path': 'HD-Player.exe', 'path_re': 'HD-Player.exe'},
             ('proc2', 'path_or_pid_or_dict'))),
           ('proc2',
            ('C:\\ProgramData\\BlueStacks_nxt', ('proc2', 'path2search'))),
           ('proc2', ('e:\\check1', ('proc2', 'savepath'))),
           ('proc2', (1, ('proc2', 'sleeptime_psutil'))),
           ('proc2', (True, ('proc2', 'check_files'))),
           ('proc2', (False, ('proc2', 'check_reg'))),
           ('proc2', (re.compile('check\\d+'), ('proc2', 'regexcheck'))),
           ('proc2',
            (('aa_path',
              'aa_name',
              'aa_size_on_disk',
              'aa_created',
              'aa_last_written',
              'aa_last_accessed'),
             ('proc2', 'attrbs_of_files_2_check'))),
           ('proc2', ('ctrl+alt+q', ('proc2', 'suspend_hotkeys'))),
           ('proc2', (None, ('proc2', 'folder_for_modified_files'))),
           ('proc2', (1024000, ('proc2', 'copybuffer')))]}



```