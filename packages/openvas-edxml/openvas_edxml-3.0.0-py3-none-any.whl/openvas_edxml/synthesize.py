#!/usr/bin/env python3
import datetime

import openvas_edxml
from edxml import EDXMLWriter
from edxml.miner.knowledge import KnowledgeBase
from edxml.synthesizer.scenario import Scenario
from edxml.transcode import TranscoderMediator
from openvas_edxml.brick import OpenVASBrick


def main():
    with TranscoderMediator() as mediator:
        openvas_edxml.register_transcoders(mediator)
        ontology = mediator._ontology

    source_uri = '/some/uri/'
    ontology.create_event_source(source_uri)

    file = open('/home/user/development/edxml/sources/idrs-openvas/output-snippet-mined.json', mode='r')
    knowledge = KnowledgeBase.from_json(file.read())

    # Extract the scan from the knowledge base and
    # find the number of scan results. We need the number
    # of generated scan result events to match.
    scan = knowledge.filter_concept(OpenVASBrick.CONCEPT_SCAN).concept_collection.concepts.popitem()[1]
    num_findings = int(scan.get_attributes('count.big:host-count')[0].value)
    scan_timeline = scan.get_attributes('count.big:host-count')[0].confidence_timeline.pop()

    # Find the scan duration and compute the average delay
    # between new findings as the scan is running
    scan_duration = scan_timeline[1] - scan_timeline[0]
    result_delay = scan_duration.total_seconds() / num_findings

    s = Scenario(ontology=ontology, knowledge_base=knowledge)

    # Scenario starts with a scan event
    # TODO: Should scan go at the end in stead?
    s.at(datetime.datetime.now())\
        .from_source(source_uri)\
        .with_type(ontology.get_event_type('org.openvas.scan'))\
        .with_timespan_length(time_delta=scan_duration)\
        .repeat(1)

    # Then a series of OpenVAS finding events
    # TODO: What if the requested number of findings cannot be generated? Exception raised?
    s.then()\
        .from_source(source_uri)\
        .with_type(ontology.get_event_type('org.openvas.scan.result'))\
        .repeat(num_findings, delay=result_delay, time_jitter=result_delay)

    # Generate the data
    writer = EDXMLWriter()
    writer.add_ontology(ontology)

    for event in s.generate():
        writer.add_event(event)

    writer.close()


if __name__ == "__main__":
    main()
