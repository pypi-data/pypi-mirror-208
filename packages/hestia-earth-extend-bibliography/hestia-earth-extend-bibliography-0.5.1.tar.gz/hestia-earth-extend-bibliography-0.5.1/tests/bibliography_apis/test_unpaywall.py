from unittest.mock import patch
import json

from tests.utils import fixtures_path, get_citations, clean_actors, clean_bibliography
from hestia_earth.extend_bibliography.bibliography_apis.unpaywall import (
    extend_unpaywall, extend_bibliography_pdf, extend_source_license
)


class FakeGetRequest():
    def __init__(self, type='search'):
        with open(f"{fixtures_path}/unpaywall/{type}-response.json", 'r') as f:
            self.content = json.load(f)

    def json(self):
        return self.content


def get_exception(): raise Exception('error')


@patch('requests.get', return_value=FakeGetRequest())
def test_extend_unpaywall(*args):
    with open(f"{fixtures_path}/unpaywall/results.json", 'r') as f:
        expected = json.load(f).get('results')
    (actors, bibliographies) = extend_unpaywall(get_citations())
    # actor ids are all random, so update result to make sure tests are passing
    result = list(map(clean_actors(expected), actors)) + list(map(clean_bibliography, bibliographies))
    assert result == expected


@patch('requests.get', side_effect=get_exception)
def test_extend_unpaywall_exception(*args):
    assert extend_unpaywall(['title']) == ([], [])


def test_extend_bibliography_pdf_no_doi():
    bibliography = {}
    result = extend_bibliography_pdf(bibliography)
    assert result == bibliography


@patch('requests.get', return_value=FakeGetRequest('doi'))
def test_extend_bibliography_pdf_with_doi(*args):
    bibliography = {'documentDOI': '10.1117/1.jbo.18.2.026003'}
    result = extend_bibliography_pdf(bibliography)
    assert result == {
        **bibliography,
        'articlePdf': 'http://europepmc.org/articles/pmc3556647?pdf=render'
    }


def test_extend_source_license_no_doi():
    source = {'bibliography': {}}
    result = extend_source_license(source)
    assert result == source


@patch('requests.get', return_value=FakeGetRequest('doi'))
def test_extend_source_license_with_doi(*args):
    source = {'bibliography': {'documentDOI': '10.1117/1.jbo.18.2.026003'}}
    result = extend_source_license(source)
    assert result == source
