import argparse
import os
import re
from distutils.util import strtobool

import requests
from requests.auth import HTTPBasicAuth

from ESGConfigParser import SectionParser, build_line, lengths
from config import *
from constants import *
from git_exceptions import *


def get_args():
    parser = argparse.ArgumentParser(
        prog='json2ini',
        description=PROGRAM_DESC,
        add_help=False,
        epilog=EPILOG)
    parser._optionals.title = OPTIONAL
    parser._positionals.title = POSITIONAL
    parser.add_argument(
        '-h', '--help',
        action='help',
        help=HELP)
    parser.add_argument(
        '--project',
        metavar='PROJECT_ID',
        type=str,
        required=True,
        help=PROJECT_HELP)
    parser.add_argument(
        '--outdir',
        metavar='CWD',
        type=str,
        default=os.path.join(os.getcwd()),
        help=OUTDIR_HELP)
    parser.add_argument(
        '--gh-user',
        metavar='USERNAME',
        type=str,
        help=GITHUB_USER_HELP)
    parser.add_argument(
        '--gh-password',
        metavar='PASSWORD',
        type=str,
        help=GITHUB_PASSWORD_HELP)
    parser.add_argument(
        '--devel',
        action='store_true',
        default=False,
        help=DEVEL_HELP)
    return parser.parse_args()


def gh_request_content(url, auth=None, devel=False):
    """
    Gets the GitHub content of a file or a directory.

    :param str url: The GitHub url to request
    :param *requests.auth.HTTPBasicAuth* auth: The authenticator object
    :param boolean devel: True to request the devel branch
    :returns: The GitHub request content
    :rtype: *requests.models.Response*
    :raises Error: If user not authorized to read GitHub repository
    :raises Error: If user exceed the GitHub API rate limit
    :raises Error: If the queried content does not exist
    :raises Error: If the GitHub request fails for other reasons

    """
    if devel:
        url += '?ref=devel'
    GitHubException.URI = url
    r = requests.get(url, auth=auth)
    if r.status_code == 200:
        return r
    elif r.status_code == 401:
        raise GitHubUnauthorized()
    elif r.status_code == 403:
        raise GitHubAPIRateLimit()
    elif r.status_code == 404:
        raise GitHubFileNotFound()
    else:
        raise GitHubConnectionError()


def get_json_content(facet, auth=None, devel=False):
    try:
        WCRP_facet = FACET_MAP[facet]
    except KeyError:
        WCRP_facet = facet
    url = GITHUB_CV_API.format(JSON_FILE.format(WCRP_facet))
    r = gh_request_content(url=url, auth=auth, devel=devel)
    return requests.get(r.json()['download_url'], auth=auth).json()[WCRP_facet]


def authenticate(self):
    """
    Build GitHub HTTP authenticator

    :returns: The HTTP authenticator
    :rtype: *requests.auth.HTTPBasicAuth*

    """
    return HTTPBasicAuth(self.gh_user, self.gh_password) if self.gh_user and self.gh_password else None


def find_facets(facets, format):
    for i, v in enumerate(re.findall(re.compile(r'%\(([^()]*)\)s'), format)):
        try:
            if v not in IGNORED_FACETS and v not in zip(*facets)[1]:
                facets.append((i - 1, v))
        except IndexError:
            facets.append((i - 1, v))
    return facets


def get_facets(filename_vars=True, directory_vars=True, dataset_vars=True, dataset_name_vars=False):
    facets = []
    if directory_vars:
        facets = find_facets(facets, DIRECTORY_FORMAT)
    if dataset_vars:
        facets = find_facets(facets, DATASET_ID)
    if filename_vars:
        facets = find_facets(facets, FILENAME_FORMAT)
    if dataset_name_vars:
        facets = find_facets(facets, DATASET_FORMAT)
    return facets


def get_categories(facets):
    categories = []
    i = 0
    for i, facet in facets:
        facet_type = 'enum'
        if facet in ['variable', 'version', 'ensemble', 'institute']:
            facet_type = 'string'
        categories.append((facet, facet_type, 'true', 'true', str(i)))
    for facet in EXTRACT_GLOBAL_NC:
        categories.append((facet, 'string', 'false', 'true', str(i)))
        i += 1
    categories.append(('description', 'text', 'false', 'false', '99'))
    categories = tuple([build_line(category, length=lengths(categories), indent=True) for category in categories])
    return build_line(categories, sep='\n')


def declare_map(config, facet):
    maps = []
    if config.has_option('maps'):
        maps = map(str.strip, config.get('maps').split(','))
    maps.append('{}_map'.format(facet))
    config.set('maps', build_line(tuple(maps), sep=', '))


if __name__ == "__main__":
    args = get_args()
    auth = HTTPBasicAuth(args.gh_user, args.gh_password) if args.gh_user and args.gh_password else None
    config = SectionParser(section='project:{}'.format(args.project))
    # Get all facet keys from format elements
    facets = get_facets()
    config.set('categories', get_categories(facets), newline=True)
    config.set('category_defaults', build_line(('project', 'CMIP6'), indent=True), newline=True)
    config.set('filename_format', FILENAME_FORMAT)
    config.set('directory_format', DIRECTORY_FORMAT)
    config.set('dataset_id', DATASET_ID)
    config.set('dataset_name_format', DATASET_FORMAT)
    categories = config.get_options_from_table('categories')
    rank = 1
    while rank in map(int, zip(*categories)[4]):
        facet, facet_type, mandatory, _, _ = categories[rank]
        if strtobool(mandatory):
            if facet_type == 'enum':
                content = get_json_content(facet, auth=auth, devel=args.devel)
                if facet == 'model':
                    values = content.keys()
                    config.set('{}_options'.format(facet), build_line(tuple(sorted(values)), sep=', '))
                elif facet == 'experiment':
                    values = []
                    length = lengths([(args.project.lower(), k) for k in content.keys()])
                    for k in content.keys():
                        values.append('    {} | {} | {}'.format(format(args.project, str(length[0])),
                                                                format(k, str(length[1])),
                                                                content[k]['description']))
                    config.set('{}_options'.format(facet), build_line(tuple(values), sep='\n'), newline=True)
                else:
                    values = content
                    config.set('{}_options'.format(facet), build_line(tuple(sorted(values)), sep=', '))
            else:
                try:
                    config.set('{}_pattern'.format(facet), FACET_PATTERNS[facet])
                except KeyError:
                    content = get_json_content(facet, auth=auth, devel=args.devel)
                    declare_map(config, facet)
                    if facet == 'institute':
                        header = 'map(model : {})'.format(facet)
                        institutes = []
                        for model in content.keys():
                            institutes.append((model, content[model]['institution_id'][0]))
                        institutes = tuple(
                            [build_line(institute, length=lengths(institutes), indent=True) for institute in
                             sorted(institutes)])
                        config.set('{}_map'.format(facet), build_line((header,) + institutes, sep='\n'))
        rank += 1
    # Add time_frequency options
    content = get_json_content('time_frequency', auth=auth, devel=args.devel)
    values = content.keys()
    config.set('{}_options'.format('time_frequency'), build_line(tuple(sorted(values)), sep=', '))
    # Add las_time_delta_map
    declare_map(config, 'las_time_delta')
    header = 'map(time_frequency : las_time_delta)'
    content = get_json_content('frequency', auth=auth, devel=args.devel)
    las_frequencies = []
    for frequency in content.keys():
        las_frequencies.append((frequency, LAS_FREQUENCIES[frequency]))
    las_frequencies = tuple(
        [build_line(frequency, length=lengths(las_frequencies), indent=True) for frequency in las_frequencies])
    config.set('las_time_delta_map', build_line((header,) + las_frequencies, sep='\n'))
    config.set('handler', HANDLER)
    config.set('min_cmor_version', MIN_CMOR_VERSION)
    config.set('min_cf_version', MIN_CF_VERSION)
    for att, delimiter in ATTRIBUTE_DELIMITERS.iteritems():
        config.set('{}_delimiter'.format(att), delimiter)
    config.set('cmor_table_path', CMOR_TABLE_PATH)
    config.set('CREATE_CIM', CREATE_CIM)
    config.set('las_configure', LAS_CONFIGURE)
    config.set('cmor_table_path', CMOR_TABLE_PATH)
    config.set('extract_global_attrs', build_line(tuple(EXTRACT_GLOBAL_NC), sep=', '))
    config.set('thredds_exclude_variables', build_line(tuple(THREDDS_EXCLUDE_VARIABLES), sep=', '))
    config.set('variable_locate', build_line(('ps', 'ps_'), sep=', '))
    config.set('variable_per_file', 'true')
    config.set('version_by_date', 'true')

    # Write final configuration
    with open('{}/esg.{}.ini'.format(args.outdir, args.project), 'w') as config_file:
        config.write(config_file)

    # Upgrade esgcet_models_table.txt
    url = GITHUB_TABLE_API.format('esgcet_models_table.txt')
    r = gh_request_content(url=url, auth=auth, devel=args.devel)
    content = requests.get(r.json()['download_url'], auth=auth).text.split('\n')
    help = content[0:11]
    fields = []
    for line in content:
        if not line.startswith('#'):
            fields.append(tuple([field.strip() for field in line.split('|')]))
    institute_description = get_json_content('institution_id', auth=auth, devel=args.devel)
    content = get_json_content('source_id', auth=auth, devel=args.devel)
    for model in content.keys():
        fields.append((args.project, model, '', '{}, {}'.format(content[model]['institution_id'][0],
                                                                institute_description[
                                                                    content[model]['institution_id'][0]])))
    fields.sort()
    lines = []
    for field in fields:
        lines.append(build_line(field, indent=False))
    with open('{}/esgcet_models_table.txt'.format(args.outdir), 'w') as table_file:
        table_file.write('\n'.join(help))
        table_file.write('\n'.join(lines))