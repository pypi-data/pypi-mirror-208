from os.path import dirname

import pytest

from edxml.transcode.xml import XmlTranscoderTestHarness
from openvas_edxml import register_transcoders, OpenVasErrorTranscoder


@pytest.fixture()
def harness():
    harness = XmlTranscoderTestHarness(
        fixtures_path=dirname(__file__) + '/fixtures',
        transcoder=OpenVasErrorTranscoder(),
        transcoder_root='/report/report/errors/error',
        register=False
    )
    register_transcoders(harness)
    return harness


def test_detection_errors(harness):
    harness.process_xml(
        'errors.xml',
        element_root='.'
    )

    assert len(harness.events.filter_type('org.openvas.scan.error')) == 1

    result = harness.events.filter_type('org.openvas.scan.error').pop()

    assert result['scan-id'] == {'fb167629-3bdf-4ab1-ae7d-c64a0d7ad595'}
    assert result['time'] == {'2019-01-01T12:01:01.000000Z'}
    assert result['nvt.oid'] == {'1.3.6.1.4.1.25623.1.0.804489'}
    assert result['nvt.name'] == {'GNU Bash Environment Variable Handling Shell Remote Command Execution Vulnerability'}
    assert result['message'] == {'NVT timed out after 320 seconds.'}
    assert result['host.ipv4'] == {'10.0.0.1'}

    assert result.get_attachments() == {}


def test_detection_errors_ipv6(harness):
    harness.process_xml(
        'errors-ipv6.xml',
        element_root='.'
    )

    result = harness.events.filter_type('org.openvas.scan.error').pop()

    assert result['host.ipv6'] == {'2001:0db8:0000:0000:0000:8a2e:0370:7334'}
