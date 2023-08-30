import os
import pickle as pkl
import warnings

import pandas as pd

"""
Author: Chris Magnano
02/15/21

Methods and intermediate state for loading data and putting it into pandas tables for use by pathway reconstruction algorithms.
"""

class Dataset:

    NODE_ID = "NODEID"
    warning_threshold = 0.05  # Threshold for scarcity of columns to warn user

    def __init__(self, dataset_dict):
        self.label = None
        self.interactome = None
        self.node_table = None
        self.edge_table = None
        self.node_set = set()
        self.other_files = []
        self.load_files_from_dict(dataset_dict)
        return

    def to_file(self, file_name):
        """
        Saves dataset object to pickle file
        """
        with open(file_name, "wb") as f:
            pkl.dump(self, f)

    @classmethod
    def from_file(cls, file_name):
        """
        Loads dataset object from a pickle file.
        Usage: dataset = Dataset.from_file(pickle_file)
        """
        with open(file_name, "rb") as f:
            return pkl.load(f)

    def load_files_from_dict(self, dataset_dict):
        """
        Loads data files from dataset_dict, which is one dataset dictionary from the list
        in the config file with the fields in the config file.
        Populates node_table, edge_table, and interactome.

        node_table is a single merged pandas table.

        When loading data files, files of only a single column with node
        identifiers are assumed to be a binary feature where all listed nodes are
        True.

        We might want to eventually add an additional "algs" argument so only
        subsets of the entire config file are loaded, alternatively this could
        be handled outside this class.

        returns: none
        """

        self.label = dataset_dict["label"]

        # Get file paths from config
        # TODO support multiple edge files
        interactome_loc = dataset_dict["edge_files"][0]
        node_data_files = dataset_dict["node_files"]
        # edge_data_files = [""]  # Currently None
        data_loc = dataset_dict["data_dir"]

        # Load everything as pandas tables
        print("about to create self.interactome")
        print(data_loc)
        print(interactome_loc)

        with open(os.path.join(data_loc, interactome_loc), "r") as f:
            for _i in range(9):  # first 5 lines
                print(f.readline())

        self.interactome = pd.read_table(
            os.path.join(data_loc, interactome_loc), sep="\t", header=None
        )
        print(self.interactome)
        num_cols = self.interactome.shape[1]
        print(num_cols)
        if num_cols == 3:

            self.interactome.columns = ["Interactor1", "Interactor2", "Weight"]
            self.interactome["Direction"] = "U"

        elif num_cols == 4:
            self.interactome.columns = [
                "Interactor1",
                "Interactor2",
                "Weight",
                "Direction",
            ]
        else:
            raise ValueError(
                f"edge_files must have three or four columns but found {num_cols}"
            )

        node_set = set(self.interactome.Interactor1.unique())
        node_set = node_set.union(set(self.interactome.Interactor2.unique()))

        # Load generic node tables
        self.node_table = pd.DataFrame(node_set, columns=[self.NODE_ID])
        for node_file in node_data_files:
            single_node_table = pd.read_table(os.path.join(data_loc, node_file))
            # If we have only 1 column, assume this is an indicator variable
            if len(single_node_table.columns) == 1:
                single_node_table = pd.read_table(
                    os.path.join(data_loc, node_file), header=None
                )
                single_node_table.columns = [self.NODE_ID]
                new_col_name = node_file.split(".")[0]
                single_node_table[new_col_name] = True

            # Use only keys from the existing node table so that nodes that are not in the interactome are ignored
            # If there duplicate columns, keep the existing column and add the suffix '_DROP' to the new column so it
            # will be ignored
            # TODO may want to warn about duplicate before removing them, for instance, if a user loads two files that
            #  both have prizes
            self.node_table = self.node_table.merge(
                single_node_table, how="left", on=self.NODE_ID, suffixes=(None, "_DROP")
            ).filter(regex="^(?!.*DROP)")
        # Ensure that the NODEID column always appears first, which is required for some downstream analyses
        self.node_table.insert(0, "NODEID", self.node_table.pop("NODEID"))
        self.other_files = dataset_dict["other_files"]

    def request_node_columns(self, col_names):
        """
        returns: A table containing the requested column names and node IDs
        for all nodes with at least 1 of the requested values being non-empty
        """
        col_names.append(self.NODE_ID)
        filtered_table = self.node_table[col_names]
        filtered_table = filtered_table.dropna(
            axis=0, how="all", subset=filtered_table.columns.difference([self.NODE_ID])
        )
        percent_hit = (float(len(filtered_table)) / len(self.node_table)) * 100
        if percent_hit <= self.warning_threshold * 100:
            # Only use stacklevel 1 because this is due to the data not the code context
            warnings.warn(
                "Only %0.2f of data had one or more of the following columns filled:"
                % (percent_hit)
                + str(col_names),
                stacklevel=1,
            )
        return filtered_table

    def contains_node_columns(self, col_names):
        """
        col_names: A list-like object of column names to check or a string of a single column name to check.
        returns: Whether or not all columns in col_names exist in the dataset.
        """
        if isinstance(col_names, str):
            return col_names in self.node_table.columns
        else:
            for c in col_names:
                if c not in self.node_table.columns:
                    return False
                return True

    def request_edge_columns(self, col_names):
        return None

    def get_other_files(self):
        return self.other_files.copy()

    def get_interactome(self):
        return self.interactome.copy()

def convert_undirected_to_directed(df: pd.DataFrame) -> pd.DataFrame:
    """
    turns a graph into a fully directed graph
    - turns every unidirected edges into a bi-directed edge
    - with bi-directed edges, we are not loosing too much information because the relationship of the undirected egde is still preserved

   *A user must keep the Direction column when using this function

    @param df: input network df of edges, weights, and directionality
    @return a dataframe with no undirected edges in Direction column
    """

    # TODO: add a check to make sure there is a direction column in df

    for index, row in df.iterrows():
        if row["Direction"] == "U":
            df.at[index, "Direction"] = "D"

            new_directed_row = row.copy(deep=True)
            new_directed_row["Interactor1"], new_directed_row["Interactor2"] = (
                row["Interactor2"],
                row["Interactor1"],
            )
            print("new directed row\n", new_directed_row)
            new_directed_row["Direction"] = "D"
            df.loc[len(df)] = new_directed_row

    return df


def convert_directed_to_undirected(df: pd.DataFrame) -> pd.DateOffset:
    """
    turns a graph into a fully undirected graph
    - turns the directed edges directly into undirected edges
    - we will loose any sense of directionality and the graph won't be inherently accurate, but the basic relationship between the two connected nodes will still remain intact.

    @param df: input network df of edges, weights, and directionality
    @return a dataframe with no directed edges in Direction column
    """

    for index, row in df.iterrows():
        if row["Direction"] == "D":
            df.at[index, "Direction"] = "U"

    return df


def add_seperator(df: pd.DataFrame, col_loc: int, col_name: str, sep: str) -> pd.DataFrame:
    """
    adds a seperator somewhere into the input dataframe

    @param df: input network df of edges, weights, and directionality
    @param col_loc: the spot in the dataframe to put the new column
    @param col_name: the name of the new column
    @param sep: some type of seperator needed in the df
    @return a df with a new seperator added to every row
    """

    df.insert(col_loc, col_name, sep)
    return df


def add_directionality_seperators(df: pd.DataFrame, col_loc: int, col_name: str, dir_sep: str, undir_sep: str) -> pd.DataFrame:
    """
    deals with adding in directionality seperators for mixed graphs that isn't in the universal input

    *user must keep the Direction column when using the function

    @param df: input network df of edges, weights, and directionality
    @param col_loc: the spot in the dataframe to put the new column
    @param col_name: the name of the new column
    @param dir_sep: the directed edge sep
    @param undir_sep: the undirected edge sep
    @return a df converted to show directionality differently
    """

    # TODO: add a check to make sure there is a direction column in df

    df.insert(col_loc, col_name, dir_sep)

    for index, row in df.iterrows():
        if row["Direction"] == "U":
            df.at[index, col_name] = undir_sep
        elif row["Direction"] == "D":
            continue
        else:
            raise ValueError(
                f'direction must be a \'U\' or \'D\', but found {row["Direction"]}'
            )

    return df

def readd_direction_col_mixed(df: pd.DataFrame, direction_col_loc: int, existing_direction_column: str, dir_sep: str, undir_sep: str) -> pd.DataFrame:
    """
    readds a 'Direction' column that puts a 'U' or 'D' based on the dir/undir seperators in the existing direction column

    *user must keep the existing direction column when using the function

    @param df: input network df that contains directionality
    @param direction_col_loc: the spot in the dataframe to put back the 'Direction' column
    @param existing_direction_column: the name of the existing directionality column
    @param dir_sep: the directed edge sep
    @param undir_sep: the undirected edge sep
    @return a df with Direction column added back
    """

    df.insert(direction_col_loc, "Direction", "D")

    for index, row in df.iterrows():
        if row[existing_direction_column] == undir_sep:
            df.at[index, "Direction"] = "U"

        elif row[existing_direction_column] == dir_sep:
            df.at[index, "Direction"] = "D"

        else:
            raise ValueError(
                f'direction must be a \'{dir_sep}\' or \'{undir_sep}\', but found {row[existing_direction_column]}'
            )

    return df

def readd_direction_col_undirected(df: pd.DataFrame, direction_col_loc: int) -> pd.DataFrame:
    """
    readds a 'Direction' column that puts a 'U'

    @param df: input network df that contains directionality
    @param direction_col_loc: the spot in the dataframe to put back the 'Direction' column
    @return a df with Direction column added back
    """
    df.insert(direction_col_loc, "Direction", "U")
    return df

def readd_direction_col_directed(df: pd.DataFrame, direction_col_loc: int) -> pd.DataFrame:
    """
    readds a 'Direction' column that puts a 'D'

    @param df: input network df that contains directionality
    @param direction_col_loc: the spot in the dataframe to put back the 'Direction' column
    @return a df with Direction column added back
    """
    df.insert(direction_col_loc, "Direction", "D")
    return df
