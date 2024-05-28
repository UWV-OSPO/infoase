from typing import Callable, Optional
import pandas as pd
import streamlit as st
from uwv_toolkit.streamlit.components import BaseStreamlitComponent


class StreamlitTableComponent(BaseStreamlitComponent):
    def __init__(
        self,
        dataframe: pd.DataFrame,
        action_column_title: Optional[str] = None,
        action_column_content_function: Optional[
            Callable[[int, pd.Series, st.delta_generator.DeltaGenerator], None]
        ] = None,
    ):
        """
        A Streamlit component that displays a DataFrame as a table.

        Args:
            dataframe (pd.DataFrame): The DataFrame to display.
            action_column_title (Optional[str], optional): The title of the action column. Defaults to None.
            action_column_content_function (Optional[Callable[[int, pd.Series, st.delta_generator.DeltaGenerator], None]], optional): A function that generates the content of the action column. Defaults to None.

            The function should have the following signature:
            def my_action_column_content(index, row: pd.Series, column: st.delta_generator.DeltaGenerator):
                pass
        """

        self.dataframe = dataframe
        self.action_column_title = action_column_title
        self.action_column_content_function = action_column_content_function

    def show(self):
        with st.container():
            st.write("""<div class='column-marker'/>""", unsafe_allow_html=True)

            # Bepaal het aantal kolommen op basis van de DataFrame
            col_names = list(self.dataframe.columns)
            if self.action_column_title and self.action_column_content_function:
                col_names.append(self.action_column_title)

            num_cols = len(col_names)
            col_widths = [1] * num_cols  # Verdeel de breedte gelijkmatig

            # Header kolommen
            header_cols = st.columns(col_widths)

            for header_col, name in zip(header_cols, col_names):
                header_col.write(
                    f"<b>{name}</b><span class='col-header' />", unsafe_allow_html=True
                )

            # Rijen van de DataFrame
            for index, row in self.dataframe.iterrows():
                cols = st.columns(col_widths)
                for i, col_name in enumerate(self.dataframe.columns):
                    cols[i].write(row[col_name])

                # Actie kolom inhoud
                if self.action_column_content_function:
                    self.action_column_content_function(index, row, cols[-1])

            # Stijlen toevoegen
            dynamic_css = self._generate_dynamic_css(num_cols)
            self._add_styles(dynamic_css)

    def _generate_dynamic_css(self, num_cols: int) -> str:
        """Generate dynamic CSS based on the number of columns."""
        css = """

[data-testid="stVerticalBlock"]:has(div.column-marker) [data-testid="stHorizontalBlock"] {
    /* Remove gaps, so that it looks like a table */
    gap:0;
}
[data-testid="stVerticalBlock"]:has(div.column-marker) [data-testid="column"]:has(span.col-header) {
    background:rgb(240, 242, 246);
    border: 1px solid rgba(0, 0, 0, 0.2);
}
[data-testid="stVerticalBlock"]:has(div.column-marker) [data-testid="column"] {
    padding:10px;
}
[data-testid="stVerticalBlock"]:has(div.column-marker) [data-testid="column"] {
    border: 1px solid rgb(240, 242, 246);
    border-top: none;
    margin-bottom: -1rem; /* Undo the horizontal gap */
}
        """

        # Dynamische CSS voor kolomgrenzen
        for i in range(1, num_cols):
            css += f"""
            [data-testid="stVerticalBlock"]:has(div.column-marker) [data-testid="column"]:has(span.col-header):nth-child({i}),
            [data-testid="stVerticalBlock"]:has(div.column-marker) [data-testid="column"]:nth-child({i}) {{
                border-right: none;
            }}
            """

        # CSS voor de onderste rand van de laatste rij
        css += """
        [data-testid="stVerticalBlockBorderWrapper"]:has(div.column-marker) [data-testid="stHorizontalBlock"]:last-child [data-testid="column"]:not(:last-child) {
            border-bottom: 1px solid rgb(240, 242, 246);
        }
        """

        return css
