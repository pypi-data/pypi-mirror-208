import uuid
from typing import Callable
from ipywidgets import (
    Layout,
    Box,
    Text,
    Button,
    Label,
)
from odapqi.display import Main
from odapqi.logger import create_logger

logger = create_logger("simple_example")


class Save(Main):
    def __init__(self, update):
        self.update = update
        self.id = ""
        super().__init__(
            body=Box(
                children=[
                    Box(
                        children=[
                            Label(value="Segment name"),
                            Text(value=""),
                            Button(description="Save as segment"),
                        ],
                        layout=Layout(margin="25px 0 0 0"),
                    ),
                ],
                layout=Layout(border_top="1px solid black", display="block"),
            ),
            graphics=Box(
                children=[],
                layout=Layout(
                    border="1px solid rgba(0, 0, 0, 0.2)", margin="15px 0 5px 0"
                ),
            ),
        )

    def save_persona(
        self, *, boxes, get_conditions: Callable, save_segment: Callable, output
    ):
        if self.body.children[0].children[1].value:
            with output:
                logger.info(
                    "Saving persona in progress"
                    if not self.id
                    else "Updating persona in progress"
                )
            try:
                if self.id:
                    save_segment(
                        "",
                        f"conditions = '{get_conditions()}' WHERE id LIKE '{self.id}%'",
                    )
                else:
                    save_segment(
                        f"""
                    (
                        '{uuid.uuid4()}', 
                        '{self.body.children[0].children[1].value}', 
                        '{get_conditions()}', 
                        False, 
                        0
                    )
                    """
                    )
                self.body.children[0].children[1].value = ""
                boxes.reset()
                with output:
                    logger.info("Persona saved")
            except:
                with output:
                    logger.error("Persona save failed")
        else:
            with output:
                logger.error("No persona name")
