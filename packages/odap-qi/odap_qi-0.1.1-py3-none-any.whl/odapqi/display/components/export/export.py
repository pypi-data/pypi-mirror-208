from typing import Callable
from ipywidgets import (
    Layout,
    Text,
    Dropdown,
    Button,
    HTML,
    Checkbox,
    VBox,
)
from odapqi.display import Main


class Export(Main):
    def __init__(
        self,
        *,
        get_destinations: Callable,
        get_segments: Callable,
        build_export_config: Callable,
        create_export_job: Callable,
        databricks_host: str,
    ):
        self.build_export_config = build_export_config
        self.create_export_job = create_export_job
        self.databricks_host = databricks_host

        self.export_name_wg = Text(value="", description="Export name:", disabled=False)
        self.export_segment_wg = Dropdown(
            options=list(map(lambda seg: (seg.name, seg.id), get_segments())),
            description="Segment:",
            value=None,
        )
        self.export_destinations_wg = Dropdown(
            options=list(map(lambda seg: (seg.name, seg.id), get_destinations())),
            description="Destination:",
            disabled=False,
        )
        self.export_run_now_wg = Checkbox(
            value=False, description="Run now", indent=True
        )
        self.export_submit_wg = Button(description="CREATE EXPORT", disabled=True)
        self.export_reset_wg = Button(
            description="RESET & CREATE NEW EXPORT", layout=Layout(width="300px")
        )

        self.export_inputs_wg = [
            self.export_name_wg,
            self.export_segment_wg,
            self.export_destinations_wg,
            self.export_run_now_wg,
        ]
        self.export_form_wg = [
            *self.export_inputs_wg,
            self.export_submit_wg,
        ]
        super().__init__(body=VBox(self.export_form_wg), graphics=False)

        self.export_destinations_wg.observe(self.validate_export_form, names="value")
        self.export_segment_wg.observe(self.validate_export_form, names="value")
        self.export_name_wg.observe(self.validate_export_form, names="value")
        self.export_reset_wg.on_click(self.export_form_reset)
        self.export_submit_wg.on_click(self.on_export_submit)

    def on_export_submit(self, e):
        self.export_name_wg.disabled = True
        self.export_segment_wg.disabled = True
        self.export_destinations_wg.disabled = True
        self.export_run_now_wg.disabled = True
        self.export_submit_wg.disabled = True
        self.export_submit_wg.description = "CREATING..."
        export_config = self.build_export_config(
            self.export_name_wg.value,
            self.export_segment_wg.value,
            self.export_destinations_wg.value,
            [],
        )
        job_id = self.create_export_job(export_config, self.export_run_now_wg.value)
        self.body.children = [
            *self.export_inputs_wg,
            HTML(
                value="<a href='{0}/#job/{1}'>Click to open the new export job</a>".format(
                    self.databricks_host, job_id
                )
            ),
            self.export_reset_wg,
        ]

    def export_form_reset(self, e):
        self.body.children = self.export_form_wg
        self.export_name_wg.disabled = False
        self.export_segment_wg.disabled = False
        self.export_destinations_wg.disabled = False
        self.export_run_now_wg.disabled = False
        self.export_name_wg.value = ""
        self.export_segment_wg.value = None
        self.export_destinations_wg.value = None
        self.export_submit_wg.disabled = False
        self.export_submit_wg.description = "CREATE EXPORT"

    def validate_export_form(self, e):
        if (
            self.export_name_wg.value
            and self.export_segment_wg.value
            and self.export_destinations_wg.value
        ):
            self.export_submit_wg.disabled = False
        else:
            self.export_submit_wg.disabled = True
