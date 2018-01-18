# type nosetests to exeute the tests, alternative is  py.test (python -m pytest <spacy-directory> --vectors --model --slow) - you are able to use assert
from nose.tools import *
import NAME

def setup():
    print "SETUP!"

def teardown():
    print "TEAR DOWN!"

def test_basic():
    print "I RAN!"
