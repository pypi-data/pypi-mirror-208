"""Tests the classes and interfaced created for supporting DevOps
"""

from platinumtools.aws_classes.class_guardian import *


def test_token_guardian_accepts_token():
    basicTokenGuard = BasicTokenGuardian(token="1234")
    sample_event = {"token": "1234", "data": "etc"}
    assert(basicTokenGuard.inspect(sample_event) == True)


def test_token_guardian_rejecs_token():
    basicTokenGuard = BasicTokenGuardian(token="12346")
    sample_event = {"token": "1234", "data": "etc"}
    assert(basicTokenGuard.inspect(sample_event) == False)


def test_token_guardian_filters_usefuldicts():
    basicTokenGuard = BasicTokenGuardian(token="12346")
    sample_event = [{"token": "1234", "data": "etc"}, {"token": "12346", "data": "etc"}, {"token": "12346", "data": "etc2"}]
    assert(basicTokenGuard.filter(sample_event) == [{"token": "12346", "data": "etc"}, {"token": "12346", "data": "etc2"}])

def test_token_guardian_detains_bad_tokens():
    basicTokenGuard = BasicTokenGuardian(token="12346")
    sample_event = [{"token": "1234", "data": "etc"}, {"token": "12346", "data": "etc"}, {"token": "12346", "data": "etc2"}]
    basicTokenGuard.filter(sample_event)

    assert( basicTokenGuard.detained == [{"token": "1234", "data": "etc"}])

def test_token_guardian_detains_no_tokens():
    basicTokenGuard = BasicTokenGuardian(token="12346")
    sample_event = [{ "data": "etc"}, {"token": "12346", "data": "etc"}, {"token": "12346", "data": "etc2"}]
    basicTokenGuard.filter(sample_event)

    assert( basicTokenGuard.detained == [{"data": "etc"}])

def test_token_guardian_empty_filters_nothing():
    basicTokenGuard = BasicTokenGuardian(token="12346")
    sample_event = []
    assert(basicTokenGuard.filter(sample_event) == [])



