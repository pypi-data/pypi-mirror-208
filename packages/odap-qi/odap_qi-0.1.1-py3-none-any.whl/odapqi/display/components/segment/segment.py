from typing import List, Callable
from ipywidgets import (
    Layout,
    Box,
    Button,
    Label,
    Output,
)
from odapqi.display import Main, Attributes, Selector, Save


class Segment(Main):
    def __init__(
        self, *, attributes: List[str], get_ids: Callable, save_segment: Callable
    ):
        self.update = False
        self.attributes = attributes
        self.get_ids = get_ids
        self.save_segment = save_segment

        self.boxes = Attributes()

        self.selector = Selector(
            attributes=attributes,
            get_conditions=self.boxes.get_conditions,
            get_ids=get_ids,
        )
        self.selector.body.children[4].on_click(self.add_attribute)

        self.add_category = Button(
            description="Add box", icon="plus", layout=Layout(margin="15px 0 0 0")
        )
        self.add_category.on_click(self.add_box)

        self.save = Save(self.update)
        self.save.body.children[0].children[2].on_click(self.save_persona)

        self.output = Output()

        super().__init__(
            body=Box(
                children=[
                    self.selector.display_output(),
                    self.boxes.display_output(),
                    self.add_category,
                    self.save.display_output(),
                    self.output,
                ],
                layout=Layout(display="block"),
            ),
            graphics=False,
        )

    def save_persona(self, change):
        self.save.save_persona(
            boxes=self.boxes,
            get_conditions=self.boxes.get_conditions,
            save_segment=self.save_segment,
            output=self.output,
        )

    def add_box(self, change):
        self.boxes.add_child(
            child=[
                Label(
                    value="AND",
                    layout=Layout(
                        width="auto", min_width="200px", margin="25px 0 25px 0"
                    ),
                ),
                Box(
                    children=[],
                    layout=Layout(
                        display="block",
                        align_items="center",
                        border="1px solid black",
                        min_height="10px",
                        padding="20px",
                    ),
                ),
            ]
        )

        self.selector.body.children[3].options = tuple(
            list(self.selector.body.children[3].options)
            + [
                f"Container #{str(int(self.selector.body.children[3].options[-1].split('#')[1])+1)}"
            ]
        )

    def add_attribute(self, change):
        index = int(self.selector.body.children[3].value.split("#")[1])
        if index == 1:
            index = 0
        elif index % 2 != 0:
            index += 1
        self.boxes.add_attribute(
            selector=self.selector, index=index, alternative={"id": False}
        )

    def reset(self):
        self.save.id = ""
        self.save.body.children[0].children[1].disabled = False
        self.save.body.children[0].children[2].description = "Save as segment"
        self.update = False
        self.save.body.children[0].children[1].value = ""
        self.boxes.reset()
        self.output.clear_output()
