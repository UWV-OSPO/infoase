from uwv_toolkit.streamlit.components.footer import Footer
from uwv_toolkit.utils import deep_update


class FooterMixin:
    """
    A mixin class that provides functionality for displaying a footer in a page.
    """

    def __init__(self, **kwargs):
        """
        Initializes the FooterMixin.

        Args:
            **kwargs: Keyword arguments to configure the footer.
        """
        self._config = deep_update(
            {
                "footer": {
                    "content": None,
                    "fixed": True,
                }
            },
            kwargs,
        )

        super().__init__(**kwargs)

    def show(self) -> None:
        """
        Displays the page content and the footer, if configured.

        Returns:
            None
        """

        # Show footer before all else otherwise it flickers when chatting.
        if "footer" in self._config:

            cfg = self._config["footer"]
            footer = Footer(
                content=cfg["content"],
                fixed=cfg["fixed"],
            )
            footer.show()

        super().show()
