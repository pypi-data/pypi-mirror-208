from txp.web.core_components.app_profiles import AppProfile
from txp.web.core_components.main_view import MainView
from txp.web.views.analytics_view import (
    DataRequest,
    VibrationDataCharts,
    TemperatureDataCharts,
)
import txp.web.views.analytics.vibration_analytics as vibration_utils
import txp.web.views.analytics.complex_analytics as complex_utils
import txp.web.views.analytics.temperature_analytics_view as temperature_utils
from txp.common.utils import bigquery_utils
from typing import Dict, Any
import streamlit as st
import logging
import datetime
import pytz
import txp.web.new_views.rpm_util as rpm
import dataclasses
import pandas as pd
import plotly.graph_objects as go
import enum
from PIL import Image
import dataclasses
import os
_current_directory = os.path.dirname(os.path.realpath(__file__))

# TODO: This might be a problem. The logging configuration is being taken from `txp` package
from txp.common.config import settings

log = logging.getLogger(__name__)
log.setLevel(settings.txp.general_log_level)


@dataclasses.dataclass
class EngineCardData:
    image: Image
    last_temp_value: float
    last_seen_value: datetime
    last_rpm_value: float
    engine_card: pd.DataFrame
    last_24_hours_state_plot: Image
    fft_data: VibrationDataCharts
    temperature: TemperatureDataCharts
    worked_time: float


class EquipmentDetails(MainView):
    def __init__(self):
        super(EquipmentDetails, self).__init__(component_key="equipment_details")

        # Keys to name the interactive widgets and the corresponding class attribute
        self._machines_group_selectbox_key = "machines_group_selectbox"
        self._machines_group_selected: str = None
        self._machine_selectbox = "machine_selectbox"
        self._machine_selected: str = None
        self._data_to_show: EngineCardData = None

    def _machines_group_selectbox_clicked(self):
        self._user_first_interacted = True
        self._machines_group_selected = st.session_state[self._machines_group_selectbox_key]

    def _machine_selectbox_clicked(self):
        self._user_first_interacted = True
        self._machine_selected = st.session_state[self._machine_selectbox]

    def _see_details_btn_clicked(self):
        self._data_to_show = self._collect_machine_data(
            self._machines_group_selected,
            self._machine_selected,
            self._get_edge_for_machine().logical_id,
        )

    def _get_machine_image(self):
        return Image.open(f"{_current_directory}/../resources/images/Motor_lab.jpg")

    def _get_last_24_plot(self):
        return Image.open(f"{_current_directory}/../resources/images/last_24_hours.png")

    def _get_machine_specifications(self):
        data = {"Lubricación": "Cada 3500 Hrs", "Cambio de Bandas": "Cada 10.000 Hrs"}
        return pd.DataFrame([data])

    def _get_edge_for_machine(self):
        # For demo, we return the first edge only!
        return self.app_state.conveyors_dashboard[
            self._machines_group_selected
        ].get_edge_by_machine(self._machine_selected)

    def _collect_machine_data(self, machines_group, machine_id, edge_logical_id):
        image = self._get_machine_image()
        last_24_hours_plt = self._get_last_24_plot()
        machine_specifications = self._get_machine_specifications()

        if self.app_state.conveyors_dashboard[machines_group]._machine_metrics.get(machine_id, None):
            return EngineCardData(
                image,
                self.app_state.conveyors_dashboard[machines_group]
                ._machine_metrics[machine_id]
                .temperature,
                self.app_state.conveyors_dashboard[machines_group]
                ._machine_metrics[machine_id]
                .last_seen,
                self.app_state.conveyors_dashboard[machines_group]
                ._machine_metrics[machine_id]
                .rpm,
                machine_specifications,
                last_24_hours_plt,
                None,
                None,
                self.app_state.conveyors_dashboard[machines_group]
                ._machine_metrics[machine_id]
                .worked_hours
            )
        else:
            return EngineCardData(
                image,
                0.0,
                "",
                0.0,
                machine_specifications,
                last_24_hours_plt,
                None,
                None,
                0.0
            )

    def _draw_machines_group_selectbox(self):
        machines_groups = self.app_state.project_model.assets_groups_table.keys()
        self._machines_group_selected = st.selectbox(
            label="Seleccione Linea",
            options=machines_groups,
            help="Seleccione la línea de producción que quiere inspeccionar",
            on_change=self._machines_group_selectbox_clicked,
            key=self._machines_group_selectbox_key
        )

    def _draw_machines_selectbox(self):
        machines = self.app_state.project_model.assets_groups_table[
            self._machines_group_selected
        ].assets
        self._machine_selected = st.selectbox(
            label="Seleccione Equipo",
            options=machines,
            help=f"Seleccione el equipo perteneciente a la línea {self._machines_group_selected} para ver sus detalles",
            key=self._machine_selectbox
        )

    def _draw_see_details_btn(self):
        st.button(
            label="Ver Detalles",
            on_click=self._see_details_btn_clicked,
        )

    def _draw_machine_component(self):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Modelo**: SA47/T DRS71M4")
            st.markdown("**Fabricante**: SEW Eurodrive")
            st.markdown(
                f"**Visto por última vez**: {self._data_to_show.last_seen_value}"
            )
            st.image(self._data_to_show.image, width=400)
            # st.markdown("**Ficha técnica del equipo**")
            # st.table(self._data_to_show.engine_card)

        with c2:
            st.markdown("**Últimas Métricas Recibidas**")
            # st.table(self._data_to_show.metrics_table)
            st.metric(
                label="Temperatura",
                value=f"{self._data_to_show.last_temp_value:.2f} C",
            )
            st.metric(
                label="Velocidad",
                value=f"{int(self._data_to_show.last_rpm_value)} RPM",
            )
            st.metric(
                label="Horas Trabajadas",
                value=f"{float(self._data_to_show.worked_time):.2f} horas",
            )

    def _render_content(self) -> None:
        area = st.empty()
        with st.container():
            self.app_state.stop_background_download()
            st.subheader("Detalles de Equipo")

            c1_machine_group_box, c2_machine_box = st.columns(2)

            with c1_machine_group_box:
                self._draw_machines_group_selectbox()
            with c2_machine_box:
                self._draw_machines_selectbox()

            self._draw_see_details_btn()

            if self._data_to_show:
                st.markdown("--------")
                st.markdown(f"### Equipo: {self._machine_selected}")
                self._draw_machine_component()

                st.markdown("-------")

    def _render_submenu(self) -> None:
        pass

    def _build_content_state(self) -> Dict:
        pass

    def _build_submenu_state(self) -> Dict:
        pass

    def get_associated_profile(self) -> AppProfile:
        return AppProfile.RESUMEN

    def get_display_name(cls) -> str:
        return "Detalles de Equipo"
