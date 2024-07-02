# pymodaq_simple.py
import pandas as pd
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


class Pymodaq_Simple_Result(MeasurementResult, ActivityResult):
    '''
    Class representing the result of a simple measurement in PyMoDAQ.
    '''
    m_def = Section(
        a_eln={
            "properties": {
                "order": [
                    "intensity",
                    "time"
                ]
            }
        }
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
        super(Pymodaq_Simple_Result, self).normalize(archive, logger)
        if len(self.intensity) != len(self.time):
            logger.warning("Intensity and time arrays have different lengths.")
        # Additional normalization steps can be added here.


class Pymodaq_Simple_Measurement(Measurement, Activity, BaseSection):
    '''
    Class representing a simple measurement in PyMoDAQ.
    '''
    m_def = Section(
        a_eln={
            "properties": {
                "order": [
                    "name",
                    "instruments",
                    "samples",
                    "results"
                ]
            }
        }
    )

    name = Quantity(
        type=str,
        description='Name of the measurement.'
    )

    instruments = Quantity(
        type=str,
        description='Instruments used in the measurement.'
    )

    samples = Quantity(
        type=str,
        description='Samples used in the measurement.'
    )

    results = SubSection(
        section_def=Pymodaq_Simple_Result,
        repeats=True,
        description='Results of the measurement.'
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `Pymodaq_Simple_Measurement` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(Pymodaq_Simple_Measurement, self).normalize(archive, logger)
        if self.name:
            logger.info(f"Measurement name: {self.name}")
        else:
            logger.warning("Measurement name is missing.")

        if self.instruments:
            logger.info(f"Instruments used: {self.instruments}")
        else:
            logger.warning("Instruments are not specified.")

        if self.samples:
            logger.info(f"Samples used: {self.samples}")
        else:
            logger.warning("Samples are not specified.")

        if self.results:
            logger.info(f"Number of results: {len(self.results)}")
            for result in self.results:
                result.normalize(archive, logger)
        else:
            logger.warning("No results found in the measurement.")
