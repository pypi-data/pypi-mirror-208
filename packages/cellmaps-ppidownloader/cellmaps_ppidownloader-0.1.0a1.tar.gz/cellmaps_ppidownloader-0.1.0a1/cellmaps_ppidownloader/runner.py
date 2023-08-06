#! /usr/bin/env python

import os
from multiprocessing import Pool
import re
import csv
import subprocess
import logging
import logging.config
import requests
import time
from datetime import date
import json
from tqdm import tqdm
from cellmaps_utils import logutils
from cellmaps_utils import constants
from cellmaps_utils.provenance import ProvenanceUtil
import cellmaps_ppidownloader
from cellmaps_ppidownloader.exceptions import CellMapsPPIDownloaderError

logger = logging.getLogger(__name__)


class CellmapsPPIDownloader(object):
    """
    Class to run algorithm
    """

    EDGELIST_FILEKEY = 'edgelist'
    BAITLIST_FILEKEY = 'baitlist'

    def __init__(self, outdir=None,
                 imgsuffix='.jpg',
                 apmsgen=None,
                 skip_logging=False,
                 provenance=None,
                 input_data_dict=None,
                 provenance_utils=ProvenanceUtil(),
                 skip_failed=False):
        """
        Constructor

        :param outdir: directory where images will be downloaded to
        :type outdir: str
        :param apmsgen: gene node attribute generator for APMS data
        :type apmsgen: :py:class:`~cellmaps_downloader.gene.APMSGeneNodeAttributeGenerator`
        :param skip_logging:
        :type skip_logging: bool
        :param provenance:
        :type provenance: dict
        :param input_data_dict:
        :type input_data_dict: dict
        """
        if outdir is None:
            raise CellMapsPPIDownloaderError('outdir is None')
        self._outdir = os.path.abspath(outdir)
        self._imgsuffix = imgsuffix
        self._start_time = int(time.time())
        self._end_time = -1
        self._apmsgen = apmsgen
        self._provenance = provenance
        self._input_data_dict = input_data_dict
        if skip_logging is None:
            self._skip_logging = False
        else:
            self._skip_logging = skip_logging
        self._edgelist_datasetid = None
        self._baitlist_datasetid = None
        self._softwareid = None
        self._apms_gene_attrid = None
        self._provenance_utils = provenance_utils
        self.skip_failed = skip_failed

    @staticmethod
    def get_example_provenance(requiredonly=True,
                               with_ids=False):
        """
        Gets a dict of provenance parameters needed to add/register
        a dataset with FAIRSCAPE

        :param requiredonly: If ``True`` only output required fields,
                             otherwise output all fields. This value
                             is ignored if **with_ids** is ``True``
        :type requiredonly: bool
        :param with_ids: If ``True`` only output the fields
                         to set dataset guids and ignore value of
                         **requiredonly** parameter.
        :type with_ids: bool
        :return:
        """
        base_dict = {'name': 'Name for pipeline run',
                     'organization-name': 'Name of organization',
                     'project-name': 'Name of project'}
        if with_ids is not None and with_ids is True:
            guid_dict = ProvenanceUtil.example_dataset_provenance(with_ids=with_ids)
            base_dict.update({CellmapsPPIDownloader.EDGELIST_FILEKEY: guid_dict,
                              CellmapsPPIDownloader.BAITLIST_FILEKEY: guid_dict})
            return base_dict

        field_dict = ProvenanceUtil.example_dataset_provenance(requiredonly=requiredonly)

        base_dict.update({CellmapsPPIDownloader.EDGELIST_FILEKEY: field_dict,
                          CellmapsPPIDownloader.BAITLIST_FILEKEY: field_dict})
        return base_dict

    def _create_output_directory(self):
        """
        Creates output directory if it does not already exist

        :raises CellmapsDownloaderError: If output directory is None or if directory already exists
        """
        if os.path.isdir(self._outdir):
            raise CellMapsPPIDownloaderError(self._outdir + ' already exists')

        os.makedirs(self._outdir, mode=0o755)

    def _register_software(self):
        """
        Registers this tool

        :raises CellMapsProvenanceError: If fairscape call fails
        """
        self._softwareid = self._provenance_utils.register_software(self._outdir,
                                                                    name=cellmaps_ppidownloader.__name__,
                                                                    description=cellmaps_ppidownloader.__description__,
                                                                    author=cellmaps_ppidownloader.__author__,
                                                                    version=cellmaps_ppidownloader.__version__,
                                                                    file_format='.py',
                                                                    url=cellmaps_ppidownloader.__repo_url__)

    def _register_apms_gene_node_attrs(self):
        """
        Registers image_gene_node_attributes.tsv file with create as a dataset

        """
        data_dict = {'name': cellmaps_ppidownloader.__name__ + ' output file',
                     'description': 'APMS gene node attributes file',
                     'data-format': 'tsv',
                     'author': '',
                     'version': cellmaps_ppidownloader.__version__,
                     'date-published': date.today().strftime('%m-%d-%Y')}
        self._apms_gene_attrid = self._provenance_utils.register_dataset(self._outdir,
                                                                         source_file=self.get_ppi_gene_node_attributes_file(),
                                                                         data_dict=data_dict)

    def _add_dataset_to_crate(self, data_dict=None,
                              source_file=None, skip_copy=True):
        """

        :param crate_path:
        :param data_dict:
        :return:
        """
        return self._provenance_utils.register_dataset(self._outdir,
                                                       source_file=source_file,
                                                       data_dict=data_dict,
                                                       skip_copy=skip_copy)

    def _register_computation(self):
        """

        :return:
        """
        self._provenance_utils.register_computation(self._outdir,
                                                    name=cellmaps_ppidownloader.__name__ + ' computation',
                                                    run_by=str(os.getlogin()),
                                                    command=str(self._input_data_dict),
                                                    description='run of ' + cellmaps_ppidownloader.__name__,
                                                    used_software=[self._softwareid],
                                                    used_dataset=[self._baitlist_datasetid, self._edgelist_datasetid],
                                                    generated=[self._apms_gene_attrid])

    def _create_rocrate(self):
        """
        Creates rocrate for output directory

        :raises CellMapsProvenanceError: If there is an error
        """
        try:
            self._provenance_utils.register_rocrate(self._outdir,
                                                    name=self._provenance['name'],
                                                    organization_name=self._provenance['organization-name'],
                                                    project_name=self._provenance['project-name'])
        except TypeError as te:
            raise CellMapsPPIDownloaderError('Invalid provenance: ' + str(te))
        except KeyError as ke:
            raise CellMapsPPIDownloaderError('Key missing in provenance: ' + str(ke))

    def _register_input_datasets(self):
        """
        Registers samples and unique input datasets with FAIRSCAPE
        setting **self._edgelist_datasetid** and **self._baitlist_datasetid**
        values.

        :return:
        """

        if 'guid' in self._provenance[CellmapsPPIDownloader.EDGELIST_FILEKEY]:
            self._edgelist_datasetid = self._provenance[CellmapsPPIDownloader.EDGELIST_FILEKEY]['guid']
        if 'guid' in self._provenance[CellmapsPPIDownloader.BAITLIST_FILEKEY]:
            self._baitlist_datasetid = self._provenance[CellmapsPPIDownloader.BAITLIST_FILEKEY]['guid']

        if self._edgelist_datasetid is not None and self._baitlist_datasetid is not None:
            logger.debug('Both edgelist and baitlist have dataset ids. Just returning')
            return

        if self._edgelist_datasetid is None:
            # write file and add samples dataset
            self._edgelist_datasetid = self._add_dataset_to_crate(data_dict=self._provenance[CellmapsPPIDownloader.EDGELIST_FILEKEY],
                                                                  source_file=self._input_data_dict[CellmapsPPIDownloader.EDGELIST_FILEKEY],
                                                                  skip_copy=False)
            logger.debug('Edgelist dataset id: ' + str(self._edgelist_datasetid))

        if self._baitlist_datasetid is None:
            # write file and add unique dataset
            self._baitlist_datasetid = self._add_dataset_to_crate(data_dict=self._provenance[CellmapsPPIDownloader.BAITLIST_FILEKEY],
                                                                  source_file=self._input_data_dict[CellmapsPPIDownloader.BAITLIST_FILEKEY],
                                                                  skip_copy=False)
            logger.debug('Baitlist dataset id: ' + str(self._baitlist_datasetid))

    def _write_task_start_json(self):
        """
        Writes task_start.json file with information about
        what is to be run

        """
        data = {}

        if self._input_data_dict is not None:
            data.update({'commandlineargs': self._input_data_dict})

        logutils.write_task_start_json(outdir=self._outdir,
                                       start_time=self._start_time,
                                       version=cellmaps_ppidownloader.__version__,
                                       data=data)

    def get_ppi_gene_node_attributes_file(self):
        """
        Gets full path to ppi gene node attribute file under output directory
        created when invoking :py:meth:`~cellmaps_downloader.runner.CellmapsPPIDownloader.run`

        :return: Path to file
        :rtype: str
        """
        return os.path.join(self._outdir,
                            constants.PPI_GENE_NODE_ATTR_FILE)

    def get_ppi_gene_node_errors_file(self):
        """
        Gets full path to ppi gene node attribute errors file under output directory
        created when invoking :py:meth:`~cellmaps_downloader.runner.CellmapsPPIDownloader.run`

        :return: Path to file
        :rtype: str
        """
        return os.path.join(self._outdir,
                            constants.PPI_GENE_NODE_ERRORS_FILE)

    def _write_ppi_gene_node_attrs(self, gene_node_attrs=None,
                                   errors=None):
        """

        :param gene_node_attrs:
        :param errors:
        :return:
        """
        with open(self.get_ppi_gene_node_attributes_file(), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=constants.PPI_GENE_NODE_COLS, delimiter='\t')

            writer.writeheader()
            for key in gene_node_attrs:
                writer.writerow(gene_node_attrs[key])

        if errors is not None:
            with open(self.get_ppi_gene_node_errors_file(), 'w') as f:
                for e in errors:
                    f.write(str(e) + '\n')

    def get_ppi_edgelist_file(self):
        """

        :return:
        """
        return os.path.join(self._outdir,
                            constants.PPI_EDGELIST_FILE)

    def _write_ppi_network(self, edgelist=None,
                           gene_node_attrs=None):
        """

        :param edgelist:
        :param gene_node_attrs:
        :return:
        """
        with open(self.get_ppi_edgelist_file(), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=constants.PPI_EDGELIST_COLS, delimiter='\t')
            writer.writeheader()
            for edge in edgelist:
                if edge['GeneID1'] not in gene_node_attrs:
                    logger.error('Skipping ' + str(edge['GeneID1'] + ' cause it lacks a symbol'))
                    continue
                if edge['GeneID2'] not in gene_node_attrs:
                    logger.error('Skipping ' + str(edge['GeneID2'] + ' cause it lacks a symbol'))
                    continue

                genea = gene_node_attrs[edge['GeneID1']]['name']
                geneb = gene_node_attrs[edge['GeneID2']]['name']
                if genea is None or geneb is None:
                    logger.error('Skipping edge cause no symbol is found: ' + str(edge))
                    continue
                if len(genea) == 0 or len(geneb) == 0:
                    logger.error('Skipping edge cause no symbol is found: ' + str(edge))
                    continue
                writer.writerow({constants.PPI_EDGELIST_COLS[0]: genea,
                                 constants.PPI_EDGELIST_COLS[1]: geneb})

    def run(self):
        """
        Downloads ppi data to output directory specified in constructor

        :raises CellMapsPPIDownloaderError: If there is an error
        :return: 0 upon success, otherwise failure
        """
        try:
            exitcode = 99
            self._create_output_directory()
            if self._skip_logging is False:
                logutils.setup_filelogger(outdir=self._outdir,
                                          handlerprefix='cellmaps_ppidownloader')
                self._write_task_start_json()

            self._create_rocrate()
            self._register_input_datasets()

            self._register_software()

            gene_node_attrs, errors = self._apmsgen.get_gene_node_attributes()

            # write apms attribute data
            self._write_ppi_gene_node_attrs(gene_node_attrs, errors)

            # write apms network
            self._write_ppi_network(edgelist=self._apmsgen.get_apms_edgelist(),
                                    gene_node_attrs=gene_node_attrs)

            self._register_apms_gene_node_attrs()

            self._register_computation()
            exitcode = 0
            return exitcode
        finally:
            self._end_time = int(time.time())
            if self._skip_logging is False:
                # write a task finish file
                logutils.write_task_finish_json(outdir=self._outdir,
                                                start_time=self._start_time,
                                                end_time=self._end_time,
                                                status=exitcode)
