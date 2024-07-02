# pymodaq_simple.py
import datetime

import pandas as pd
import csv
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from nomad.units import ureg
from nomad.datamodel.metainfo.basesections import Measurement, MeasurementResult, Activity, ActivityResult, BaseSection
from nomad.metainfo import (
    Package,
    Quantity,
    SubSection,
    Section,
)
from nomad.datamodel.data import (
    EntryData,
    ArchiveSection,
)
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

m_package = Package(name='pymodaq_simple')


class PymodaqSimpleResult(MeasurementResult, ActivityResult):
    '''
    Class representing the result of a simple measurement in PyMoDAQ.
    '''
    m_def = Section(
        a_eln={
            "properties": {
                "order": [
                    "name",
                    "intensity",
                    "time"
                ]
            }
        }
    )

    name = Quantity(
        type=str,
        description='Channel Name'
    )

    intensity = Quantity(
        type=np.float64,
        shape=['*'],
        unit=ureg.volt,
        description='Intensity values of the measurement.'
    )

    time = Quantity(
        type=np.float64,
        shape=['*'],
        unit=ureg.second,
        description='Time values of the measurement.'
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `Pymodaq_Simple_Result` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super().normalize(archive, logger)
        if len(self.intensity) != len(self.time):
            logger.warning("Intensity and time arrays have different lengths.")
        # Additional normalization steps can be added here.


class PymodaqSimpleMeasurement(Measurement, Activity, BaseSection):
    '''
    Class representing a simple measurement in PyMoDAQ.
    '''
    m_def = Section(
        a_eln={
            "properties": {
                "order": [
                    "name",
                    "results"
                ]
            }
        }
    )

    name = Quantity(
        type=str,
        description='Author name.'
    )

    results = SubSection(
        section_def=PymodaqSimpleResult,
        repeats=True,
    )
    data_file = Quantity(
        type=str,
        description='File name of raw data',
        a_eln={
            "component": "FileEditQuantity",
        },
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `Pymodaq_Simple_Measurement` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being normalized.
            logger (BoundLogger): A structlog logger.
        '''

        super().normalize(archive, logger)
        results = []
        if self.data_file:
            with archive.m_context.raw_file(self.data_file) as file:
                reader = csv.reader(file, delimiter=',')

                name, date = next(reader)
                #print(name, date)
                self.name = name
                self.datetime = datetime.datetime.strptime(date, '%d/%m/%Y')

                try:
                    while True:
                        result = PymodaqSimpleResult()
                        result.name = next(reader)[0]
                        logger.info(result.name)
                        result.intensity = np.array(next(reader), dtype=np.float64)
                        result.time = np.array(next(reader), dtype=np.float64)
                        results.append(result)
                except StopIteration:
                    pass
        self.results = results
