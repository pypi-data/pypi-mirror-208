"""Helper classes for using auto-generated API."""
# pylint: disable=line-too-long too-many-instance-attributes too-many-public-methods

import asyncio
import json
import logging
import re
from datetime import time
from threading import Thread
from types import SimpleNamespace

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from inflection import underscore
from mozart_api.api.mozart_api import MozartApi
from mozart_api.api_client import ApiClient
from mozart_api.configuration import Configuration

RECONNECT_INTERVAL: float = 15.0
WEBSOCKET_HEARTBEAT: float = 10
WEBSOCKET_RECIEVE_TIMEOUT: float = 5.0

logger = logging.getLogger(__name__)


def refactor_name(notification_type: str) -> str:
    """Remove WebSocketEvent prefix from string and convert to snake_case."""
    return underscore(notification_type.removeprefix("WebSocketEvent"))


def time_to_seconds(time_object: time) -> int:
    """Convert time object to number of seconds."""
    return (time_object.hour * 60 * 60) + (time_object.minute * 60) + time_object.second


def check_valid_jid(jid: str) -> bool:
    """Check if a JID is valid."""
    pattern = re.compile(r"(^\d{4})[.](\d{7})[.](\d{8})(@products\.bang-olufsen\.com)$")

    if pattern.fullmatch(jid) is not None:
        return True

    return False


class MozartClient(MozartApi):
    """User friendly setup for a Mozart device."""

    def __init__(
        self,
        host: str,
        websocket_reconnect: bool = False,
        websocket_reconnect_interval: float = RECONNECT_INTERVAL,
    ) -> None:
        """Initialize Mozart device."""
        self.host: str = host
        self.websocket_connected: bool = False
        self.websocket_reconnect: bool = websocket_reconnect
        self._websocket_reconnect_interval: float = websocket_reconnect_interval

        self._websocket_threads: set[Thread] = set()
        self._websocket_active: bool = False

        self._on_connection_lost = None
        self._on_connection = None

        self._on_all_notifications = None
        self._on_all_notifications_raw = None

        self._on_active_hdmi_input_signal_notification = None
        self._on_active_listening_mode_notification = None
        self._on_active_speaker_group_notification = None
        self._on_alarm_timer_notification = None
        self._on_alarm_triggered_notification = None
        self._on_battery_notification = None
        self._on_beo_remote_button_notification = None
        self._on_beolink_experiences_result_notification = None
        self._on_beolink_join_result_notification = None
        self._on_button_notification = None
        self._on_curtains_notification = None
        self._on_hdmi_video_format_signal_notification = None
        self._on_notification_notification = None
        self._on_playback_error_notification = None
        self._on_playback_metadata_notification = None
        self._on_playback_progress_notification = None
        self._on_playback_source_notification = None
        self._on_playback_state_notification = None
        self._on_power_state_notification = None
        self._on_puc_install_remote_id_status_notification = None
        self._on_role_notification = None
        self._on_room_compensation_current_measurement_event_notification = None
        self._on_room_compensation_state_notification = None
        self._on_software_update_state_notification = None
        self._on_sound_settings_notification = None
        self._on_source_change_notification = None
        self._on_speaker_group_changed_notification = None
        self._on_stand_connected_notification = None
        self._on_stand_position_notification = None
        self._on_tv_info_notification = None
        self._on_volume_notification = None
        self._on_wisa_out_state_notification = None

        # Configure MozartApi object.
        configuration = Configuration(host=self.host)
        configuration.verify_ssl = False

        super().__init__(ApiClient(configuration))

    def connect_notifications(self, remote_control=False) -> None:
        """Start the WebSocket listener thread."""
        if self._websocket_active:
            # Check if only the remote control listener should be started
            if len(self._websocket_threads) == 1 and remote_control is True:
                pass
            else:
                logger.warning("WebSocket listener(s) already running")
                return

        else:
            self._websocket_active = True

            # Always add main WebSocket listener
            self._websocket_threads.add(
                Thread(
                    name=f"{self.host} - listener thread",
                    target=self._start_websocket_listener,
                    args=(f"ws://{self.host}:9339/",),
                )
            )

        # Add WebSocket listener for remote control events if defined.
        if remote_control:
            self._websocket_threads.add(
                Thread(
                    name=f"{self.host} - remote listener thread",
                    target=self._start_websocket_listener,
                    args=(f"ws://{self.host}:9339/remoteControl",),
                )
            )

        for websocket_thread in self._websocket_threads:
            if websocket_thread.is_alive():
                continue
            websocket_thread.start()

    def disconnect_notifications(self) -> None:
        """Stop the WebSocket listener threads. May take a few seconds to complete, non-blocking."""
        # Don't try to close the WebSocket listener(s) if already closed
        if not self._websocket_active:
            logger.warning("WebSocket listener(s) already closed")
            return

        self._websocket_active = False

        # Start a new thread to kill the threads with blocking code
        Thread(
            name=f"{self.host} - websocket listener closer",
            target=self._stop_websocket_listeners,
        ).start()

    def _stop_websocket_listeners(self) -> None:
        """Stop running blocking threads."""
        for websocket_thread in self._websocket_threads:
            websocket_thread.join()

        self.websocket_connected = False
        self._websocket_threads = set()

    def _start_websocket_listener(self, host: str) -> None:
        """Start the async WebSocket listener."""
        asyncio.run(self._websocket_listener(host))

    async def _websocket_listener(self, host: str) -> None:
        """WebSocket listener."""
        while True:
            try:
                async with ClientSession() as session:
                    async with session.ws_connect(
                        url=host, heartbeat=WEBSOCKET_RECIEVE_TIMEOUT
                    ) as websocket:
                        self.websocket_connected = True

                        if self._on_connection:
                            self._on_connection()

                        while self._websocket_active:
                            # Receive JSON in order to get the Websocket notification name for deserialization
                            try:
                                notification = await asyncio.wait_for(
                                    websocket.receive_json(),
                                    timeout=WEBSOCKET_RECIEVE_TIMEOUT,
                                )

                                # Ensure that any notifications received after the disconnect command has been executed are not processed
                                if not self._websocket_active:
                                    break

                                self._on_message(notification)
                            except asyncio.TimeoutError:
                                pass

                        return

            except (ClientConnectorError, TypeError) as error:
                if self.websocket_connected:
                    self.websocket_connected = False

                    if self._on_connection_lost:
                        self._on_connection_lost()

                if not self.websocket_reconnect:
                    logger.error("%s : %s", host, error)
                    return

                await asyncio.sleep(self._websocket_reconnect_interval)

    def _on_message(self, notification) -> None:
        """Handle WebSocket notifications."""

        # Get the object type and deserialized object.
        try:
            notification_type = notification["eventType"]

            deserialized_data = self.api_client.deserialize(
                SimpleNamespace(data=json.dumps(notification)), notification_type
            ).event_data

            refactored_type = refactor_name(notification_type)

        except (ValueError, AttributeError) as error:
            logger.error(
                "Error deserializing WebSocket notification %s error %s",
                notification_type,
                error,
            )
            return

        # Ensure that only valid notifications trigger callbacks
        if deserialized_data is None:
            return

        # Handle all notifications if defined
        if self._on_all_notifications:
            self._on_all_notifications(deserialized_data, refactored_type)

        if self._on_all_notifications_raw:
            self._on_all_notifications_raw(notification)

        # Handle specific notifications if defined
        {
            "WebSocketEventActiveHdmiInputSignal": lambda notification: self._on_active_hdmi_input_signal_notification(
                notification
            )
            if self._on_active_hdmi_input_signal_notification
            else None,
            "WebSocketEventActiveListeningMode": lambda notification: self._on_active_listening_mode_notification(
                notification
            )
            if self._on_active_listening_mode_notification
            else None,
            "WebSocketEventActiveSpeakerGroup": lambda notification: self._on_active_speaker_group_notification(
                notification
            )
            if self._on_active_speaker_group_notification
            else None,
            "WebSocketEventAlarmTimer": lambda notification: self._on_alarm_timer_notification(
                notification
            )
            if self._on_alarm_timer_notification
            else None,
            "WebSocketEventAlarmTriggered": lambda notification: self._on_alarm_triggered_notification(
                notification
            )
            if self._on_alarm_triggered_notification
            else None,
            "WebSocketEventBattery": lambda notification: self._on_battery_notification(
                notification
            )
            if self._on_battery_notification
            else None,
            "WebSocketEventBeoRemoteButton": lambda notification: self._on_beo_remote_button_notification(
                notification
            )
            if self._on_beo_remote_button_notification
            else None,
            "WebSocketEventBeolinkExperiencesResult": lambda notification: self._on_beolink_experiences_result_notification(
                notification
            )
            if self._on_beolink_experiences_result_notification
            else None,
            "WebSocketEventBeolinkJoinResult": lambda notification: self._on_beolink_join_result_notification(
                notification
            )
            if self._on_beolink_join_result_notification
            else None,
            "WebSocketEventButton": lambda notification: self._on_button_notification(
                notification
            )
            if self._on_button_notification
            else None,
            "WebSocketEventCurtains": lambda notification: self._on_curtains_notification(
                notification
            )
            if self._on_curtains_notification
            else None,
            "WebSocketEventHdmiVideoFormatSignal": lambda notification: self._on_hdmi_video_format_signal_notification(
                notification
            )
            if self._on_hdmi_video_format_signal_notification
            else None,
            "WebSocketEventNotification": lambda notification: self._on_notification_notification(
                notification
            )
            if self._on_notification_notification
            else None,
            "WebSocketEventPlaybackError": lambda notification: self._on_playback_error_notification(
                notification
            )
            if self._on_playback_error_notification
            else None,
            "WebSocketEventPlaybackMetadata": lambda notification: self._on_playback_metadata_notification(
                notification
            )
            if self._on_playback_metadata_notification
            else None,
            "WebSocketEventPlaybackProgress": lambda notification: self._on_playback_progress_notification(
                notification
            )
            if self._on_playback_progress_notification
            else None,
            "WebSocketEventPlaybackSource": lambda notification: self._on_playback_source_notification(
                notification
            )
            if self._on_playback_source_notification
            else None,
            "WebSocketEventPlaybackState": lambda notification: self._on_playback_state_notification(
                notification
            )
            if self._on_playback_state_notification
            else None,
            "WebSocketEventPowerState": lambda notification: self._on_power_state_notification(
                notification
            )
            if self._on_power_state_notification
            else None,
            "WebSocketEventPucInstallRemoteIdStatus": lambda notification: self._on_puc_install_remote_id_status_notification(
                notification
            )
            if self._on_puc_install_remote_id_status_notification
            else None,
            "WebSocketEventRole": lambda notification: self._on_role_notification(
                notification
            )
            if self._on_role_notification
            else None,
            "WebSocketEventRoomCompensationCurrentMeasurementEvent": lambda notification: self._on_room_compensation_current_measurement_event_notification(
                notification
            )
            if self._on_room_compensation_current_measurement_event_notification
            else None,
            "WebSocketEventRoomCompensationState": lambda notification: self._on_room_compensation_state_notification(
                notification
            )
            if self._on_room_compensation_state_notification
            else None,
            "WebSocketEventSoftwareUpdateState": lambda notification: self._on_software_update_state_notification(
                notification
            )
            if self._on_software_update_state_notification
            else None,
            "WebSocketEventSoundSettings": lambda notification: self._on_sound_settings_notification(
                notification
            )
            if self._on_sound_settings_notification
            else None,
            "WebSocketEventSourceChange": lambda notification: self._on_source_change_notification(
                notification
            )
            if self._on_source_change_notification
            else None,
            "WebSocketEventSpeakerGroupChanged": lambda notification: self._on_speaker_group_changed_notification(
                notification
            )
            if self._on_speaker_group_changed_notification
            else None,
            "WebSocketEventStandConnected": lambda notification: self._on_stand_connected_notification(
                notification
            )
            if self._on_stand_connected_notification
            else None,
            "WebSocketEventStandPosition": lambda notification: self._on_stand_position_notification(
                notification
            )
            if self._on_stand_position_notification
            else None,
            "WebSocketEventTvInfo": lambda notification: self._on_tv_info_notification(
                notification
            )
            if self._on_tv_info_notification
            else None,
            "WebSocketEventVolume": lambda notification: self._on_volume_notification(
                notification
            )
            if self._on_volume_notification
            else None,
            "WebSocketEventWisaOutState": lambda notification: self._on_wisa_out_state_notification(
                notification
            )
            if self._on_wisa_out_state_notification
            else None,
        }[notification_type](deserialized_data)

    def get_on_connection_lost(self, on_connection_lost) -> None:
        """Callback for WebSocket connection lost."""
        self._on_connection_lost = on_connection_lost

    def get_on_connection(self, on_connection) -> None:
        """Callback for WebSocket connection."""
        self._on_connection = on_connection

    def get_all_notifications(self, on_all_notifications) -> None:
        """Callback for all notifications."""
        self._on_all_notifications = on_all_notifications

    def get_all_notifications_raw(self, on_all_notifications_raw) -> None:
        """Callback for all notifications as dict."""
        self._on_all_notifications_raw = on_all_notifications_raw

    def get_active_hdmi_input_signal_notifications(
        self, on_active_hdmi_input_signal_notification
    ) -> None:
        """Callback for WebSocketEventActiveHdmiInputSignal notifications."""
        self._on_active_hdmi_input_signal_notification = (
            on_active_hdmi_input_signal_notification
        )

    def get_active_listening_mode_notifications(
        self, on_active_listening_mode_notification
    ) -> None:
        """Callback for WebSocketEventActiveListeningMode notifications."""
        self._on_active_listening_mode_notification = (
            on_active_listening_mode_notification
        )

    def get_active_speaker_group_notifications(
        self, on_active_speaker_group_notification
    ) -> None:
        """Callback for WebSocketEventActiveSpeakerGroup notifications."""
        self._on_active_speaker_group_notification = (
            on_active_speaker_group_notification
        )

    def get_alarm_timer_notifications(self, on_alarm_timer_notification) -> None:
        """Callback for WebSocketEventAlarmTimer notifications."""
        self._on_alarm_timer_notification = on_alarm_timer_notification

    def get_alarm_triggered_notifications(
        self, on_alarm_triggered_notification
    ) -> None:
        """Callback for WebSocketEventAlarmTriggered notifications."""
        self._on_alarm_triggered_notification = on_alarm_triggered_notification

    def get_battery_notifications(self, on_battery_notification) -> None:
        """Callback for WebSocketEventBattery notifications."""
        self._on_battery_notification = on_battery_notification

    def get_beo_remote_button_notifications(
        self, on_beo_remote_button_notification
    ) -> None:
        """Callback for WebSocketEventBeoRemoteButton notifications."""
        self._on_beo_remote_button_notification = on_beo_remote_button_notification

    def get_beolink_experiences_result_notifications(
        self, on_beolink_experiences_result_notification
    ) -> None:
        """Callback for WebSocketEventBeolinkExperiencesResult notifications."""
        self._on_beolink_experiences_result_notification = (
            on_beolink_experiences_result_notification
        )

    def get_beolink_join_result_notifications(
        self, on_beolink_join_result_notification
    ) -> None:
        """Callback for WebSocketEventBeolinkJoinResult notifications."""
        self._on_beolink_join_result_notification = on_beolink_join_result_notification

    def get_button_notifications(self, on_button_notification) -> None:
        """Callback for WebSocketEventButton notifications."""
        self._on_button_notification = on_button_notification

    def get_curtains_notifications(self, on_curtains_notification) -> None:
        """Callback for WebSocketEventCurtains notifications."""
        self._on_curtains_notification = on_curtains_notification

    def get_hdmi_video_format_signal_notifications(
        self, on_hdmi_video_format_signal_notification
    ) -> None:
        """Callback for WebSocketEventHdmiVideoFormatSignal notifications."""
        self._on_hdmi_video_format_signal_notification = (
            on_hdmi_video_format_signal_notification
        )

    def get_notification_notifications(self, on_notification_notification) -> None:
        """Callback for WebSocketEventNotification notifications."""
        self._on_notification_notification = on_notification_notification

    def get_playback_error_notifications(self, on_playback_error_notification) -> None:
        """Callback for WebSocketEventPlaybackError notifications."""
        self._on_playback_error_notification = on_playback_error_notification

    def get_playback_metadata_notifications(
        self, on_playback_metadata_notification
    ) -> None:
        """Callback for WebSocketEventPlaybackMetadata notifications."""
        self._on_playback_metadata_notification = on_playback_metadata_notification

    def get_playback_progress_notifications(
        self, on_playback_progress_notification
    ) -> None:
        """Callback for WebSocketEventPlaybackProgress notifications."""
        self._on_playback_progress_notification = on_playback_progress_notification

    def get_playback_source_notifications(
        self, on_playback_source_notification
    ) -> None:
        """Callback for WebSocketEventPlaybackSource notifications."""
        self._on_playback_source_notification = on_playback_source_notification

    def get_playback_state_notifications(self, on_playback_state_notification) -> None:
        """Callback for WebSocketEventPlaybackState notifications."""
        self._on_playback_state_notification = on_playback_state_notification

    def get_power_state_notifications(self, on_power_state_notification) -> None:
        """Callback for WebSocketEventPowerState notifications."""
        self._on_power_state_notification = on_power_state_notification

    def get_puc_install_remote_id_status_notifications(
        self, on_puc_install_remote_id_status_notification
    ) -> None:
        """Callback for WebSocketEventPucInstallRemoteIdStatus notifications."""
        self._on_puc_install_remote_id_status_notification = (
            on_puc_install_remote_id_status_notification
        )

    def get_role_notifications(self, on_role_notification) -> None:
        """Callback for WebSocketEventRole notifications."""
        self._on_role_notification = on_role_notification

    def get_room_compensation_current_measurement_event_notifications(
        self, on_room_compensation_current_measurement_event_notification
    ) -> None:
        """Callback for WebSocketEventRoomCompensationCurrentMeasurementEvent notifications."""
        self._on_room_compensation_current_measurement_event_notification = (
            on_room_compensation_current_measurement_event_notification
        )

    def get_room_compensation_state_notifications(
        self, on_room_compensation_state_notification
    ) -> None:
        """Callback for WebSocketEventRoomCompensationState notifications."""
        self._on_room_compensation_state_notification = (
            on_room_compensation_state_notification
        )

    def get_software_update_state_notifications(
        self, on_software_update_state_notification
    ) -> None:
        """Callback for WebSocketEventSoftwareUpdateState notifications."""
        self._on_software_update_state_notification = (
            on_software_update_state_notification
        )

    def get_sound_settings_notifications(self, on_sound_settings_notification) -> None:
        """Callback for WebSocketEventSoundSettings notifications."""
        self._on_sound_settings_notification = on_sound_settings_notification

    def get_source_change_notifications(self, on_source_change_notification) -> None:
        """Callback for WebSocketEventSourceChange notifications."""
        self._on_source_change_notification = on_source_change_notification

    def get_speaker_group_changed_notifications(
        self, on_speaker_group_changed_notification
    ) -> None:
        """Callback for WebSocketEventSpeakerGroupChanged notifications."""
        self._on_speaker_group_changed_notification = (
            on_speaker_group_changed_notification
        )

    def get_stand_connected_notifications(
        self, on_stand_connected_notification
    ) -> None:
        """Callback for WebSocketEventStandConnected notifications."""
        self._on_stand_connected_notification = on_stand_connected_notification

    def get_stand_position_notifications(self, on_stand_position_notification) -> None:
        """Callback for WebSocketEventStandPosition notifications."""
        self._on_stand_position_notification = on_stand_position_notification

    def get_tv_info_notifications(self, on_tv_info_notification) -> None:
        """Callback for WebSocketEventTvInfo notifications."""
        self._on_tv_info_notification = on_tv_info_notification

    def get_volume_notifications(self, on_volume_notification) -> None:
        """Callback for WebSocketEventVolume notifications."""
        self._on_volume_notification = on_volume_notification

    def get_wisa_out_state_notifications(self, on_wisa_out_state_notification) -> None:
        """Callback for WebSocketEventWisaOutState notifications."""
        self._on_wisa_out_state_notification = on_wisa_out_state_notification
