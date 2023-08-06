#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cellmaps_ppi_embedding` package."""

import os
import unittest
import tempfile
import shutil
import csv
from cellmaps_ppi_embedding.runner import CellMapsPPIEmbedder
from cellmaps_ppi_embedding.runner import Node2VecEmbeddingGenerator
from cellmaps_ppi_embedding.exceptions import CellMapsPPIEmbeddingError


class TestCellmapsNetworkEmbeddingRunner(unittest.TestCase):
    """Tests for `cellmaps_ppi_embedding` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_constructor(self):
        """Tests constructor"""
        temp_dir = tempfile.mkdtemp()
        try:
            myobj = CellMapsPPIEmbedder(outdir=os.path.join(temp_dir,
                                                                       'out'))
            self.assertIsNotNone(myobj)
        finally:
            shutil.rmtree(temp_dir)

    def test_constructor_no_outdir(self):
        """ Tests run()"""
        try:
            myobj = CellMapsPPIEmbedder()
            self.fail('Expected exception')
        except CellMapsPPIEmbeddingError as ce:
            self.assertEqual('outdir is None', str(ce))

    def test_run_no_edgelist(self):
        temp_dir = tempfile.mkdtemp()
        try:
            rundir = os.path.join(temp_dir, 'run')
            gen = Node2VecEmbeddingGenerator(None)
            myobj = CellMapsPPIEmbedder(outdir=rundir,
                                        embedding_generator=gen)
            myobj.run()
            self.fail('Expected exception')
        except CellMapsPPIEmbeddingError as ce:
            self.assertEqual('network is None', str(ce))
        finally:
            shutil.rmtree(temp_dir)

    @unittest.skip('Need to refactor to match code changes')
    def test_run_success(self):
        try:
            temp_dir = tempfile.mkdtemp()
            e_file = os.path.join(temp_dir, 'edgelist.tsv')
            with open(e_file, 'w') as f:
                f.write('geneA\tgeneB\n')
                f.write('ABC\tDEF\n')
            myobj = CellMapsPPIEmbedder(outdir=temp_dir,
                                        edgelist=e_file)
            self.assertEqual(0, myobj.run())
            apms_emd = os.path.join(temp_dir, 'apms_emd.tsv')
            self.assertTrue(os.path.isfile(apms_emd))
            with open(apms_emd, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                resmap = {}
                for row in reader:
                    resmap[row[0]] = row[1:]

                for g in ['ABC', 'DEF']:
                    self.assertTrue(g in resmap)
                    self.assertEqual(1024, len(resmap[g]))
        finally:
            shutil.rmtree(temp_dir)
