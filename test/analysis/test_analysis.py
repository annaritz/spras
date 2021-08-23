import pytest
from pathlib import Path
import os
import src.analysis.summary.summary as summary
import src.analysis.viz.graphspace as graphspace
import src.analysis.precrec.precrec as precrec
import Dataset

TEST_DIR = 'test/analysis/'

class TestAnalysis:
    """
    Test the summary statistics
    """
    # test a ranked file of ints (1 - 10)
    def test_summary_ranked_ints(self):
        summary.run(TEST_DIR+'input/standardized-ranked.txt',TEST_DIR+'output/standardized-ranked-out.txt')

    # test a ranked file of floats (1.0 - 10.0)
    def test_summary_ranked_floats(self):
        summary.run(TEST_DIR+'input/standardized-ranked-floats.txt',TEST_DIR+'output/standardized-ranked-floats-out.txt')

    # test an unranked file (all ranks are 1)
    def test_summary_unranked(self):
        summary.run(TEST_DIR+'input/standardized-unranked.txt',TEST_DIR+'output/standardized-unranked-out.txt')

    # test a ranked file interpreted as a directed network (e.g. uses nx.DiGraph).
    def test_summary_directed(self):
        summary.run(TEST_DIR+'input/standardized-ranked.txt',TEST_DIR+'output/standardized-ranked-directed-out.txt',directed=True)

    # test GraphSpace json output on an undirected graph.
    def test_graphspace_ranked(self):
        graphspace.write_json(TEST_DIR+'input/standardized-ranked.txt',TEST_DIR+'output/standardized-ranked-undirected-gs.json',TEST_DIR+'output/standardized-ranked-undirected-gs-style.json')

    # test GraphSpace json output on a directed graph.
    def test_graphspace_ranked_directed(self):
        graphspace.write_json(TEST_DIR+'input/standardized-ranked.txt',TEST_DIR+'output/standardized-ranked-directed-gs.json',TEST_DIR+'output/standardized-ranked-directed-gs-style.json',directed=True)

    def test_precrec_nodes_1(self):
        dataset_dict = {'label': 'wnt', 'node_files': ['sources.wnt.txt', 'targets.wnt.txt'], 'edge_files': ['np-union.txt'], 'other_files': [], 'ground_truth_files': ['wnt-edges.txt', 'wnt-nodes.txt'], 'data_dir': TEST_DIR+'input/wnt/'}

        # make output directory if it doesn't exist:
        outdir = TEST_DIR+'output/wnt/'
        if not os.path.isdir(outdir):
            print('making output directory.... %s' % (outdir))
            os.makedirs(outdir)

        # compute_precrec(infiles:list,data:Dataset, gt_header:string, outprefix:string,subsample:string)
        infiles = [TEST_DIR+'input/wnt/pathway-wnt-pathlinker-params0.txt',TEST_DIR+'input/wnt/pathway-wnt-pathlinker-params1.txt',TEST_DIR+'input/wnt/pathway-wnt-omicsintegrator2-params0.txt',TEST_DIR+'input/wnt/pathway-wnt-manual-params0.txt',TEST_DIR+'input/wnt/pathway-wnt-manual2-params0.txt']
        outfiles = [TEST_DIR+'output/wnt/precrec-pathway-wnt-pathlinker-params0.txt',TEST_DIR+'output/wnt/precrec-pathway-wnt-pathlinker-params1.txt',TEST_DIR+'output/wnt/precrec-pathway-wnt-omicsintegrator2-params0.txt',TEST_DIR+'output/wnt/precrec-pathway-wnt-manual-params0.txt',TEST_DIR+'output/wnt/precrec-pathway-wnt-manual2-params0.txt']
        data = Dataset.Dataset(dataset_dict)
        gt_header = 'wnt-nodes'
        outprefix=TEST_DIR+'output/wnt-nodes-2x'
        subsample='2'
        precrec.compute_precrec(infiles,outfiles,data,gt_header,outprefix,subsample)

    def test_precrec_nodes_2(self):
        dataset_dict = {'label': 'wnt', 'node_files': ['sources.wnt.txt', 'targets.wnt.txt'], 'edge_files': ['np-union.txt'], 'other_files': [], 'ground_truth_files': ['wnt-edges.txt', 'wnt-nodes.txt'], 'data_dir': TEST_DIR+'input/wnt/'}

        # make output directory if it doesn't exist:
        outdir = TEST_DIR+'output/wnt/'
        if not os.path.isdir(outdir):
            print('making output directory.... %s' % (outdir))
            os.makedirs(outdir)

        # compute_precrec(infiles:list,data:Dataset, gt_header:string, outprefix:string,subsample:string)
        infiles = [TEST_DIR+'input/wnt/pathway-wnt-pathlinker-params0.txt',TEST_DIR+'input/wnt/pathway-wnt-pathlinker-params1.txt',TEST_DIR+'input/wnt/pathway-wnt-omicsintegrator2-params0.txt',TEST_DIR+'input/wnt/pathway-wnt-manual-params0.txt',TEST_DIR+'input/wnt/pathway-wnt-manual2-params0.txt']
        outfiles = [TEST_DIR+'output/wnt/precrec-pathway-wnt-pathlinker-params0.txt',TEST_DIR+'output/wnt/precrec-pathway-wnt-pathlinker-params1.txt',TEST_DIR+'output/wnt/precrec-pathway-wnt-omicsintegrator2-params0.txt',TEST_DIR+'output/wnt/precrec-pathway-wnt-manual-params0.txt',TEST_DIR+'output/wnt/precrec-pathway-wnt-manual2-params0.txt']
        data = Dataset.Dataset(dataset_dict)
        gt_header = 'wnt-nodes'
        outprefix=TEST_DIR+'output/wnt-nodes-all'
        subsample='all'
        precrec.compute_precrec(infiles,outfiles,data,gt_header,outprefix,subsample)
