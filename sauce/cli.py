import click
import os
import re
import yaml
import tarfile


# Sauce is a command line tool for searching files and lines for keywords.

def unzip_tarfile(file_path):
    '''Extract tarfile.'''
    click.echo('extracting ' + file_path)
    try:
        tar = tarfile.open(file_path)
        tar.extractall()
        tar.close()
        return True
    except BaseException as e:
        click.echo('error: file not extracted')
        return False

def load_yaml(file_path):
    '''Load search configs from yaml file.'''
    click.echo('loading yaml ' + file_path)
    try:
        with open(file_path, "r") as stream:
            doc = yaml.load(stream)  # TODO validate
        return doc
    except yaml.parser.ParserError as e:
        click.echo('error: yaml.parser.ParserError: yaml syntax invalid')
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

def get_lines(file_path, doc, max_lines, show_duplicates):
    '''Search file contents.'''
    excluded_terms = doc['lines']['exclude']
    included_terms = doc['lines']['include']
    lines = []
    try:
        with open(file_path) as f:
            for line in f:
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

def get_files(path, doc):
    '''Walk directory tree for matching folders, files and lines.'''
    excluded_files = doc['files']['exclude']
    included_files = doc['files']['include']
    file_paths = []
    n = 0
    for root, dirs, files in os.walk(path):
        # if check_terms(root, excluded_folders, included_folders):
        for _file in files:
            n += 1
            if check_terms(_file, excluded_files, included_files):
                file_path = os.path.join(root, _file)
                file_paths.append(file_path)
    click.echo('total files ' + str(n))
    return file_paths

def get_results(path, doc, max_lines, step, show_duplicates):
    '''Get and click.echo matching file paths, and lines.'''
    click.echo('search params ' + str(doc))
    file_paths = get_files(path, doc)
    click.echo('files checked ' + str(len(file_paths)))
    click.echo('\n')
    results = []
    for file_path in file_paths:
        lines = get_lines(file_path, doc, max_lines, show_duplicates)
        if lines:
            click.echo(file_path)
            click.echo(re.sub(r'.', '=', file_path))
            for line in lines:
                click.echo(line)
            click.echo('\n')
            if step:
                input("==>..\n")
            # results.append(lines)
    # click.echo('lines found ' + str(len(results)))
    return [file_paths, results]

@click.command()
@click.argument('path', default='.', required=False)
@click.option('--from-yaml', '-y', default=None, help='Use yaml file search paramaters.')
@click.option('--limit-lines', '-l', default=0, help='Limit number of line results to return from each file.')
# @click.option('--slice-search', '-s', default=None, help='Slice line searches with <start>:<end>')
# @click.option('--bottoms-up', '-b', is_flag=True, help='Read up from the bottom of files.')
# @click.option('--create-yaml', '-c', is_flag=True, help='Create yaml file from search arguments.')
@click.option('--walk-results', '-w', is_flag=True, help='Step through the results of each file.')
@click.option('--show-duplicates', '-d', is_flag=True, help='Show duplicate lines.')
@click.option('--extract-tarfile', '-t', default=None, help='Extract tarfile.')
@click.option('--lines-include', '-j', default=None, help='Line terms to be matched.')
@click.option('--lines-exclude', '-k', default=None, help='Line terms not to be matched.')
@click.option('--files-include', '-x', default=None, help='File name terms to be matched.')
@click.option('--files-exclude', '-y', default=None, help='File name terms not to be matched.')
def main(path, from_yaml, max_lines, step_results, show_duplicates, \
    extract_tarfile, lines_include, lines_exclude, files_include, files_exclude):
    doc = {'lines': {'exclude': None, 'include': None}, 'files': {'exclude': None, 'include': None}}
    if extract_tarfile:
        unzip_tarfile(extract_tarfile)
    if yaml_file:
        doc = load_yaml(from_yaml)
    if lines_include:
        doc['lines']['include'] = lines_include.strip().split(',')
    if lines_exclude:
        doc['lines']['exclude'] = lines_exclude.strip().split(',')
    if files_include:
        doc['files']['include'] = files_include.strip().split(',')
    if files_exclude:
        doc['files']['exclude'] = files_exclude.strip().split(',')
    get_results(path, doc, max_lines, step_results, show_duplicates)


if __name__ == '__main__':
    main()
