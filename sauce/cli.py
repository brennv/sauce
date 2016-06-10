import click
import os
import re
import yaml
import tarfile


def unzip_tarfile(file_path):
    '''Extract tarfile.'''
    click.echo('extracting ' + file_path)
    try:
        tar = tarfile.open(file_path)
        tar.extractall()
        tar.close()
        return True
    except BaseException as e:
        click.secho('error: file not extracted', fg='red')
        return False

def load_yaml(file_path):
    '''Load search configs from yaml file.'''
    click.secho('loading yaml ' + file_path, fg='green')
    try:
        with open(file_path, "r") as stream:
            doc = yaml.load(stream)  # TODO validate
        return doc
    except yaml.parser.ParserError as e:
        click.secho('error: yaml.parser.ParserError: yaml syntax invalid', fg='red')
        pass

def check_terms(item, excluded, included):
    '''Search item against lists of excluded and/or included terms.'''
    result = False
    if not excluded and not included:
        result = True
    else:
        if included:
            is_included = any(x.lower() in item.lower() for x in included)
        if excluded:
            is_excluded = any(x.lower() in item.lower() for x in excluded)
        if (excluded and included) and (not is_excluded and is_included):
            result = True
        if (included and not excluded) and is_included:
            result = True
        if (excluded and not included) and not is_excluded:
            result = True
    return result

def get_lines(doc, file_path):
    '''Search file contents.'''
    excluded_terms = doc['lines']['exclude']
    included_terms = doc['lines']['include']
    show_duplicates = doc['showDuplicates']
    max_lines = doc['lineLimit']
    lines = []
    try:
        with open(file_path) as f:
            for line in f:
                if len(line.strip()) > 0:
                    is_terms = check_terms(line, excluded_terms, included_terms)
                    if is_terms:
                        line = line.strip()
                        if show_duplicates:
                            lines.append(line)
                        else:
                            if line not in lines:
                                lines.append(line)
                        if max_lines != 0 and len(lines) > max_lines - 1:
                            return lines
    except BaseException as e:
        pass
    return lines

def get_files(doc, path):
    '''Walk directory tree for matching folders, files and lines.'''
    excluded_files = doc['files']['exclude']
    included_files = doc['files']['include']
    file_paths = []
    for root, dirs, files in os.walk(path):
        # if check_terms(root, excluded_folders, included_folders):
        for _file in files:
            if check_terms(_file, excluded_files, included_files):
                file_path = os.path.join(root, _file)
                file_paths.append(file_path)
    return file_paths

def print_lines(doc, file_paths):
    '''Display results.'''
    walk_results = doc['walkResults']
    lead = '\n'
    if walk_results:
        lead = '\n  '
    for file_path in file_paths:
        lines = get_lines(doc, file_path)
        if lines:
            header = lead + file_path + '\n'
            if walk_results:
                click.clear()
                click.echo_via_pager(('\n').join([header] + lines))
            else:
                click.echo(header)
                for line in lines:
                    click.echo(line)
    pass

def get_results(doc, path):
    '''Get matching file paths, and lines.'''
    file_paths = get_files(doc, path)
    if doc['walkResults']:
        click.clear()
        with click.progressbar(file_paths) as bar:
            print_lines(doc, bar)
    else:
        print_lines(doc, file_paths)
    click.secho('\nsearch params ' + str(doc), fg='green')
    click.secho('files checked ' + str(len(file_paths)), fg='green')
    click.echo()
    return file_paths

# @click.option('--slice-search', '-s', default=None, help='Slice line searches with <start>:<end>')
# @click.option('--bottoms-up', '-b', is_flag=True, help='Read up from the bottom of files.')
# @click.option('--create-yaml', '-c', is_flag=True, help='Create yaml file from search arguments.')

@click.command()
@click.argument('path', default='.', required=False)
@click.option('--show-duplicates', '-d', is_flag=True, help='Show duplicate lines.')
@click.option('--extract-tarfile', '-e', default=None, help='Extract tarfile.')
@click.option('--from-yaml', '-f', default=None, help='Use search paramaters from yaml file.')
@click.option('--lines-include', '-j', default=None, help='Line terms to be matched.')
@click.option('--lines-exclude', '-k', default=None, help='Line terms not to be matched.')
@click.option('--limit-lines', '-l', default=0, help='Limit number of line results to return from each file.')
@click.option('--walk-results', '-w', is_flag=True, help='Step through the results of each file.')
@click.option('--files-include', '-x', default=None, help='File name terms to be matched.')
@click.option('--files-exclude', '-y', default=None, help='File name terms not to be matched.')
def main(path, from_yaml, limit_lines, walk_results, show_duplicates, \
            extract_tarfile, lines_include, lines_exclude, files_include, files_exclude):
    doc = {'lines': {'exclude': None, 'include': None}, 'files': {'exclude': None, 'include': None}, \
            'showDuplicates': False, 'walkResults': False, 'lineLimit': 0}
    if extract_tarfile:
        unzip_tarfile(extract_tarfile)
    if from_yaml:
        doc = load_yaml(from_yaml)
    if lines_include:
        doc['lines']['include'] = lines_include.strip().split(',')
    if lines_exclude:
        doc['lines']['exclude'] = lines_exclude.strip().split(',')
    if files_include:
        doc['files']['include'] = files_include.strip().split(',')
    if files_exclude:
        doc['files']['exclude'] = files_exclude.strip().split(',')
    if show_duplicates:
        doc['showDuplicates'] = True
    if walk_results:
        doc['walkResults'] = True
    if limit_lines:
        doc['lineLimit'] = limit_lines
    get_results(doc, path)


if __name__ == '__main__':
    main()
