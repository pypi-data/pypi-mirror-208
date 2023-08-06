# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot

snapshots = Snapshot()

snapshots["TestConfigureLogCodes.test_correct_logging_codes[codes0] 1"] = GenericRepr(
    "mappingproxy(OrderedDict([('Generic', <LogCodeEnum.Generic: 1000>), ('InputDataValid', <LogCodeEnum.InputDataValid: 1100>), ('InvalidRawInputData', <LogCodeEnum.InvalidRawInputData: 1101>), ('InvalidInputFileAttribute', <LogCodeEnum.InvalidInputFileAttribute: 1102>), ('OutputDataValid', <LogCodeEnum.OutputDataValid: 1200>), ('InvalidIdsData', <LogCodeEnum.InvalidIdsData: 1201>), ('InvalidNonIdsData', <LogCodeEnum.InvalidNonIdsData: 1202>), ('InvalidOutputFileAttribute', <LogCodeEnum.InvalidOutputFileAttribute: 1203>), ('Configuration', <LogCodeEnum.Configuration: 1300>), ('InvalidPipelineConfiguration', <LogCodeEnum.InvalidPipelineConfiguration: 1301>), ('ProcessingStatus', <LogCodeEnum.ProcessingStatus: 1400>), ('ProcessingBegin', <LogCodeEnum.ProcessingBegin: 1401>), ('ProcessingEnd', <LogCodeEnum.ProcessingEnd: 1402>), ('ProcessingError', <LogCodeEnum.ProcessingError: 1403>), ('PlatformInteraction', <LogCodeEnum.PlatformInteraction: 1500>), ('SpaceOdyssey', <LogCodeEnum.SpaceOdyssey: 2001>), ('LoggerError', <LogCodeEnum.LoggerError: 4900>)]))"
)

snapshots["TestConfigureLogCodes.test_correct_logging_codes[codes1] 1"] = GenericRepr(
    "mappingproxy(OrderedDict([('Generic', <LogCodeEnum.Generic: 1000>), ('InputDataValid', <LogCodeEnum.InputDataValid: 1100>), ('InvalidRawInputData', <LogCodeEnum.InvalidRawInputData: 1101>), ('InvalidInputFileAttribute', <LogCodeEnum.InvalidInputFileAttribute: 1102>), ('OutputDataValid', <LogCodeEnum.OutputDataValid: 1200>), ('InvalidIdsData', <LogCodeEnum.InvalidIdsData: 1201>), ('InvalidNonIdsData', <LogCodeEnum.InvalidNonIdsData: 1202>), ('InvalidOutputFileAttribute', <LogCodeEnum.InvalidOutputFileAttribute: 1203>), ('Configuration', <LogCodeEnum.Configuration: 1300>), ('InvalidPipelineConfiguration', <LogCodeEnum.InvalidPipelineConfiguration: 1301>), ('ProcessingStatus', <LogCodeEnum.ProcessingStatus: 1400>), ('ProcessingBegin', <LogCodeEnum.ProcessingBegin: 1401>), ('ProcessingEnd', <LogCodeEnum.ProcessingEnd: 1402>), ('ProcessingError', <LogCodeEnum.ProcessingError: 1403>), ('PlatformInteraction', <LogCodeEnum.PlatformInteraction: 1500>), ('SpaceOdyssey', <LogCodeEnum.SpaceOdyssey: 2001>), ('LoggerError', <LogCodeEnum.LoggerError: 4900>), ('Foo', <LogCodeEnum.Foo: 5001>), ('Bar', <LogCodeEnum.Bar: 5002>)]))"
)
