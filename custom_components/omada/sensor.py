from __future__ import annotations

import logging

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict

from homeassistant.components.sensor import (DOMAIN, DEVICE_CLASS_TIMESTAMP, SensorEntity,
                                             SensorEntityDescription)
from homeassistant.const import UnitOfInformation, UnitOfDataRate, PERCENTAGE
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt as dt_util

from .controller import OmadaController

from .api.devices import Device
from .const import (DOMAIN as OMADA_DOMAIN, CLIENTS)
from .omada_entity import (OmadaEntity, OmadaEntityDescription, device_device_info_fn,
                           client_device_info_fn, unique_id_fn)

DOWNLOAD_SENSOR = "downloaded"
UPLOAD_SENSOR = "uploaded"
UPTIME_SENSOR = "uptime"
RX_SENSOR = "rx"
TX_SENSOR = "tx"
CPU_USAGE_SENSOR = "cpu_usage"
MEMORY_USAGE_SENSOR = "memory_usage"
CLIENTS_SENSOR = "clients"
CLIENTS_2G_SENSOR = "2ghz_clients"
CLIENTS_5G_SENSOR = "5ghz_clients"
CLIENTS_6G_SENSOR = "6ghz_clients"
TX_UTILIZATION_2G_SENSOR = "2ghz_tx_utilization"
TX_UTILIZATION_5G_SENSOR = "5ghz_tx_utilization"
TX_UTILIZATION_6G_SENSOR = "6ghz_tx_utilization"
RX_UTILIZATION_2G_SENSOR = "2ghz_rx_utilization"
RX_UTILIZATION_5G_SENSOR = "5ghz_rx_utilization"
RX_UTILIZATION_6G_SENSOR = "6ghz_rx_utilization"
INTER_UTILIZATION_2G_SENSOR = "2ghz_interference_utilization"
INTER_UTILIZATION_5G_SENSOR = "5ghz_interference_utilization"
INTER_UTILIZATION_6G_SENSOR = "6ghz_interference_utilization"

LOGGER = logging.getLogger(__name__)


@callback
def client_download_value_fn(controller: OmadaController, mac: str) -> float:
    """Retrieve client total download value and convert to MB"""
    return controller.api.known_clients[mac].download / 1000000


@callback
def client_upload_value_fn(controller: OmadaController, mac: str) -> float:
    """Retrieve client total upload value and convert to MB"""
    return controller.api.known_clients[mac].upload / 1000000


@callback
def client_rx_value_fn(controller: OmadaController, mac: str) -> float:
    """Retrieve client current rx rate and convert to MB/s"""
    if mac in controller.api.clients:
        return controller.api.clients[mac].rx_rate / 1000000
    else:
        return 0


@callback
def client_tx_value_fn(controller: OmadaController, mac: str) -> float:
    """Retrieve client current tx rate and convert to MB/s"""
    if mac in controller.api.clients:
        return controller.api.clients[mac].tx_rate / 1000000
    else:
        return 0


@callback
def client_uptime_value_fn(controller: OmadaController, mac: str) -> datetime:
    """Retrieve client connected time"""
    if mac in controller.api.clients:
        return dt_util.now() - timedelta(seconds=controller.api.clients[mac].uptime)
    else:
        return None


@callback
def device_download_value_fn(controller: OmadaController, mac: str) -> float:
    """Retrieve client total download value and convert to MB"""
    return controller.api.devices[mac].download / 1000000


@callback
def device_upload_value_fn(controller: OmadaController, mac: str) -> float:
    """Retrieve client total upload value and convert to MB"""
    return controller.api.devices[mac].upload / 1000000


@callback
def device_rx_value_fn(controller: OmadaController, mac: str) -> float:
    """Retrieve device current rx rate and convert to MB/s"""
    return controller.api.devices[mac].rx_rate / 1000000


@callback
def device_tx_value_fn(controller: OmadaController, mac: str) -> float:
    """Retrieve device current tx rate and convert to MB/s"""
    return controller.api.devices[mac].tx_rate / 1000000


@callback
def device_cpu_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device current cpu usage"""
    return controller.api.devices[mac].cpu


@callback
def device_memory_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device current memory usage"""
    return controller.api.devices[mac].memory


@callback
def device_uptime_value_fn(controller: OmadaController, mac: str) -> datetime:
    """Retrieve device connected time"""
    return dt_util.now() - timedelta(seconds=controller.api.devices[mac].uptime)


@callback
def device_clients_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device client count"""
    return controller.api.devices[mac].clients


@callback
def device_clients_2g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device 2g client count"""
    return controller.api.devices[mac].clients_2ghz


@callback
def device_clients_5g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device 5g client count"""
    return controller.api.devices[mac].clients_5ghz


@callback
def device_clients_6g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device client count"""
    return controller.api.devices[mac].clients_6ghz


@callback
def device_tx_utilization_2g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device 2GHz TX utilization"""
    return controller.api.devices[mac].tx_utilization_2ghz


@callback
def device_tx_utilization_5g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device 5GHz TX utilization"""
    return controller.api.devices[mac].tx_utilization_5ghz


@callback
def device_tx_utilization_6g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device 6GHz TX utilization"""
    return controller.api.devices[mac].tx_utilization_6ghz


@callback
def device_rx_utilization_2g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device 2GHz RX utilization"""
    return controller.api.devices[mac].rx_utilization_2ghz


@callback
def device_rx_utilization_5g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device 5GHz RX utilization"""
    return controller.api.devices[mac].rx_utilization_5ghz


@callback
def device_rx_utilization_6g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device 6GHz RX utilization"""
    return controller.api.devices[mac].rx_utilization_6ghz


@callback
def device_inter_utilization_2g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device 2GHz RX utilization"""
    return controller.api.devices[mac].interference_utilization_2ghz


@callback
def device_inter_utilization_5g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device 5GHz RX utilization"""
    return controller.api.devices[mac].interference_utilization_5ghz


@callback
def device_inter_utilization_6g_value_fn(controller: OmadaController, mac: str) -> int:
    """Retrieve device 6GHz RX utilization"""
    return controller.api.devices[mac].interference_utilization_6ghz


@dataclass
class OmadaSensorEntityDescriptionMixin():
    value_fn: Callable[[OmadaController, str], datetime | float | int | None]


@dataclass
class OmadaSensorEntityDescription(
    OmadaEntityDescription,
    SensorEntityDescription,
    OmadaSensorEntityDescriptionMixin
):
    """Omada Sensor Entity Description"""


CLIENT_ENTITY_DESCRIPTIONS: Dict[str, OmadaSensorEntityDescription] = {
    DOWNLOAD_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=DOWNLOAD_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        has_entity_name=True,
        allowed_fn=lambda controller, mac: (controller.option_client_bandwidth_sensors and
                                            controller.option_track_clients and
                                            controller.is_client_allowed(mac)),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=client_device_info_fn,
        name_fn=lambda *_: "Downloaded",
        unique_id_fn=unique_id_fn,
        value_fn=client_download_value_fn
    ),
    UPLOAD_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=UPLOAD_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        has_entity_name=True,
        allowed_fn=lambda controller, mac: (controller.option_client_bandwidth_sensors and
                                            controller.option_track_clients and
                                            controller.is_client_allowed(mac)),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=client_device_info_fn,
        name_fn=lambda *_: "Uploaded",
        unique_id_fn=unique_id_fn,
        value_fn=client_upload_value_fn
    ),
    RX_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=RX_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfDataRate.MEGABYTES_PER_SECOND,
        has_entity_name=True,
        allowed_fn=lambda controller, mac: (controller.option_client_bandwidth_sensors and
                                            controller.option_track_clients and
                                            controller.is_client_allowed(mac)),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=client_device_info_fn,
        name_fn=lambda *_: "RX Activity",
        unique_id_fn=unique_id_fn,
        value_fn=client_rx_value_fn
    ),
    TX_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=TX_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfDataRate.MEGABYTES_PER_SECOND,
        has_entity_name=True,
        allowed_fn=lambda controller, mac: (controller.option_client_bandwidth_sensors and
                                            controller.option_track_clients and
                                            controller.is_client_allowed(mac)),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=client_device_info_fn,
        name_fn=lambda *_: "TX Activity",
        unique_id_fn=unique_id_fn,
        value_fn=client_tx_value_fn
    ),
    UPTIME_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=UPTIME_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=DEVICE_CLASS_TIMESTAMP,
        has_entity_name=True,
        allowed_fn=lambda controller, mac: (controller.option_client_uptime_sensor and
                                            controller.option_track_clients and
                                            controller.is_client_allowed(mac)),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=client_device_info_fn,
        name_fn=lambda *_: "Uptime",
        unique_id_fn=unique_id_fn,
        value_fn=client_uptime_value_fn
    ),
}

DEVICE_ENTITY_DESCRIPTIONS: Dict[str, OmadaSensorEntityDescription] = {
    DOWNLOAD_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=DOWNLOAD_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_bandwidth_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "Downloaded",
        unique_id_fn=unique_id_fn,
        value_fn=device_download_value_fn
    ),
    UPLOAD_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=UPLOAD_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_bandwidth_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "Uploaded",
        unique_id_fn=unique_id_fn,
        value_fn=device_upload_value_fn
    ),
    RX_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=RX_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfDataRate.MEGABYTES_PER_SECOND,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_bandwidth_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "RX Activity",
        unique_id_fn=unique_id_fn,
        value_fn=device_rx_value_fn
    ),
    TX_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=TX_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfDataRate.MEGABYTES_PER_SECOND,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_bandwidth_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "TX Activity",
        unique_id_fn=unique_id_fn,
        value_fn=device_tx_value_fn
    ),
    CPU_USAGE_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=CPU_USAGE_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_statistics_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "CPU Usage",
        unique_id_fn=unique_id_fn,
        value_fn=device_cpu_value_fn
    ),
    MEMORY_USAGE_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=MEMORY_USAGE_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_statistics_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "Memory Usage",
        unique_id_fn=unique_id_fn,
        value_fn=device_memory_value_fn
    ),
    UPTIME_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=UPTIME_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=DEVICE_CLASS_TIMESTAMP,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_statistics_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "Uptime",
        unique_id_fn=unique_id_fn,
        value_fn=device_uptime_value_fn
    ),
    CLIENTS_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=CLIENTS_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=CLIENTS,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_clients_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "Clients",
        unique_id_fn=unique_id_fn,
        value_fn=device_clients_value_fn
    ),
    CLIENTS_2G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=CLIENTS_2G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=CLIENTS,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_clients_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda controller, mac: controller.api.devices[mac].radio_enabled_2ghz,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "2.4Ghz Clients",
        unique_id_fn=unique_id_fn,
        value_fn=device_clients_2g_value_fn
    ),
    CLIENTS_5G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=CLIENTS_5G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=CLIENTS,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_clients_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda controller, mac: controller.api.devices[mac].radio_enabled_5ghz,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "5Ghz Clients",
        unique_id_fn=unique_id_fn,
        value_fn=device_clients_5g_value_fn
    ),
    CLIENTS_6G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=CLIENTS_6G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=CLIENTS,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_clients_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda controller, mac: controller.api.devices[mac].radio_enabled_6ghz,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "6Ghz Clients",
        unique_id_fn=unique_id_fn,
        value_fn=device_clients_6g_value_fn
    ),
    TX_UTILIZATION_2G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=TX_UTILIZATION_2G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_radio_utilization_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "2.4Ghz TX Utilization",
        unique_id_fn=unique_id_fn,
        value_fn=device_tx_utilization_2g_value_fn
    ),
    TX_UTILIZATION_5G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=TX_UTILIZATION_5G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_radio_utilization_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda controller, mac: controller.api.devices[mac].radio_enabled_5ghz,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "5Ghz TX Utilization",
        unique_id_fn=unique_id_fn,
        value_fn=device_tx_utilization_5g_value_fn
    ),
    TX_UTILIZATION_6G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=TX_UTILIZATION_6G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_radio_utilization_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda controller, mac: controller.api.devices[mac].radio_enabled_6ghz,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "6Ghz TX Utilization",
        unique_id_fn=unique_id_fn,
        value_fn=device_tx_utilization_6g_value_fn
    ),
    RX_UTILIZATION_2G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=RX_UTILIZATION_2G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_radio_utilization_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda controller, mac: controller.api.devices[mac].radio_enabled_2ghz,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "2.4Ghz RX Utilization",
        unique_id_fn=unique_id_fn,
        value_fn=device_rx_utilization_2g_value_fn
    ),
    RX_UTILIZATION_5G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=RX_UTILIZATION_5G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_radio_utilization_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda controller, mac: controller.api.devices[mac].radio_enabled_5ghz,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "5Ghz RX Utilization",
        unique_id_fn=unique_id_fn,
        value_fn=device_rx_utilization_5g_value_fn
    ),
    RX_UTILIZATION_6G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=RX_UTILIZATION_6G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_radio_utilization_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda controller, mac: controller.api.devices[mac].radio_enabled_6ghz,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "6Ghz RX Utilization",
        unique_id_fn=unique_id_fn,
        value_fn=device_rx_utilization_6g_value_fn
    ),
    INTER_UTILIZATION_2G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=INTER_UTILIZATION_2G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_radio_utilization_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda *_: True,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "2.4Ghz Interference",
        unique_id_fn=unique_id_fn,
        value_fn=device_inter_utilization_2g_value_fn
    ),
    INTER_UTILIZATION_5G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=INTER_UTILIZATION_5G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_radio_utilization_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda controller, mac: controller.api.devices[mac].radio_enabled_5ghz,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "5Ghz Interference",
        unique_id_fn=unique_id_fn,
        value_fn=device_inter_utilization_5g_value_fn
    ),
    INTER_UTILIZATION_6G_SENSOR: OmadaSensorEntityDescription(
        domain=DOMAIN,
        key=INTER_UTILIZATION_6G_SENSOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        has_entity_name=True,
        allowed_fn=lambda controller, _: (controller.option_device_radio_utilization_sensors and
                                          controller.option_track_devices),
        supported_fn=lambda controller, mac: controller.api.devices[mac].radio_enabled_6ghz,
        available_fn=lambda controller, _: controller.available,
        device_info_fn=device_device_info_fn,
        name_fn=lambda *_: "6Ghz Interference",
        unique_id_fn=unique_id_fn,
        value_fn=device_inter_utilization_6g_value_fn
    )
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    controller: OmadaController = hass.data[OMADA_DOMAIN][config_entry.entry_id]

    @callback
    def items_added() -> None:

        if controller.option_track_clients:
            controller.register_platform_entities(
                controller.api.clients,
                OmadaSensorEntity,
                CLIENT_ENTITY_DESCRIPTIONS,
                async_add_entities)

        if controller.option_track_devices:
            controller.register_platform_entities(
                controller.api.devices,
                OmadaSensorEntity,
                DEVICE_ENTITY_DESCRIPTIONS,
                async_add_entities)

    for signal in (controller.signal_update, controller.signal_options_update):
        config_entry.async_on_unload(
            async_dispatcher_connect(hass, signal, items_added))

    if controller.option_track_clients:
        controller.restore_cleanup_platform_entities(
            DOMAIN,
            controller.api.clients,
            controller.api.known_clients,
            OmadaSensorEntity,
            CLIENT_ENTITY_DESCRIPTIONS,
            config_entry,
            async_add_entities
        )

    items_added()


class OmadaSensorEntity(OmadaEntity, SensorEntity):

    entity_description: OmadaSensorEntityDescription

    def __init__(self, mac: str, controller: OmadaController, description: OmadaEntityDescription) -> None:

        super().__init__(mac, controller, description)
        self._attr_native_value = self.entity_description.value_fn(
            self.controller, self._mac)

    @callback
    async def async_update(self):
        if ((value := self.entity_description.value_fn(self.controller, self._mac)) != self.native_value):
            self._attr_native_value = value
            await super().async_update()
