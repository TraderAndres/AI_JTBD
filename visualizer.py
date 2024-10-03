# visualizer.py
import streamlit as st
from anytree import PreOrderIter
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd

class Visualizer:
    def prepare_dataframe(self, root):
        """
        Converts the AnyTree structure into a Pandas DataFrame suitable for AgGrid.
        """
        data = []
        for node in PreOrderIter(root):
            path = " / ".join([ancestor.name for ancestor in node.path])
            data.append({
                "Name": node.name,
                "Description": node.description,
                "Processed": node.processed,
                "Path": path
            })
        df = pd.DataFrame(data)
        return df

    def display_hierarchy(self, root):
        """
        Displays the hierarchy using AgGrid with tree data.
        """
        df = self.prepare_dataframe(root)

        gb = GridOptionsBuilder.from_dataframe(df)
        # Remove or comment out the pagination configuration
        # gb.configure_pagination(paginationAutoPageSize=True)  # Remove this line

        gb.configure_selection('single')
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True)

        grid_options = gb.build()

        # Manually set tree data options
        grid_options['treeData'] = True
        grid_options['getDataPath'] = JsCode("""
            function(data) {
                return data.Path.split(" / ");
            }
        """)
        grid_options['autoGroupColumnDef'] = {
            'headerName': 'Name',
            'cellRenderer': 'agGroupCellRenderer',
            'cellRendererParams': {
                'suppressCount': True
            }
        }

        # Display AgGrid with adjusted height and width, and without pagination
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            height=800,  # Increased height to make it longer
            width='100%',  # Ensure it takes the full available width
            data_return_mode='AS_INPUT',
            update_mode='MODEL_CHANGED',
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=True,
            allow_unsafe_jscode=True
        )

        selected = grid_response['selected_rows']
        if selected:
            selected_node_name = selected[0]['Name']
            node = self.find_node_by_name(root, selected_node_name)
            if node:
                st.write(f"### You selected: **{node.name}**")
                st.write(f"**Description:** {getattr(node, 'description', 'No description.')}")
                st.write(f"**Processed:** {getattr(node, 'processed', False)}")
            else:
                st.warning("Selected node not found in the hierarchy.")

    def find_node_by_name(self, root, name):
        """
        Finds a node by its name in the AnyTree structure.
        Assumes node names are unique.
        """
        for node in PreOrderIter(root):
            if node.name == name:
                return node
        return None
