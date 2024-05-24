#!/usr/bin/python3
"""
Parses the CMIP6Plus_CV.json and constructs an esg.cmip6plus.ini with sufficient content for use by esgdrs.
(Does not contain additional directives needed by the legacy esgpublish itself.)
"""

import requests
import json

url = "https://raw.githubusercontent.com/WCRP-CMIP/CMIP6Plus_CVs/main/CVs/CMIP6Plus_CV.json"

cv = json.loads(requests.get(url).content.decode())["CV"]

def opts_line(facet):
    vals = cv[facet]
    if isinstance(vals, str):
        opts = vals
    else:
        # loops over list items or dict keys
        opts = ', '.join(item for item in sorted(vals)
                         if not item.startswith("."))
    return f'{facet}_options = {opts}'

content=f"""[project:cmip6plus]

categories = 
    mip_era            | enum   | true  | true  | 0 
    activity_id        | enum   | true  | true  | 1 
    institution_id     | enum   | true  | true  | 2 
    source_id          | enum   | true  | true  | 3 
    experiment_id      | enum   | true  | true  | 4 
    member_id          | string | true  | true  | 5 
    table_id           | enum   | true  | true  | 6 
    variable_id        | string | true  | true  | 7 
    grid_label         | enum   | true  | true  | 8 

filename_format = %(variable_id)s_%(table_id)s_%(source_id)s_%(experiment_id)s_%(member_id)s_%(grid_label)s[_%(period_start)s-%(period_end)s].nc

directory_format = %(root)s/%(mip_era)s/%(activity_id)s/%(institution_id)s/%(source_id)s/%(experiment_id)s/%(member_id)s/%(table_id)s/%(variable_id)s/%(grid_label)s/%(version)s

dataset_id = %(mip_era)s.%(activity_id)s.%(institution_id)s.%(source_id)s.%(experiment_id)s.%(member_id)s.%(table_id)s.%(variable_id)s.%(grid_label)s

{opts_line("mip_era")}

{opts_line("activity_id")}

{opts_line("institution_id")}

{opts_line("source_id")}

{opts_line("experiment_id")}

member_id_pattern = [%(sub_experiment_id)s-]%(variant_label)s

{opts_line("table_id")}

variable_id_pattern = %(string)s

{opts_line("grid_label")}

{opts_line("sub_experiment_id")}

variant_label_pattern = r%(digit)si%(digit)sp%(digit)sf%(digit)s

version_pattern = v%(digit)s
"""


with open('esg.cmip6plus.ini', 'w') as fout:
    fout.write(content)
