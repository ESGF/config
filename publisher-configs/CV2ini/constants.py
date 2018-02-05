#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GitHub configuration
GITHUB_CV_API = 'https://api.github.com/repos/WCRP-CMIP/CMIP6_CVs/contents/{}'
GITHUB_TABLE_API = 'https://api.github.com/repos/ESGF/config/contents/publisher-configs/{}'

# JSON CV file format
JSON_FILE = 'CMIP6_{}.json'

# Facets to ignore
IGNORED_FACETS = ['root', 'period_start', 'period_end']

# Facet mapping between INI and JSON attributes (if necessary)
FACET_MAP = {}

# Facet patterns
FACET_PATTERNS = {'variant_label': 'r%(digit)si%(digit)sp%(digit)sf%(digit)s',
                  'variable_id': '%(string)s',
                  'version': 'v%(digit)s'}

# LAS time frequencies
LAS_FREQUENCIES = {'1hr': '1 hour',
                   '1hrCM': '1 hour',
                   '1hrPt': '1 hour',
                   '3hr': '3 hours',
                   '3hrPt': '3 hours',
                   '6hr': '6 hours',
                   '6hrPt': '6 hours',
                   'day': '1 day',
                   'MonDay': 'Monthly(Day)',
                   'dec': '10 years',
                   'fx': 'fixed',
                   'mon': '1 month',
                   'monC': '1 month',
                   'monPt': '1 month',
                   'MonNight': 'Monthly(Nigh)',
                   'sem': 'seasonal mean',
                   'subhr': '1 minute',
                   'subhrPt': '1 minute',
                   'yr': '1 year',
                   'yrPt': '1 year'}

# Help
PROGRAM_DESC = \
    """
    This script assembles an INI file for the ESGF publisher provided WCRP JSON CV files and additional static content.
    The CV files are found in https://github.com/WCRP-CMIP/CMIP6_CVs.git
    Only CMIP6 CV is supported at the moment. 
    
    """

EPILOG = \
    """
    Developed by:\n
    Ames, S. (DOE/LLNL - ames4@llnl.gov)\n
    Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.fr)\n

    """

OPTIONAL = \
    """Optional arguments"""

POSITIONAL = \
    """Positional arguments"""

HELP = \
    """
    Show this help message and exit.

    """

PROJECT_HELP = \
    """
    Required lower-cased project name.
    
    """

OUTDIR_HELP = \
    """
    Output directory for generated INI file.

    """

GITHUB_USER_HELP = \
    """
    GitHub username.

    """

GITHUB_PASSWORD_HELP = \
    """
    GitHub password.

    """

DEVEL_HELP = \
    """
    Fetch from the devel branch.

    """
