from openvas_edxml.logger import log
from openvas_edxml.brick import OpenVASBrick
from openvas_edxml.transcoders import post_process_ip

from edxml.ontology import EventProperty
from edxml.transcode.xml import XmlTranscoder

from edxml_bricks.generic import GenericBrick
from edxml_bricks.computing.generic import ComputingBrick
from edxml_bricks.computing.networking.generic import NetworkingBrick


class OpenVasReportTranscoder(XmlTranscoder):

    TYPES = ['org.openvas.scan']

    TYPE_MAP = {'.': 'org.openvas.scan'}

    PROPERTY_MAP = {
        'org.openvas.scan': {
            '@id': 'id',
            '../task/name': 'name',
            'ports/port/host': ['host.ipv4', 'host.ipv6'],
            'hosts/count': 'host-count',
            'vulns/count': 'finding-count',
            'scan_start': 'time-start',
            'scan_end': 'time-end'
        }
    }

    TYPE_DESCRIPTIONS = {
        'org.openvas.scan': 'OpenVAS vulnerability scan'
    }

    TYPE_DISPLAY_NAMES = {
        'org.openvas.scan': ['OpenVAS scan']
    }

    TYPE_SUMMARIES = {
        'org.openvas.scan': 'OpenVAS scan named "[[name]]"'
    }

    TYPE_STORIES = {
        'org.openvas.scan':
            'On [[date_time:time-start,minute]] an OpenVAS vulnerability scan{ ([[name]])} was initiated, targeting '
            '[[host-count]] hosts. The scan{ [[empty:time-end,is incomplete]]}{ was completed in '
            '[[duration:time-start,time-end]]} yielding [[finding-count]] '
            'findings{ and was assigned UUID [[id]]}.{ The IP addresses of the scan targets are '
            '[[merge:host.ipv4,host.ipv6]].}'
    }

    TYPE_PROPERTIES = {
        'org.openvas.scan': {
            'id': ComputingBrick.OBJECT_UUID,
            'name': OpenVASBrick.OBJECT_SCAN_NAME,
            'host.ipv4': NetworkingBrick.OBJECT_HOST_IPV4,
            'host.ipv6': NetworkingBrick.OBJECT_HOST_IPV6,
            'host-count': GenericBrick.OBJECT_COUNT_BIG,
            'finding-count': GenericBrick.OBJECT_COUNT_BIG,
            'time-start': GenericBrick.OBJECT_DATETIME,
            'time-end': GenericBrick.OBJECT_DATETIME,
        }
    }

    TYPE_PROPERTY_CONCEPTS = {
        'org.openvas.scan': {
            'id': {OpenVASBrick.CONCEPT_SCAN: 10},
            'name': {OpenVASBrick.CONCEPT_SCAN: 2},
            'host-count': {OpenVASBrick.CONCEPT_SCAN: 0},
            'finding-count': {OpenVASBrick.CONCEPT_SCAN: 0},
            'host.ipv4': {ComputingBrick.CONCEPT_COMPUTER: 8},
            'host.ipv6': {ComputingBrick.CONCEPT_COMPUTER: 8}
        },
    }

    TYPE_PROPERTY_CONCEPTS_CNP = {
        'org.openvas.scan': {
            'name': {OpenVASBrick.CONCEPT_SCAN: 180},
            'host.ipv4': {ComputingBrick.CONCEPT_COMPUTER: 180},
            'host.ipv6': {ComputingBrick.CONCEPT_COMPUTER: 180},
        }
    }

    TYPE_PROPERTY_ATTRIBUTES = {
        'org.openvas.scan': {
            'id': {
                OpenVASBrick.CONCEPT_SCAN: [
                    ComputingBrick.OBJECT_UUID + ':openvas.scan', 'OpenVAS scan ID'
                ]
            },
            'host-count': {
                OpenVASBrick.CONCEPT_SCAN: [
                    GenericBrick.OBJECT_COUNT_BIG + ':host-count', 'scanned host count'
                ]
            },
            'finding-count': {
                OpenVASBrick.CONCEPT_SCAN: [
                    GenericBrick.OBJECT_COUNT_BIG + ':finding-count', 'finding count'
                ]
            }
        }
    }

    TYPE_OPTIONAL_PROPERTIES = {
        'org.openvas.scan': ['host.ipv4', 'host.ipv6', 'time-end']
    }

    TYPE_MULTI_VALUED_PROPERTIES = {
        'org.openvas.scan': ['host.ipv4', 'host.ipv6']
    }

    TYPE_PROPERTY_DESCRIPTIONS = {
        'org.openvas.scan': {
            'id': 'OpenVAS UUID',
            'host.ipv4': 'target host (IPv4)',
            'host.ipv6': 'target host (IPv6)',
            'finding-count': 'finding count',
            'time-start': 'starting time',
            'time-end': 'completion time',
        }
    }

    TYPE_HASHED_PROPERTIES = {
        'org.openvas.scan': ['id']
    }

    TYPE_PROPERTY_MERGE_STRATEGIES = {
        'org.openvas.scan': {
            'host.ipv4': EventProperty.MERGE_ADD,
            'host.ipv6': EventProperty.MERGE_ADD,
            'host-count': EventProperty.MERGE_MAX,
            'finding-count': EventProperty.MERGE_MAX,
            'time-end': EventProperty.MERGE_SET
        }
    }

    TYPE_PROPERTY_POST_PROCESSORS = {
        'org.openvas.scan': {'host.ipv4': post_process_ip, 'host.ipv6': post_process_ip}
    }

    TYPE_AUTO_REPAIR_NORMALIZE = {
        'org.openvas.scan': ['host.ipv4', 'host.ipv6', 'time-start', 'time-end']
    }

    TYPE_AUTO_REPAIR_DROP = {
        'org.openvas.scan': ['host.ipv4', 'host.ipv6']
    }

    TYPE_TIME_SPANS = {'org.openvas.scan': ('time-start', 'time-end')}

    def post_process(self, event, input_element):

        if not event['time-end']:
            log.warning('This scan report is incomplete, its scan_end tag is empty.\n')
        else:
            filtering = input_element.find('filters/term').text
            if 'rows=' in filtering and 'rows=-1' not in filtering:
                log.warning('This scan report may be incomplete, it has been capped to a maximum result count.\n')

        yield event

    @classmethod
    def create_event_type(cls, event_type_name, ontology):

        result = super().create_event_type(event_type_name, ontology)

        # Use intra relations to link the scan ID to other scan attributes
        result['id'].relate_intra('has', 'name')\
            .because('OpenVAS scan [[id]] is named [[name]]')
        result['id'].relate_intra('scanned', 'host-count')\
            .because('OpenVAS scan [[id]] scanned [[host-count]] hosts')
        result['id'].relate_intra('found', 'finding-count')\
            .because('OpenVAS scan [[id]] yielded [[finding-count]] findings')

        # Create inter-concept relations to relate the scan to the hosts that were scanned
        result['id'].relate_inter('scanned', 'host.ipv4')\
            .because('OpenVAS scan [[id]] scanned host [[host.ipv4]]')
        result['id'].relate_inter('scanned', 'host.ipv6')\
            .because('OpenVAS scan [[id]] scanned host [[host.ipv6]]')
