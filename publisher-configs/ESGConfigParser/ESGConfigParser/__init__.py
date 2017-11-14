#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. module:: ESGConfigParser
.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.fr>

"""

import os
import re
import string
from ConfigParser import ConfigParser, _Chainmap, DEFAULTSECT, MAX_INTERPOLATION_DEPTH

from custom_exceptions import *


class SectionParser(ConfigParser):
    """
    Custom ConfigParser class to parse ESGF .ini files from a source directory.
    Parse a configuration section (mandatory).

    """

    def __init__(self, section, directory=None):
        ConfigParser.__init__(self)
        self.reset()
        ConfigException.SECTION = section
        self.section = section
        if directory:
            self.file = None
            self.parse(directory)
        else:
            self.add_section(section)

    def set(self, option, value=None, newline=False, section=None):
        """
        Overwrite the original method to set an option value for the given section.
        The value can be written on a new line.

        """
        if self.section == DEFAULTSECT:
            sectdict = self._defaults
        else:
            try:
                sectdict = self._sections[self.section]
            except KeyError:
                raise NoConfigSection()
        if newline:
            value = '\n{}'.format(value)
        sectdict[self.optionxform(option)] = value

    def write(self, fp):
        """
        Overwrite the original method to write options value for the given section.
        An ending newline is added in any case.

        """
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            fp.write("\n")
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, str(value)))
                fp.write("\n")
        for section in self._sections:
            fp.write("[%s]\n" % section)
            fp.write("\n")
            for (key, value) in self._sections[section].items():
                if key == "__name__":
                    continue
                if (value is not None) or (self._optcre == self.OPTCRE):
                    key = " = ".join((key, str(value)))
                fp.write("%s\n" % key)
                fp.write("\n")

    def get(self, option, raw=True, variables=None, section=None):
        """
        Overwrite the original method to get an option value for the given section.

        """
        sectiondict = {}
        try:
            sectiondict = self._sections[self.section]
        except KeyError:
            if self.section != DEFAULTSECT:
                raise NoConfigSection()
        # Update with the entry specific variables
        vardict = {}
        if variables:
            for key, value in variables.items():
                vardict[self.optionxform(key)] = value
        d = _Chainmap(vardict, sectiondict, self._defaults)
        option = self.optionxform(option)
        try:
            value = d[option]
        except KeyError:
            raise NoConfigOption(option)
        if raw or value is None:
            return value
        else:
            return self._interpolate(self.section, option, value, d)

    def has_option(self, option, section=None):
        """
        Overwrite the original method to check for the existence of a given option in the given section.

        """
        if not self.section or self.section == DEFAULTSECT:
            option = self.optionxform(option)
            return option in self._defaults
        elif self.section not in self._sections:
            return False
        else:
            option = self.optionxform(option)
            return (option in self._sections[self.section]
                    or option in self._defaults)

    @staticmethod
    def reset():
        """
        Resets exception constants

        """
        ConfigException.FILE = None
        ConfigException.SECTION = None

    def parse(self, path):
        """
        Parses the configuration files.

        :param str path: The directory path of configuration files
        :returns: The configuration file
        :rtype: *CfgParser*
        :raises Error: If no configuration file exists
        :raises Error: If no configuration section exist
        :raises Error: If the configuration file parsing fails

        """
        # If the section is not "[project:.*]", only read esg.ini
        ConfigException.FILE = os.path.join(path, 'esg.ini')
        self.file = os.path.join(path, 'esg.ini')
        self.read(self.file)
        if re.match(r'project:.*', self.section) and self.section not in self.sections():
            project = self.section.split('project:')[1]
            ConfigException.FILE = os.path.join(path, 'esg.{}.ini'.format(project))
            self.file = os.path.join(path, 'esg.{}.ini'.format(project))
            if not os.path.isfile(self.file):
                raise NoConfigFile(self.file)
            self.read(self.file)
        if self.section not in self.sections():
            raise NoConfigSection()
        if not self:
            raise EmptyConfigFile()

    def read(self, filenames):
        """
        Read and parse a filename or a list of filenames, and records their paths.

        """
        if isinstance(filenames, str):
            filenames = [filenames]
        for filename in filenames:
            try:
                fp = open(filename)
            except IOError:
                continue
            self._read(fp, filename)
            fp.close()

    def sections(self, default=True):
        """
        Returns the list of section names with/without [DEFAULT]

        """
        if default:
            return self._sections.keys() + ['DEFAULT']
        else:
            return self._sections.keys()

    def options(self, defaults=True):
        """
        Returns the list of options names into the section with/without defaults.

        """
        opts = self._sections[self.section].copy()
        if defaults:
            opts.update(self._defaults)
        if '__name__' in opts:
            del opts['__name__']
        return opts.keys()

    def translate(self, option, filename_pattern=False):
        """
        Return a regular expression associated with a ``pattern_format`` option
        in the configuration file. This can be passed to the Python ``re`` methods.

        :returns: The corresponding ``re`` pattern

        """
        if option not in self.options():
            raise NoConfigOption(option)
        pattern = self.get(option, raw=True).strip()
        # Start translation
        pattern = pattern.replace('\.', '__ESCAPE_DOT__')
        pattern = pattern.replace('.', r'\.')
        pattern = pattern.replace('__ESCAPE_DOT__', r'\.')
        # Translate all patterns matching [.*] as optional pattern
        pattern = re.sub(re.compile(r'\[(.*)\]'), r'(\1)?', pattern)
        # Remove underscore from latest mandatory pattern to allow optional brackets
        pattern = re.sub(re.compile(r'%\(([^()]*)\)s\('), r'(?P<\1>[^-_]+)(', pattern)
        # Translate %(root)s variable if exists but not required. Can include the project name.
        if re.compile(r'%\((root)\)s').search(pattern):
            pattern = re.sub(re.compile(r'%\((root)\)s'), r'(?P<\1>[\w./-]+)', pattern)
        # Include specific facet patterns
        for facet, facet_regex in self.get_patterns().items():
            pattern = re.sub(re.compile(r'%\(({})\)s'.format(facet)), facet_regex.pattern, pattern)
        # Constraint on %(version)s number
        pattern = re.sub(re.compile(r'%\((version)\)s'), r'(?P<\1>v[\d]+|latest)', pattern)
        # Translate all patterns matching %(name)s
        pattern = re.sub(re.compile(r'%\(([^()]*)\)s'), r'(?P<\1>[\w.-]+)', pattern)
        if filename_pattern:
            return '{}/(?P<filename>[\w.-]+)$'.format(pattern)
        else:
            return '{}$'.format(pattern)

    def get_facets(self, option, ignored=None):
        """
        Returns the set of facets declared into "*_format" attributes in the configuration file.
        :param str option: The option to get facet names
        :param list ignored: The list of facets to ignored
        :returns: The collection of facets
        :rtype: *set*

        """
        facets = re.findall(re.compile(r'%\(([^()]*)\)s'), self.get(option, raw=True))
        if ignored:
            return [f for f in facets if f not in ignored]
        else:
            return facets

    def check_options(self, pairs):
        """
        Checks a {key: value} pairs against the corresponding options from the configuration file.

        :param dict pairs: A dictionary of {key: value} to check
        :raises Error: If the value is missing in the corresponding options list

        """
        for key in pairs.keys():
            options, option = self.get_options(key)
            try:
                # get_options returned a list
                if pairs[key] not in options:
                    raise NoConfigValue(pairs[key], option)
            except TypeError:
                # get_options returned a regex from pattern
                if not options.match(pairs[key]):
                    raise NoConfigValue(pairs[key], option)
                else:
                    self.check_options(options.match(pairs[key]).groupdict())

    def get_options(self, option):
        """
        Returns the list of attribute options.

        :param str option: The option to get available values
        :returns: The option values
        :rtype: *list* or *re.RegexObject*
        :raises Error: If the option is missing

        """
        if self.has_option('{}_options'.format(option)):
            option = '{}_options'.format(option)
            return self.get_options_from_list(option), option
        elif self.has_option('{}_map'.format(option)):
            option = '{}_map'.format(option)
            return self.get_options_from_map(option), option
        elif self.has_option('{}_pattern'.format(option)):
            option = '{}_pattern'.format(option)
            return self.get_options_from_pattern(option), option
        else:
            raise NoConfigOptions(option)

    def get_options_from_list(self, option):
        """
        Returns the list of option values from options list.

        :param str option: The option to get available values
        :returns: The option values
        :rtype: *list*
        :raises Error: If the section does not exist
        :raises Error: If the option does not exist

        """
        if not self.has_option(option):
            raise NoConfigOption(option)
        if option.rsplit('_options')[0] == 'experiment':
            options = self.get_options_from_table(option, field_id=2)
        else:
            options = split_line(self.get(option), sep=',')
        return options

    def get_options_from_table(self, option, field_id=None):
        """
        Returns the list of options from options table (i.e., <field1> | <field2> | <field3> | etc.).

        :param str option: The option to get available values
        :param int field_id: The field number starting from 1 (if not return the tuple)
        :returns: The option values
        :rtype: *list*
        :raises Error: If the section does not exist
        :raises Error: If the option does not exist
        :raises Error: If the options table is misdeclared

        """
        if not self.has_option(option):
            raise NoConfigOption(option)
        option_lines = split_line(self.get(option).lstrip(), sep='\n')
        if len(option_lines) == 1 and not option_lines[0]:
            return list()
        try:
            if field_id:
                options = [tuple(option)[field_id - 1] for option in map(lambda x: split_line(x), option_lines)]
            else:
                options = [tuple(option) for option in map(lambda x: split_line(x), option_lines)]
        except:
            raise MisdeclaredOption(option)
        return options

    def get_options_from_pairs(self, option, key):
        """
        Returns the list of option values from pairs table (i.e., <key> | <value>).

        :param str option: The option to get available values
        :param str key: The key to get the value
        :returns: The key value
        :rtype: *str*
        :raises Error: If the section does not exist
        :raises Error: If the option does not exist
        :raises Error: If the key does not exist
        :raises Error: If the options table is misdeclared

        """
        if not self.has_option(option):
            raise NoConfigOption(option)
        options_lines = split_line(self.get(option), sep='\n')
        try:
            options = dict((k, v) for k, v in map(lambda x: split_line(x), options_lines[1:]))
        except:
            raise MisdeclaredOption(option)
        try:
            return options[key]
        except KeyError:
            raise NoConfigKey(key, option)

    def get_options_from_map(self, option, key=None):
        """
        Returns the list of option values from maptable.
        If no key submitted, the option name has to be ``<key>_map``.

        :param str option: The option to get available values
        :param str key: The key to get the values
        :returns: The option values
        :rtype: *list*
        :raises Error: If the section does not exist
        :raises Error: If the option does not exist
        :raises Error: If the related key is not in the source/destination keys of the maptable

        """
        if not self.has_option(option):
            raise NoConfigOption(option)
        if not key:
            key = option.split('_map')[0]
        from_keys, to_keys, value_map = split_map(self.get(option))
        if key in from_keys:
            return list(set([value[from_keys.index(key)] for value in value_map.keys()]))
        else:
            return list(set([value[to_keys.index(key)] for value in value_map.values()]))

    def get_option_from_map(self, option, pairs):
        """
        Returns the destination values corresponding to key values from maptable.
        The option name has to be ``<key>_map``. The key has to be in the destination keys of the maptable header.

        :param str option: The option to get the value
        :param dict pairs: A dictionary of {from_key: value} to input the maptable
        :returns: The corresponding option value
        :rtype: *list*
        :raises Error: If the section does not exist
        :raises Error: If the option does not exist
        :raises Error: If the key values are not in the destination keys of the maptable

        """
        if not self.has_option(option):
            raise NoConfigOption(option)
        from_keys, to_keys, value_map = split_map(self.get(option))
        key = option.split('_map')[0]
        if key not in to_keys:
            raise MisdeclaredOption(option, details="'{}' has to be in 'destination key'".format(key))
        from_values = tuple(pairs[k] for k in from_keys)
        to_values = value_map[from_values]
        return to_values[to_keys.index(key)]

    def get_options_from_pattern(self, option):
        """
        Returns the expanded regex from ``key_pattern``.
        The option name has to be ``<attr>_pattern``.

        :param str option: The option to get available values
        :returns: The expanded regex
        :rtype: *re.RegexObject*
        :raises Error: If the section does not exist
        :raises Error: If the option does not exist

        """
        if not self.has_option(option):
            raise NoConfigOption(option)
        pattern = self.get(option, raw=True)
        # Translate all patterns matching %(digit)s
        pattern = re.sub(re.compile(r'%\((digit)\)s'), r'[\d]+', pattern)
        # Translate all patterns matching %(string)s
        pattern = re.sub(re.compile(r'%\((string)\)s'), r'[\w]+', pattern)
        # Translate all patterns matching %(facet)s
        pattern = re.sub(re.compile(r'%\(([^()]*)\)s'), r'(?P<\1>[\w.-]+)', pattern)
        return re.compile(pattern)

    def get_patterns(self):
        """
        Get all ``key_patterns`` options declared into the project section.

        :returns: A dictionary of {option: pattern}
        :rtype: *dict*

        """
        patterns = dict()
        for option in self.options(defaults=False):
            if '_pattern' in option and option != 'version_pattern':
                patterns[option] = self.get_options_from_pattern(option)
        return patterns


def interpolate(rawval, variables):
    """
    Makes string interpolation outside of ``ConfigParser.ConfigParser`` class.

    :param str rawval: The string to interpolate
    :param dict variables: The dictionary of variables to replace with
    :return:
    """
    pattern = re.compile(r"%\(([^)]*)\)s|.")
    value = rawval
    depth = MAX_INTERPOLATION_DEPTH
    while depth:
        depth -= 1
        if value and "%(" in value:
            value = pattern.sub(interpolation_replace, value)
            try:
                value = value % variables
            except KeyError:
                raise BadInterpolation(value, variables)
        else:
            break
    if value and "%(" in value:
        raise InterpolationDepthError(rawval)
    return value


def interpolation_replace(match):
    """
    Used to interpolate deep strings.
    """
    s = match.group(1)
    if s is None:
        return match.group()
    else:
        return "%%(%s)s" % s.lower()


def split_line(line, sep='|'):
    """
    Split a line into fields removing trailing and leading characters.

    :param str line: String line to split
    :param str sep: Separator character
    :returns: The fields
    :rtype: *list*

    """
    fields = map(string.strip, line.split(sep))
    return fields


def build_line(fields, sep=' | ', length=None, indent=False):
    """
    Build a line from fields adding trailing and leading characters.

    :param tuple fields: Tuple of ordered fields
    :param str sep: Separator character
    :param tuple length: The fields length
    :param boolean indent: True to indent the line
    :returns: The line
    :rtype: *str*

    """
    if length:
        fields = [format(fields[i], str(length[i])) for i in range(len(fields))]
    line = sep.join(fields)
    if indent:
        return ' ' * 4 + line
    else:
        return line


def lengths(fields):
    """
    Returns the maximum length among items of a list of tuples.
    :param list fields:
    :returns: The fields lengths
    :rtype: *tuple*

    """
    return tuple([max(map(len, f)) for f in zip(*fields)])


def split_record(option, sep='|'):
    """
    Split a multi-line record in a configuration file.

    :param str option: Option in the configuration file.
    :param str sep: Separator character.
    :returns: A list of the form [[field1A, field2A, ...], [field1B, field2B, ...]]

    """
    result = []
    for record in option.split('\n'):
        if record == '':
            continue
        fields = split_line(record, sep)
        result.append(fields)
    return result


def split_map_header(header):
    """
    Split header of a multi-line map in a configuration file.
    A map header defines the mapping between two sets of facets id.

    :param str header: Header line of multi-line map
    :returns: 'from' and 'to' tuples representing the keys for the mapping

    """
    header_pattern = re.compile(r'map\s*\((?P<from_keys>[^(:)]*):(?P<to_keys>[^(:)]*)\)')
    result = re.match(header_pattern, header).groupdict()
    if result is None:
        raise InvalidMapHeader(header_pattern, header)
    from_keys = split_line(result['from_keys'], sep=',')
    to_keys = split_line(result['to_keys'], sep=',')
    return from_keys, to_keys


def split_map(option, sep='|'):
    """
    Split a multi-line map in a configuration file.

    :param str option: Option in the configuration file
    :param str sep: Separator character
    :returns: A dictionary mapping the 'from' tuples to the 'to' tuples

    """
    lines = option.split('\n')
    header = lines[0]
    from_keys, to_keys = split_map_header(header)
    n_from = len(from_keys)
    result = {}
    for record in lines[1:]:
        if record == '':
            continue
        fields = map(string.strip, record.split(sep))
        from_values = tuple(fields[0:n_from])
        to_values = tuple(fields[n_from:])
        if from_values not in result.keys():
            result[from_values] = to_values
        else:
            raise DuplicatedMapEntry(fields, option)
        if len(from_values) != n_from:
            raise InvalidMapEntry(fields, header, option)
    return from_keys, to_keys, result
