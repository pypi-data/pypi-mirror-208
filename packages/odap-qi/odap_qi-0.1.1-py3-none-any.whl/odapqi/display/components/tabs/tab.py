from typing import List, Callable
from ipywidgets import (
    Layout,
    Tab,
)
from odapqi.display import Main, Segment, Export, Overview


class WidgetTab(Main):
    TAB_CONTENTS = ["Explore & create segment", "Export", "Manage segments"]

    def __init__(
        self,
        *,
        attributes: List[str],
        calculate_conditions: Callable,
        remove_segment_sql: Callable,
        get_segments: Callable,
        get_destinations: Callable,
        build_export_config: Callable,
        create_export_job: Callable,
        save_segment: Callable,
        databricks_host: str,
    ):
        self.segment = Segment(
            attributes=attributes,
            get_ids=calculate_conditions,
            save_segment=save_segment,
        )
        self.export = Export(
            get_destinations=get_destinations,
            get_segments=get_segments,
            build_export_config=build_export_config,
            create_export_job=create_export_job,
            databricks_host=databricks_host,
        )
        self.overview = Overview(
            remove_segment_sql=remove_segment_sql,
            get_segments=get_segments,
            export_segment=self.export_segment,
            edit_segment=self.edit_segment,
        )
        super().__init__(
            body=Tab(
                children=[
                    self.segment.display_output(),
                    self.export.display_output(),
                    self.overview.display_output(),
                ],
                layout=Layout(min_height="400px"),
            ),
            graphics=False,
        )

        for i in range(len(self.TAB_CONTENTS)):
            self.body.set_title(i, self.TAB_CONTENTS[i])
        # tab.selected_index = 1
        self.body.observe(self.change_tabs, names="selected_index")

    def export_segment(self, id: str):
        self.body.selected_index = 1
        self.export.export_segment_wg.value = id

    def edit_segment(self, segment_conditions: str, name: str, id: str):
        self.segment.reset()

        self.body.selected_index = 0
        for x in segment_conditions.split(")"):
            if x:
                y = x.split("(")
                if "and" in y[0]:
                    self.segment.add_box("change")
                self.segment.save.body.children[0].children[1].value = name
                conditions = {"type": "between", "vals": []}
                if "> " in y[1]:
                    conditions["type"] = "greater than"
                    conditions["vals"] = float(y[1].split("> ")[1])
                elif "< " in y[1] and "and" not in y[1]:
                    conditions["type"] = "less than"
                    conditions["vals"] = float(y[1].split("< ")[1])
                elif "== " in y[1]:
                    conditions["type"] = "equals"
                    conditions["vals"] = float(y[1].split("== ")[1])
                else:
                    conditions["vals"] = [
                        float(y[1].split(">= ")[1].split(" ")[0]),
                        float(y[1].split("< ")[1]),
                    ]
                self.segment.boxes.add_attribute(
                    selector="",
                    index=-1,
                    alternative={
                        "id": y[1].split(" ")[0],
                        "condition": conditions["type"],
                        "value": conditions["vals"],
                    },
                )
                self.segment.update = True
                self.segment.save.body.children[0].children[1].disabled = True
                self.segment.save.body.children[0].children[
                    2
                ].description = "Update segment"
                self.segment.save.id = id

    def change_tabs(self, change):
        tab_index = change["new"]
        if type(tab_index) == int:
            if tab_index == 2:
                self.overview.segment_table(True)
            elif tab_index == 0:
                self.segment.reset()
            elif tab_index == 1:
                self.export.export_form_reset("change")
