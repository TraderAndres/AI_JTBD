# test_aggrid.py
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd

def main():
    st.title("Streamlit AgGrid Tree Data Test")

    # Sample DataFrame with hierarchical path
    data = {
        "Name": [
            "Finance",
            "Banking",
            "Retail Banking",
            "Corporate Banking",
            "Investment",
            "Asset Management",
            "Investment Banking"
        ],
        "Description": [
            "Finance industry hierarchy",
            "Banking sector",
            "Services for individual consumers",
            "Services for businesses",
            "Investment services",
            "Managing client assets",
            "Advisory and capital raising"
        ],
        "Processed": [False, False, False, False, False, False, False],
        "Path": [
            "Finance",
            "Finance / Banking",
            "Finance / Banking / Retail Banking",
            "Finance / Banking / Corporate Banking",
            "Finance / Investment",
            "Finance / Investment / Asset Management",
            "Finance / Investment / Investment Banking"
        ]
    }

    df = pd.DataFrame(data)

    # Configure GridOptionsBuilder
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
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

    # Display AgGrid
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        height=400,
        width='100%',
        data_return_mode='AS_INPUT',
        update_mode='MODEL_CHANGED',
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=True,
        allow_unsafe_jscode=True
    )

    selected = grid_response['selected_rows']
    if selected:
        selected_node_name = selected[0]['Name']
        st.write(f"You selected: **{selected_node_name}**")

if __name__ == "__main__":
    main()
