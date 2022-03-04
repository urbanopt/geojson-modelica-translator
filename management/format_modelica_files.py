"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the
distribution.

Neither the name of the copyright holder nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
****************************************************************************************************
"""

import os
import re
import subprocess
from pathlib import Path
from tempfile import mkstemp

import click

SKIP_FILES = ['DistrictEnergySystem.mot']
TEMPLATE_FILES = Path('geojson_modelica_translator/model_connectors').glob('**/templates/*')


@click.command()
@click.argument('mofile', required=False)
def fmt_modelica_files(mofile):
    if mofile is not None:
        files = [mofile]
    else:
        files = TEMPLATE_FILES

    for filepath in files:
        if os.path.basename(filepath) in SKIP_FILES:
            continue
        try:
            if filepath.suffix == ".mot":
                preprocess_and_format(str(filepath))
            elif filepath.suffix == ".mo":
                apply_formatter(str(filepath))
        except FormattingException as e:
            click.echo(f'Error processing file {filepath}:\n    {e}', err=True)


class FormattingException(Exception):
    pass


def apply_formatter(filepath):
    """
    Run modelicafmt on a file

    :param filepath: str, path to file
    """
    try:
        subprocess.run(["modelicafmt", "-w", filepath], stdout=subprocess.PIPE, check=True)
    except FileNotFoundError:
        raise FormattingException('Failed to run modelicafmt; ensure it can be found in $PATH')
    except subprocess.CalledProcessError as e:
        raise FormattingException(f'Failed to format filename: {e.stdout}')


class SubMap:
    """
    Class for managing substitutions into modelica template files (ie Jinja templates)
    """

    def __init__(self):
        self._cur_id = 1
        self._map = {}

    def add_sub(self, text):
        """
        Registers a substitution and returns the substitution name

        :param text: str, text to substitute
        :returns: str, substitution name/id
        """
        sub_id = f'JINJA_SUB_{self._cur_id:03}'
        self._map[sub_id] = text
        self._cur_id += 1

        return sub_id

    def get_text(self, sub):
        """
        Get original text for a substitution

        :param sub: str, substitution name
        :returns: str, text corresponding to that substitution name
        """
        try:
            return self._map[sub]
        except KeyError:
            raise FormattingException(f'Key "{sub}" was not found in the substitution map, this should never happen... '
                                      f'Perhaps the substitution name was a false positive match?')


GENERIC_CONTROL_REGEX = re.compile('({%.*?%})')


def sub_generic(text, sub_map):
    """
    Substitutes all Jinja control statements, those that look like {% ... %}

    :param text: str, text to make substitutions in
    :param sub_map: SubMap
    :returns: str, text post substitutions
    """
    matches = reversed([m.span() for m in GENERIC_CONTROL_REGEX.finditer(text)])
    for span in matches:
        sub_id = sub_map.add_sub(text[span[0]:span[1]])
        text = f'{text[:span[0]]}/*{sub_id}*/{text[span[1]:]}'

    return text


EXPRESSION_REGEX = re.compile('({{.*?}})')


def sub_expression(text, sub_map):
    """
    Substitutes all Jinja expression statements, those that look like {{ ... }}

    :param text: str, text to make substitutions in
    :param sub_map: SubMap
    :returns: str, text post substitutions
    """
    matches = reversed([m.span() for m in EXPRESSION_REGEX.finditer(text)])
    for span in matches:
        sub_id = sub_map.add_sub(text[span[0]:span[1]])
        text = f'{text[:span[0]]}{sub_id}{text[span[1]:]}'

    return text


COMMENTED_SUB = re.compile(r'/\*(JINJA_SUB_\d\d\d)\*/')
NORMAL_SUB = re.compile(r'JINJA_SUB_\d\d\d')


def reverse_sub(text, sub_map):
    """
    Reverses Jinja substitutions, ie replaces the JINJA_SUB_XXX texts with their
    original texts

    :param text: str, text to reverse substitutions
    :param sub_map: SubMap, the submap used for making substitutions
    :returns: str, text with substitutions reversed
    """
    # remove the comments around commented substitutions
    text = COMMENTED_SUB.sub(r'\1', text)

    # replace all substitutions with their original values
    def _replace(matchobj):
        return sub_map.get_text(matchobj.group(0))
    text = NORMAL_SUB.sub(_replace, text)

    return text


def preprocess_and_format(filename, outfilename=None):
    """
    Formats modelica files that include Jinja templating.

    :param filename: str, template file to format
    """
    try:
        with open(filename) as f:
            contents = f.read()
    except FileNotFoundError:
        raise FormattingException(f'File "{filename}" not found.')

    tmp_fd, tmp_filepath = mkstemp()
    try:
        # General strategy:
        #   1. replace all Jinja templating stuff with unique IDs, additionally
        #      commenting out any IDs that would result in invalid modelica
        #      syntax (those that are flow control, ie {% ... %}). After this
        #      step the file should be "valid" from the modelica lexer's perspective
        #   2. apply modelica formatter to format the file
        #   3. reverse the substitutions, replacing IDs with their original text
        sub_map = SubMap()
        previous_span = (0, 0)
        raw_regex = re.compile(r'{% raw %}[\s\S]*?{% endraw %}')
        raw_groups = [m.span() for m in raw_regex.finditer(contents)]
        with open(tmp_fd, 'w') as f:
            for span in raw_groups:
                # format from previous end to new start
                text = contents[previous_span[1]:span[0]]
                text = sub_generic(text, sub_map)
                text = sub_expression(text, sub_map)
                f.write(text)

                # format current span (should be raw)
                text = contents[span[0]:span[1]]
                text = sub_generic(text, sub_map)
                f.write(text)

                previous_span = span

            # finish from end of last span to end of file
            text = contents[previous_span[1]:]
            text = sub_generic(text, sub_map)
            text = sub_expression(text, sub_map)
            f.write(text)

        apply_formatter(tmp_filepath)

        # substitute original values back in
        with open(tmp_filepath, 'r') as f:
            formatted_result = reverse_sub(f.read(), sub_map)

        if outfilename is None:
            outfilename = filename
        with open(outfilename, 'w') as f:
            f.write(formatted_result)
    finally:
        os.remove(tmp_filepath)
