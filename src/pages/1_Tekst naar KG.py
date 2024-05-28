import os

import streamlit as st
from uwv_toolkit.utils import FileExceptionHandler, load_env, azure_llm
from modules.extraction import system_prompt
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage
from modules.extraction import FewShotDataExtractor

load_env()


DEFAULT_TEXT = """Walter (Walt) Elias Disney (Chicago, 5 december 1901 – Burbank, 15 december 1966) was een Amerikaans tekenaar, filmproducent, filmregisseur, scenarioschrijver, stemacteur, animator, zakenman, entertainer, internationaal icoon en een filantroop.

Disney werd vooral bekend door zijn vernieuwingen in de animatiefilm-industrie. Als medeoprichter (samen met zijn broer Roy Oliver Disney) van The Disney Brothers Studio, later omgedoopt tot Walt Disney Productions en later naar The Walt Disney Company, werd Disney een van de bekendste filmproducenten ter wereld."""


class TextToKgPage(BaseUWVGraphPage):

    def _show_main(self):
        st.title(self._config["page_config"]["page_title"])
        st.markdown(
            "Op deze pagina kun je experimenteren met het omzetten van tekst naar een Knowledge Graph. Druk op de knop 'Start extractie' om de tekst te verwerken."
        )

        st.markdown("---")
        with st.form("cypher_form"):
            text_input = st.text_area(
                "Voer de tekst in", value=DEFAULT_TEXT, max_chars=2400, height=400
            )

            with st.expander("✍️ Pas prompt aan", expanded=False):
                st.slider("LLM Temperature", 0.0, 1.0, 0.0, key="temperature")

                st.text_area(
                    "System prompt",
                    value=system_prompt,
                    height=300,
                    key="prompt",
                    help="Ververs de pagina om de prompt te resetten naar het origineel",
                )
                st.warning(
                    "Sla je prompt en temperatuur instellingen op, dit wordt nergens opgeslagen."
                )

            submitted = st.form_submit_button("Start extractie")
        # submitted = st.button("Start extractie")

        if submitted:
            with st.spinner(
                "☕️ Bezig met extractie van nodes, relaties en eigenschappen..."
            ):
                llm = azure_llm(temperature=st.session_state.temperature)
                extractor = FewShotDataExtractor(
                    llm,
                    system_prompt=st.session_state.prompt,
                    verbose=(os.getenv("VERBOSE") == "1"),
                )

                result = extractor.run(text_input)

            self.show_knowledge_graph(result)


try:
    p = TextToKgPage(
        page_config={
            "page_title": "Tekst naar Knowledge Graph ✨",
            "page_icon": "🏝️",
            "layout": "wide",
        },
    )

    p.show()

except Exception as e:
    FileExceptionHandler.handle(exception=e)
    # Display an error message and stop rendering.
    st.error("An error occurred. Please contact the developer.")
