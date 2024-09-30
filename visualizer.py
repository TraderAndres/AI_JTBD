# visualizer.py
import pandas as pd
import streamlit as st

from streamlit_tree_select import tree_select
from st_aggrid import AgGrid
from anytree import Node, PreOrderIter
from rich.console import Console
from rich.tree import Tree as RichTree

class Visualizer:
    def display_hierarchy(self, root):
        def build_dataframe(node, path=""):
            current_path = f"{path}/{node.name}" if path else node.name
            # Use getattr to safely access 'description'
            description = getattr(node, 'description', 'No description available')
            data = {"Job Path": current_path, "Description": description}
            df = pd.DataFrame([data])
            for child in node.children:
                df = pd.concat([df, build_dataframe(child, current_path)], ignore_index=True)
            return df

        df = build_dataframe(root)
        grid_response = AgGrid(
            df,
            editable=False,
            height=500,
            fit_columns_on_grid_load=True,
            theme='streamlit',
            allow_unsafe_jscode=True,
            columns_auto_size_mode='FIT_CONTENTS',
        )
        selected = grid_response['selected_rows']
        if selected:
            st.write(f"You selected: {selected}")

# class Visualizer:
#     def display_hierarchy(self, root):
#         console = Console()
#         rich_tree = self._convert_to_rich_tree(root)
#         console.print(rich_tree)

#     def _convert_to_rich_tree(self, node):
#         rich_node = RichTree(f"{node.name}")
#         for child in node.children:
#             child_rich = self._convert_to_rich_tree(child)
#             rich_node.add(child_rich)
#         return rich_node
