import warnings
from pathlib import Path

from spras.config.container_schema import ProcessedContainerSettings
from spras.config.util import Empty
from spras.containers import prepare_volume, run_container_and_log
from spras.dataset import Dataset
from spras.interactome import (
    convert_undirected_to_directed,
    has_direction,
    reinsert_direction_col_undirected,
)
from spras.prm import PRM
from spras.util import add_rank_column, duplicate_edges, raw_pathway_df

__all__ = ['LocalNeighborhood']

class LocalNeighborhood(PRM[Empty]):
    """
    LocalNeighborhood requires a single-column node file and an undirected network file with a pipe delimiter (e.g., 'A|B').
    LocalNeighborhood outputs an undirected network file with a pipe delimiter (e.g., 'A|B').
    """
    required_inputs = ['nodes', 'network']
    dois = []

    @staticmethod
    def generate_inputs(data, filename_map):
        """
        Access fields from the dataset and write the required input files
        @param data: dataset
        @param filename_map: a dict mapping file types in the required_inputs to the filename for that type. Associated files will be written with:
        - nodes: single-column list of nodes.
        - network: two-column edge list with a pipe (|) delimiter.
        """
        LocalNeighborhood.validate_required_inputs(filename_map)

        # Get all nodes with any prize, whether it's active, whether it's a source. 
        # NODEID is always included in the node table
        if data.contains_node_columns(['prize','active','sources', 'targets']):
            node_df = data.get_node_columns(['prize','active','sources', 'targets'])
        else:
            raise MissingDataError("(node prizes) or (sources and targets)")

        # generate a single-column file of nodes with no header.
        node_df.to_csv(filename_map['nodes'],index=False,columns=['NODEID'],header=False)

        # Get network file
        edges_df = data.get_interactome()

        # genereate pipe-delimited network file with no header.
        edges_df.to_csv(filename_map['network'],sep='|',index=False,columns=['Interactor1','Interactor2'],header=False)

    @staticmethod
    def run(inputs, output_file, args=None, container_settings=None):
        if not container_settings: container_settings = ProcessedContainerSettings()
        LocalNeighborhood.validate_required_run_args(inputs)

        work_dir = '/LocalNeighborhood'

        # Each volume is a tuple (src, dest)
        volumes = list()

        # add the input node file
        bind_path, node_file = prepare_volume(inputs["nodes"], work_dir, container_settings)
        volumes.append(bind_path)

        # add the network file
        bind_path, network_file = prepare_volume(inputs["network"], work_dir, container_settings)
        volumes.append(bind_path)

        # Specify the output directory
        out_dir = Path(output_file).parent

        # add the output file
        bind_path, mapped_out_file = prepare_volume(output_file, work_dir, container_settings)
        volumes.append(bind_path)

        command = ['python',
                   '/LocalNeighborhood/local_neighborhood_alg.py',
                   '--network', network_file,
                   '--nodes', node_file,
                   '--output', mapped_out_file]

        container_suffix = "local-neighborhood"
        run_container_and_log(
            'Local Neighborhood',
            container_suffix,
            command,
            volumes,
            work_dir,
            out_dir,
            container_settings)

    @staticmethod
    def parse_output(raw_pathway_file, standardized_pathway_file, params):
        """
        Convert a predicted pathway into the universal format
        @param raw_pathway_file: pathway file produced by an algorithm's run function (pipe-delimited output) 
        @param standardized_pathway_file: the same pathway written in the universal format
        """
        df = raw_pathway_df(raw_pathway_file, sep='|', header=None)
        if not df.empty:
            df = add_rank_column(df)
            df = reinsert_direction_col_undirected(df)
            df.columns = ['Node1', 'Node2', 'Rank', 'Direction']
            df, has_duplicates = duplicate_edges(df)
            if has_duplicates:
                print(f"Duplicate edges were removed from {raw_pathway_file}")
        df.to_csv(standardized_pathway_file, header=True, index=False, sep='\t')
