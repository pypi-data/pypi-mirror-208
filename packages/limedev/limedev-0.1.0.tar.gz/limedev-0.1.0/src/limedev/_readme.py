import datetime
import pathlib
import re
from typing import Any
from typing import Iterable
from typing import Optional

import yamdog as md
#=======================================================================

re_heading = re.compile(r'^#* .*$')

def parse_md_element(text: str):
    if match := re_heading.match(text):
        hashes, content = match[0].split(' ', 1)
        return md.Heading(content, len(hashes))
    else:
        return md.Raw(text)
#-----------------------------------------------------------------------
def parse_md(text: str):
    return md.Document([parse_md_element(item.strip())
                        for item in text.split('\n\n')])
#=======================================================================
def make_intro(full_name, pypiname, semi_description):

    shields_url = 'https://img.shields.io/'

    pypi_project_url = f'https://pypi.org/project/{pypiname}'
    pypi_badge_info = (('v', 'PyPI Package latest release'),
                       ('wheel', 'PyPI Wheel'),
                       ('pyversions', 'Supported versions'),
                       ('implementation', 'Supported implementations'))
    pypi_badges = [md.Link(pypi_project_url,
                           md.Image(f'{shields_url}pypi/{code}/{pypiname}.svg',
                                    desc), 'Project PyPI page')
                   for code, desc in pypi_badge_info]
    doc = md.Document([md.Paragraph(pypi_badges, '\n'),
                       md.Heading(full_name, 1, in_TOC = False)])
    doc += semi_description
    doc += md.Heading('Table of Contents', 2, in_TOC = False)
    doc += md.TOC()
    return doc
#=======================================================================
def make_setup_guide(name, pypiname, package_name, abbreviation = None):
    doc = md.Document([
        md.Heading('Quick start guide', 1),
        "Here's how you can start numerically ",
        md.Heading('The first steps', 2),
        md.Heading('Installing', 3),
        f'Install {name} with pip',
        md.CodeBlock(f'pip install {pypiname}'),
        md.Heading('Importing', 3),
        md.Paragraph([(f'Import name is '
                       f'{"" if pypiname == package_name else "not "}'
                       f'the same as install name, '),
                       md.Code(pypiname),
                       '.']),
        md.CodeBlock(f'import {package_name}', 'python')])

    if abbreviation is not None:
        doc += md.Paragraph(['Since the package is accessed often, I use abbreviation ',
                             md.Code(abbreviation),
                      '. The abbreviation is used throughout this document.']),
        doc += md.CodeBlock(f'import {pypiname} as {abbreviation}', 'python')
    return doc
#=======================================================================
def make_changelog(level: int, path_changelog: pathlib.Path, version: str):
    doc = md.Document([md.Heading('Changelog', level, in_TOC = False)])
    changelog = parse_md(path_changelog.read_text())
    if changelog:
        if (latest := changelog.content[0]).content.split(' ', 1)[0] == version:
            latest.content = f'{version} {datetime.date.today().isoformat()}'
        else:
            raise ValueError('Changelog not up to date')

        path_changelog.write_text(str(changelog) + '\n')

        for item in changelog:
            if isinstance(item, md.Heading):
                item.level = level + 1
                item.in_TOC = False

        doc += changelog

    return doc
#=======================================================================
def make(package,
         semi_description: Any,
         name = None,
         pypiname = None,
         quick_start: Any = None,
         readme_body: Any = None,
         annexes: Optional[Iterable[tuple[Any, Any]]] = None,
         ) -> md.Document:

    if name is None:
        name = package.__name__.capitalise()
    if pypiname is None:
        pypiname = package.__name__
    doc = make_intro(name, pypiname, semi_description)
    doc += make_setup_guide(name, pypiname, package.__name__)

    if quick_start is not None:
        doc += quick_start

    if readme_body is not None:
        doc += readme_body

    path_changelog = next(pathlib.Path(package.__file__).parent.parent.parent.rglob('*changelog.md'))
    doc += make_changelog(1, path_changelog, package.__version__)

    if annexes is not None:
        doc += make_annexes(annexes)
    return doc
#=======================================================================
def make_annexes(annexes: Iterable[tuple[Any, Any]]):
    doc = md.Document([md.Heading('Annexes', 1)])
    for index, (heading_content, body) in enumerate(annexes, start = 1):
        doc += md.Heading(2, f'Annex {index}: {heading_content}')
        doc += body
#=======================================================================
    return doc
