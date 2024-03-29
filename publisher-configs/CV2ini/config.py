#!/usr/bin/env python
# -*- coding: utf-8 -*-


# The following three format element drive the INI attributes
FILENAME_FORMAT = '%(variable_id)s_%(table_id)s_%(source_id)s_%(experiment_id)s_%(member_id)s_%(grid_label)s[_%(period_start)s-%(period_end)s].nc'
DIRECTORY_FORMAT = '%(root)s/%(mip_era)s/%(activity_drs)s/%(institution_id)s/%(source_id)s/%(experiment_id)s/%(member_id)s/%(table_id)s/%(variable_id)s/%(grid_label)s/%(version)s'
DATASET_ID = '%(mip_era)s.%(activity_drs)s.%(institution_id)s.%(source_id)s.%(experiment_id)s.%(member_id)s.%(table_id)s.%(variable_id)s.%(grid_label)s'

# Optional dataset name format
DATASET_FORMAT = 'mip_era=%(mip_era)s, source_id=%(source_id)s, experiment=%(experiment_title)s, member_id=%(member_id)s, variable=%(variable_id)s, version=%(version)s'  # SKA - this hasn't been working, perhaps done for cmip5 custom?

# netCDF global attributes to extract in addition of DRS facets
EXTRACT_GLOBAL_NC = ['frequency',
                     'realm',
                     'product',
                     'nominal_resolution',
                     'source_type',
                     'grid',
                     'creation_date',
                     'variant_label',
                     'sub_experiment_id',
                     'further_info_url',
                     'activity_id',
                     'data_specs_version']

# netCDF variable to exclude from THREDDS
THREDDS_EXCLUDE_VARIABLES = ['a', 'a_bnds', 'alev1', 'alevel', 'alevhalf', 'alt40', 'b', 'b_bnds', 'bnds',
                             'bounds_lat', 'bounds_lon', 'dbze', 'depth', 'depth0m', 'depth100m', 'depth_bnds',
                             'geo_region', 'height', 'height10m', 'height2m', 'lat', 'lat_bnds', 'latitude',
                             'latitude_bnds', 'layer', 'lev', 'lev_bnds', 'location', 'lon', 'lon_bnds', 'longitude',
                             'longitude_bnds', 'olayer100m', 'olevel', 'oline', 'p0', 'p220', 'p500', 'p560', 'p700',
                             'p840', 'plev', 'plev3', 'plev7', 'plev8', 'plev_bnds', 'plevs', 'pressure1', 'region',
                             'rho', 'scatratio', 'sdepth', 'sdepth1', 'sza5', 'time', 'time1',
                             'time2', 'time_bnds', 'vegtype', 'i', 'j', 'rlat', 'rlat_bnds', 'sector', 'type',
                             'vertices_latitude', 'vertices_longitude']

# netCDF global attribute delimiter
ATTRIBUTE_DELIMITERS = {'realm': 'space', 'activity_id': 'space', 'source_type': 'space', 'model_cohort': 'space'}  # use the facet name

# Handler
HANDLER = 'esgcet.config.cmip6_handler:CMIP6Handler'

# MIP Era value
MIP_ERA = 'CMIP6'

# Oldest CMOR version allowed
MIN_CMOR_VERSION = '3.2.4'

# Oldest Data Specs version allowed

MIN_DS_VERSION = '01.00.13'

# Oldest CF version allowed
MIN_CF_VERSION = '1.6'

# CIM docs creation boolean
CREATE_CIM = 'true'

# LAS configuration boolean
LAS_CONFIGURE = 'false'

#variables for variable_locate (will append _)
LOCATE_VARS = ['ps', 'tau']

