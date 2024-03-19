import os
import sys
import pip
import datetime
import argparse
import toml



### Get value from pyproject.toml

def pyproject_toml():
    project_fname = 'pyproject.toml'
    return os.path.join(os.path.split(__file__)[0], project_fname) 

def proj():
    return toml.load(pyproject_toml())

def keyPath():
    if len(sys.argv) < 2:
        return ''
    return sys.argv[1]

def getValue(d, element):
    keys = element.split('.')
    keys[-1] = keys[-1].split('-')[0] # macos-latest -> macos, etc.
    rv = d
    for key in keys:
        rv = rv[key]
    return rv

### Update pyproject.toml

def extraDict():
    python_packages_path = os.path.dirname(pip.__path__[0]).replace('\\', '/')

    dt = datetime.datetime.now()
    build_date = datetime.datetime.now().strftime('%d %b %Y')
    date_for_qtifw = f'{dt.year}-{dt:%m}-{dt:%d}'  # e.g. 2021-06-03

    github_server_url = os.getenv('GITHUB_SERVER_URL', '')
    github_repo = os.getenv('GITHUB_REPOSITORY', '')
    github_repo_url = f'{github_server_url}/{github_repo}'

    branch_name = os.getenv('BRANCH_NAME', '')
    branch_url = f'{github_repo_url}/tree/{branch_name}'

    commit_sha = os.getenv('GITHUB_SHA', '')
    commit_sha_short = commit_sha[:6]
    commit_url = f'{github_repo_url}/commit/{commit_sha}'

    app_version = getValue(proj(), 'project.version')
    release_tag = f'v{app_version}'
    release_title = f'Version {app_version} ({build_date})'

    return { 'paths': { 'python_packages_path': python_packages_path },
             'git': { 'build_date': build_date,
                      'date_for_qtifw': date_for_qtifw,
                      'release_tag': release_tag,
                      'release_title': release_title,
                      'branch_name': branch_name,
                      'branch_url': branch_url,
                      'commit_sha_short': commit_sha_short,
                      'commit_url': commit_url } } 

def extraToml():
    return toml.dumps(extraDict())

def updatePyProjectToml():
    output_dict = proj()
    output_dict['ci'].update(extraDict())
    with open(pyproject_toml(), 'w') as f:
        toml.dump(output_dict, f)

### Main

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--get', dest='key', type=str, help='get parameter value by key from pyproject.toml')
    parser.add_argument('-u', '--update', action='store_true', help='add extra info to the pyproject.toml')
    args = parser.parse_args()
    if args.key:
        value = getValue(proj(), args.key)
        print(value)
    if args.update:
        updatePyProjectToml()

if __name__ == '__main__':
    main()
