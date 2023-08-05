from typing import Callable
from ipywidgets import (
    Layout,
    Button,
    Label,
    Output,
    GridBox,
)
from odapqi.display import Main


class Overview(Main):
    def __init__(
        self,
        *,
        remove_segment_sql: Callable,
        get_segments: Callable,
        export_segment: Callable,
        edit_segment: Callable,
    ):
        self.output = Output()
        super().__init__(
            body=GridBox(
                children=[
                    Label(value="ID"),
                    Label(value="NAME"),
                    Label(value="CONDITION"),
                    Label(value="EDIT"),
                    Label(value="REMOVE"),
                    Label(value="EXPORT"),
                ],
                layout=Layout(
                    grid_template_columns="150px 150px auto 75px 75px 115px",
                    grid_gap="5px 10px",
                    padding="0 10px 0 0",
                ),
            ),
            graphics=False,
        )
        self.edit_segment = edit_segment
        self.export_segment = export_segment
        self.get_segments = get_segments
        self.segments = get_segments()
        self.remove_segment_sql = remove_segment_sql
        self.segment_table()

    def segment_table(self, reset=False):
        query = self.get_segments()
        ids = []
        if reset:
            for i in range(0, len(self.body.children), 6):
                ids.append(self.body.children[i].value)
        for i in query:
            if i.id[0:10] not in ids:
                self.add_child(
                    child=[
                        Label(value=i.id[0:10]),
                        Label(value=i.name),
                        Label(value=i.conditions),
                        Button(description="EDIT", layout=Layout(width="auto")),
                        Button(description="REMOVE", layout=Layout(width="auto")),
                        Button(description="EXPORT", layout=Layout(width="auto")),
                    ]
                )
            self.body.children[-3].on_click(self.edit_persona)
            self.body.children[-2].on_click(self.remove_persona)
            self.body.children[-1].on_click(self.export_persona)

    def remove_persona(self, change):
        for index, val in enumerate(self.body.children):
            if val == change:
                self.remove_segment_sql(self.body.children[index - 4].value)
                self.remove_child_index(
                    indexes=[
                        index - 4,
                        index - 3,
                        index - 2,
                        index - 1,
                        index,
                        index + 1,
                    ]
                )

    def edit_persona(self, change):
        for index, val in enumerate(self.body.children):
            if val == change:
                self.edit_segment(
                    self.body.children[index - 1].value,
                    self.body.children[index - 2].value,
                    self.body.children[index - 3].value,
                )

    def export_persona(self, change):
        for index, val in enumerate(self.body.children):
            if val == change:
                self.export_segment(
                    [
                        x
                        for x in filter(
                            lambda x: self.body.children[index - 5].value in x.id,
                            self.segments,
                        )
                    ][0].id
                )
