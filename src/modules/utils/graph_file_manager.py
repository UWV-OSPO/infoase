import os
import pickle
import hashlib
from datetime import datetime
import pandas as pd
from modules.utils import Utilities


class GraphFileManager:
    def __init__(self, username: str, directory: str = "data/saved_graphs") -> None:
        """
        Initializes the GraphFileManager object.

        Args:
            directory (str): The directory where the graphs will be saved.
                             Defaults to "data/saved_graphs".
        """
        self.username = username
        self.directory = f"{Utilities.persistent_storage_path()}/{directory}"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def _generate_hash(self, graph) -> str:
        """
        Generates a hash for the given graph object.

        Args:
            graph (object): The graph object to generate the hash for.

        Returns:
            str: The hash value as a string.
        """
        return hashlib.md5(pickle.dumps(graph)).hexdigest()

    def save_graph_file(self, graph: object, db_name: str, description: str) -> str:
        """
        Saves the given graph object to a pickle file.

        Args:
            graph (object): The graph object to be saved.
            description (str): A description of the graph.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        graph_hash = self._generate_hash(graph)
        info_path = os.path.join(self.directory, "info.csv")

        # Check if graph is already saved
        if os.path.exists(info_path):
            df = pd.read_csv(info_path)
            if graph_hash in df["Hash"].values:
                return "Graph not saved, you're trying to save a duplicate."

        # Save the graph
        username = self.username
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{db_name}_{username}.pkl"
        filepath = os.path.join(self.directory, filename)
        with open(filepath, "wb") as file:
            pickle.dump(graph, file)

        # Save description, hash, and timestamp
        new_row = pd.DataFrame(
            [
                [
                    filename,
                    username,
                    db_name,
                    description,
                    graph_hash,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            ],
            columns=[
                "Bestandsnaam",
                "Eigenaar",
                "Instance",
                "Opmerking",
                "Hash",
                "Opgeslagen op",
            ],
        )
        if os.path.exists(info_path):
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = new_row

        df.to_csv(info_path, index=False)
        return "Graph opgeslagen."

    def delete_graph_file(self, filename: str) -> None:
        """
        Deletes the pickle file and updates the info.csv file.

        Args:
            filename (str): The name of the file to be deleted.
        """
        # Delete the pickle file
        filepath = os.path.join(self.directory, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        # Update the info.csv file
        info_path = os.path.join(self.directory, "info.csv")
        if os.path.exists(info_path):
            df = pd.read_csv(info_path)
            df = df[df["Bestandsnaam"] != filename]
            df.to_csv(info_path, index=False)

    def unpickle_graph(self, filename: str) -> object:
        """
        Unpickles a graph object from a given file.

        Args:
            filename (str): The name of the file to unpickle the graph from.

        Returns:
            object: The unpickled graph object.
        """
        filepath = os.path.join(self.directory, filename)
        with open(filepath, "rb") as file:
            graph = pickle.load(file)
        return graph

    def saved_graphs_df(self) -> pd.DataFrame:
        """
        Retrieves the information about the saved graphs from the info.csv file.

        :return: A DataFrame containing the information about the saved graphs.
        """
        info_path = os.path.join(self.directory, "info.csv")
        if os.path.exists(info_path):
            return pd.read_csv(info_path)
        return pd.DataFrame(
            columns=["Bestandsnaam", "Eigenaar", "Opmerking", "Opgeslagen op"]
        )
