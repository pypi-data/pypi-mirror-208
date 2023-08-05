from ipywidgets import (
    Layout,
    Box,
    HTML,
    BoundedFloatText,
)
from odapqi.display import Main, Attribute


class Attributes(Main):
    def __init__(self):
        super().__init__(
            body=Box(
                children=[
                    Box(
                        children=[],
                        layout=Layout(
                            display="block",
                            align_items="center",
                            border="1px solid black",
                            min_height="10px",
                            padding="20px",
                            min_width="100%",
                        ),
                    )
                ],
                layout=Layout(display="block"),
            ),
            graphics=Box(
                children=[
                    Box(
                        children=[],
                        layout=Layout(
                            border="1px solid rgba(0, 0, 0, 0.2)",
                            margin="10px 0 15px 0",
                        ),
                    ),
                    HTML(
                        value=f"<b><font style='font-size:0.85rem;'>Segment conditions</b>",
                        layout=Layout(margin="0 0 10px 0"),
                    ),
                ],
                layout=Layout(display="block"),
            ),
        )

    def add_attribute(self, *, selector, index, alternative={"id": False}):
        data = Attribute(selector, alternative).display_output()
        data.children[0].on_click(self.remove_button)
        data.children[2].observe(self.change_condition, "value")
        data.children[3].children[0].observe(self.change_range, "value")
        data.children[3].children[1].observe(self.change_range, "value")
        self.body.children[index].children = tuple(
            list(self.body.children[index].children) + [data]
        )

    def reset(self):
        self.body.children = [
            Box(
                children=[],
                layout=Layout(
                    display="block",
                    align_items="center",
                    border="1px solid black",
                    min_height="10px",
                    padding="20px",
                    min_width="100%",
                ),
            )
        ]

    def get_conditions(self):
        query = []
        for count, box in enumerate(self.body.children):
            if hasattr(box, "children"):
                for count_1, obj in enumerate(box.children):
                    if obj.children[2].value == "between":
                        query.append(
                            f"({obj.children[1].value} >= {obj.children[3].children[0].value} and {obj.children[1].value} < {obj.children[3].children[1].value})"
                        )
                    elif obj.children[2].value == "equals":
                        query.append(
                            f"({obj.children[1].value} == {obj.children[3].children[0].value})"
                        )
                    elif obj.children[2].value == "less than":
                        query.append(
                            f"({obj.children[1].value} < {obj.children[3].children[0].value})"
                        )
                    else:
                        query.append(
                            f"({obj.children[1].value} > {obj.children[3].children[0].value})"
                        )
                    query.append("or")
            query = query[:-1]
            query.append("and")
        return " ".join(query[:-1])

    def change_condition(self, change):
        for count, box in enumerate(self.body.children):
            if hasattr(box, "children"):
                for count_1, obj in enumerate(box.children):
                    for inner_obj in obj.children:
                        if (
                            hasattr(inner_obj, "layout")
                            and inner_obj.layout == change["owner"].layout
                        ):
                            data = None
                            if change["new"] == "between":
                                data = [
                                    BoundedFloatText(
                                        value=0,
                                        min=0,
                                        max=10.0,
                                        step=0.1,
                                        disabled=False,
                                    ),
                                    BoundedFloatText(
                                        value=10,
                                        min=0,
                                        max=10.0,
                                        step=0.1,
                                        disabled=False,
                                    ),
                                ]
                            else:
                                data = [
                                    BoundedFloatText(
                                        value=1,
                                        min=0,
                                        max=10.0,
                                        step=0.1,
                                        disabled=False,
                                    ),
                                ]
                            data[0].observe(self.change_range, "value")
                            if change["new"] == "between":
                                data[1].observe(self.change_range, "value")
                            self.body.children[count].children[count_1].children[
                                -1
                            ].children = data

    def change_range(self, change):
        pass

    def remove_button(self, change):
        for count, box in enumerate(self.body.children):
            if hasattr(box, "children"):
                for count_1, obj in enumerate(box.children):
                    if hasattr(obj, "children"):
                        for inner_obj in obj.children:
                            if (
                                hasattr(inner_obj, "tooltip")
                                and inner_obj.tooltip == change.tooltip
                            ):
                                self.remove_grand_child(index=count, obj=obj)
