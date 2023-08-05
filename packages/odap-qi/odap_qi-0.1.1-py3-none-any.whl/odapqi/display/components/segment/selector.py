from typing import List, Callable
from ipywidgets import (
    Layout,
    Box,
    Text,
    Dropdown,
    Button,
    HTML,
    Label,
    Combobox,
)
from odapqi.display import Main


class Selector(Main):
    def __init__(
        self, *, attributes: List[str], get_conditions: Callable, get_ids: Callable
    ):
        super().__init__(
            body=Box(
                children=[
                    Label(
                        value="Filter attributes",
                        layout=Layout(width="auto", color="red"),
                    ),
                    Text(disabled=False, layout=Layout(width="auto")),
                    Combobox(
                        description="Condition",
                        options=attributes,
                        placeholder='Add attribute',
                        layout=Layout(
                            flex="2 1 auto",
                            width="350px",
                            margin="0 15px 0 0",
                        ),
                    ),
                    Dropdown(
                        description="Container",
                        options=["Container #1"],
                        value="Container #1",
                        layout=Layout(
                            flex="2 1 auto", width="auto", margin="0 15px 0 0"
                        ),
                    ),
                    Button(
                        description="Add attribute",
                        icon="plus",
                        layout=Layout(
                            flex="2 1 auto", width="auto", margin="0 15px 0 0"
                        ),
                    ),
                    HTML(
                        value=f"""
                        <div 
                        style='background:rgb(238, 238, 238);color:black;border:1px solid black;width:150px;text-align:center;'>
                        <font style='font-size:0.85rem;'>Count of ids - {get_ids(get_conditions())}</font>
                        </div>
                    """,
                        layout=Layout(margin="0 15px 0 0"),
                    ),
                    Button(
                        description="Recalculate IDs",
                        icon="retweet",
                        layout=Layout(
                            flex="2 1 auto", width="auto", margin="0 15px 0 0"
                        ),
                    ),
                ],
                layout=Layout(
                    display="flex",
                    align_items="center",
                    width="100%",
                    min_height="10px",
                ),
            ),
            graphics=Box(
                children=[
                    # HTML(
                    #    value=f"<div style='border-top:1px solid black;border-bottom:1px solid black;width:100%'><b><font style='font-size:1rem;'>Create or explore segment</b></div>"
                    # ),
                    HTML(
                        value=f"<b><font style='font-size:0.85rem;'>Add filter conditions</b>",
                        layout=Layout(margin="15px 0 10px 0"),
                    ),
                ],
                layout=Layout(display="block"),
            ),
        )
        self.attributes = attributes
        self.get_conditions = get_conditions
        self.get_ids = get_ids

        self.body.children[1].observe(self.apply_filter, "value")
        self.body.children[6].on_click(self.recheck_ids)

    def apply_filter(self, change):
        self.body.children[2].options = [
            x for x in self.attributes if change["new"] in x
        ]

    def recheck_ids(self, change):
        values = self.body.children[5].value.split("- ")
        self.body.children[5].value = values[0] + "- ..."
        self.body.children[5].value = (
            values[0] + "- " + str(self.get_ids(self.get_conditions()))
        )
