from ipywidgets import (
    Layout,
    Box,
    Dropdown,
    Button,
    Label,
    BoundedFloatText,
)
from odapqi.display import Main


class Attribute(Main):
    NUMERICAL_CONDITIONS = ["between", "equals", "less than", "greater than"]

    def __init__(self, selector, alternative={"id": False}):
        super().__init__(
            body=Box(
                children=[
                    Button(
                        description="Remove attribute",
                        layout=Layout(
                            flex="1 1 auto", width="auto", margin="0 15px 0 0"
                        ),
                        icon="trash",
                        tooltip=f"Remove attribute {selector.body.children[2].value if not alternative['id'] else alternative['id']}",
                    ),
                    Label(
                        value=selector.body.children[2].value
                        if not alternative["id"]
                        else alternative["id"],
                        layout=Layout(
                            flex="1 1 auto", width="auto", margin="0 15px 0 0"
                        ),
                    ),
                    Dropdown(
                        description="Condition",
                        options=self.NUMERICAL_CONDITIONS,
                        value=self.NUMERICAL_CONDITIONS[0]
                        if not alternative["id"]
                        else alternative["condition"],
                        layout=Layout(
                            flex="50 1 auto", width="auto", margin="0 15px 0 0"
                        ),
                    ),
                    Box(
                        children=[
                            BoundedFloatText(
                                value=0
                                if not alternative["id"]
                                else float(alternative["value"][0]),
                                min=0,
                                max=10.0,
                                step=0.1,
                                disabled=False,
                            ),
                            BoundedFloatText(
                                value=10
                                if not alternative["id"]
                                else float(alternative["value"][1]),
                                min=0,
                                max=10.0,
                                step=0.1,
                                disabled=False,
                            ),
                        ]
                        if not alternative["id"]
                        or alternative["condition"] == "between"
                        else [
                            BoundedFloatText(
                                value=float(alternative["value"][0]),
                                min=0,
                                max=10.0,
                                step=0.1,
                                disabled=False,
                            )
                        ]
                    ),
                ],
                layout=Layout(
                    display="flex",
                    flex_flow="row",
                    align_items="center",
                ),
            ),
            graphics=False,
        )
