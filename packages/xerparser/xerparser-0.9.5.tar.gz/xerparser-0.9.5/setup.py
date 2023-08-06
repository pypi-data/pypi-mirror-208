# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xerparser', 'xerparser.schemas', 'xerparser.scripts', 'xerparser.src']

package_data = \
{'': ['*']}

install_requires = \
['html-sanitizer>=1.9.3,<2.0.0']

entry_points = \
{'console_scripts': ['calc_rem_hours_test = scripts:rem_hours_per_day_test',
                     'parse_test = scripts:parse_test',
                     'test = scripts:test']}

setup_kwargs = {
    'name': 'xerparser',
    'version': '0.9.5',
    'description': 'Parse a P6 .xer file to a Python object.',
    'long_description': '# xerparser\n\nRead the contents of a P6 .xer file and convert it into a Python object.  \n\n*Disclaimers:  \nIt\'s helpfull if you are already familiar with the mapping and schemas used by P6 during the export process.\nRefer to the [Oracle Documentation]( https://docs.oracle.com/cd/F25600_01/English/Mapping_and_Schema/xer_import_export_data_map_project/index.htm) for more information regarding how data is mapped to the XER format.  \nTested on .xer files exported as versions 15.2 through 19.12.*  \n\n<br/>\n\n## Install\n\n**Windows**:\n\n```bash\npip install xerparser\n```\n\n**Linux/Mac**:\n\n```bash\npip3 install xerparser\n```\n\n<br/>  \n\n## Usage  \n\nImport the `Xer` class from `xerparser`  and pass the contents of a .xer file as an argument. Use the `Xer` class variable `CODEC` to set the proper encoding to decode the file.\n\n```python\nfrom xerparser import Xer\n\nfile = r"/path/to/file.xer"\nwith open(file, encoding=Xer.CODEC, errors="ignore") as f:\n    file_contents = f.read()\nxer = Xer(file_contents)\n```\n\nDo not pass the the .xer file directly as an argument to the `Xer` class. The file must be decoded and read into a string, which can then be passed as an argument. Or, pass the .xer file into the `Xer.reader` classmethod, which accepts:\n\n* str or pathlib.Path objects for files stored locally or on a server.\n* Binary files from requests, Flask, FastAPI, etc...\n\n```python\nfrom xerparser import Xer\n\nfile = r"/path/to/file.xer"\nxer = Xer.reader(file)\n```\n\n<br/>\n\n## Attributes\n\nThe tables stored in the .xer file are accessable as either Global, Project specific, Task specific, or Resource specific:\n\n### Global\n\n  ```python\n  xer.export_info           # export data\n  xer.activity_code_types   # dict of ACTVTYPE objects\n  xer.activity_code_values  # dict of ACTVCODE objects\n  xer.calendars             # dict of all CALENDAR objects\n  xer.financial_periods     # dict of FINDATES objects\n  xer.notebook_topics       # dict of MEMOTYPE objects\n  xer.projects              # dict of PROJECT objects\n  xer.project_code_types    # dict of PCATTYPE objects\n  xer.project_code_values   # dict of PCATVAL objects\n  xer.tasks                 # dict of all TASK objects\n  xer.relationships         # dict of all TASKPRED objects\n  xer.resources             # dict of RSRC objects\n  xer.udf_types             # dict of UDFTYPE objects\n  xer.wbs_nodes             # dict of all PROJWBS objects\n  ```  \n\n### Project Specific\n\n```python\n# Get first project\nproject = list(xer.projects.values())[0]\n\nproject.activity_codes        # list of project specific ACTVTYPE objects\nproject.calendars             # list of project specific CALENDAR objects\nproject.project_codes         # dict of PCATTYPE: PCATVAL objects\nproject.tasks                 # list of project specific TASK objects\nproject.relationships         # list of project specific TASKPRED objects\nproject.user_defined_fields   # dict of `UDFTYPE`: `UDF Value` pairs  \nproject.wbs_nodes             # list of project specific PROJWBS objects\n```\n\n### Task Specific\n\n```python\n# Get first task\ntask = project.tasks[0]\n\ntask.activity_codes       # dict of ACTVTYPE: ACTVCODE objects\ntask.memos                # list of TASKMEMO objects\ntask.periods              # list of TASKFIN objects\ntask.resources            # dict of TASKRSRC objects\ntask.user_defined_fields  # dict of `UDFTYPE`: `UDF Value` pairs \n```\n\n### Resource Specific\n\n```python\n# Get first task resource\nresource = list(task.resources.values())[0]\n\nresource.periods              # list of TRSRCFIN objects\nresource.user_defined_fields  # dict of `UDFTYPE`: `UDF Value` pairs \n```\n\n<br/>\n\n## Error Checking\n\nSometimes the xer file is corrupted during the export process. If this is the case, a `CorruptXerFile` Exception will be raised during initialization.  A list of the errors can be accessed from the `CorruptXerFile` Exception, or by using the `find_xer_errors` function.\n\n### Option 1 - `errors` attribute of `CorruptXerFile` exception  (preferred)\n```python\nfrom xerparser import Xer, CorruptXerFile\n\nfile = r"/path/to/file.xer"\ntry:\n    xer = Xer.reader(file)\nexcept CorruptXerFile as e:\n    for error in e.errors:\n        print(error)\n```  \n\n### Option 2 - `find_xer_errors` function\n```python\nfrom xerparser import parser, file_reader, find_xer_errors\n\nfile = r"/path/to/file.xer"\nxer_data = parser(file_reader(file))\nfile_errors = find_xer_errors(xer_data)\nfor error in file_errors:\n    print(error)\n```\n\n### Errors\n\n- Minimum required tables - an error is recorded if one of the following tables is missing:\n  - CALENDAR\n  - PROJECT\n  - PROJWBS\n  - TASK\n  - TASKPRED  \n- Required table pairs - an error is recorded if Table 1 is included but not Table 2:  \n  \n  | Table 1       | Table 2       | Notes    |\n  | :----------- |:-------------|----------|\n  | TASKFIN | FINDATES | *Financial Period Data for Task* |\n  | TRSRCFIN | FINDATES | *Financial Period Data for Task Resource* |\n  | TASKRSRC | RSRC | *Resource Data* |\n  | TASKMEMO | MEMOTYPE | *Notebook Data* |\n  | ACTVCODE | ACTVTYPE | *Activity Code Data* |\n  | TASKACTV | ACTVCODE | *Activity Code Data* |\n  | PCATVAL | PCATTYPE | *Project Code Data* |\n  | PROJPCAT | PCATVAL | *Project Code Data* |\n  | UDFVALUE | UDFTYPE | *User Defined Field Data* |\n\n- Non-existent calendars assigned to tasks.\n- Non-existent resources assigned to task resources.\n',
    'author': 'Jesse',
    'author_email': 'code@seqmanagement.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/jjCode01/xerparser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
