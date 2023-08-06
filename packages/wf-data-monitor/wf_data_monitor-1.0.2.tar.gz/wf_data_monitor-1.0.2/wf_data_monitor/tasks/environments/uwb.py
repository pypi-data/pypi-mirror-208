from datetime import datetime, timedelta
from typing import Optional

import dateutil
import pandas as pd

from wf_data_monitor.honeycomb_db.handle import HoneycombDBHandle
from wf_data_monitor.log import logger
from wf_data_monitor.notifications import notifier


def verify_uwb_capture(
    honeycomb_handle: HoneycombDBHandle,
    environment_id: str,
    environment_name: str,
    classroom_start_time: datetime,
    classroom_end_time: datetime,
    timezone: dateutil.tz,
    upload_delay: int = 13,
):
    alert_messages = []
    tz_aware_datetime_now = datetime.now(tz=timezone)
    # tz_aware_datetime_now = datetime.strptime("2023-04-07 15:55:00-0700", "%Y-%m-%d %H:%M:%S%z")
    minutes = 30

    if ((tz_aware_datetime_now - classroom_start_time).total_seconds() / 60) <= upload_delay:
        logger.warning(
            f"UWB validation started, but waiting to run validations until the upload_delay of {upload_delay} minutes has passed"
        )
        return

    logger.info(f"Verifying UWB capture for {environment_name}")
    # TODO: Consider removing devices operating in WoS
    df_positions = honeycomb_handle.query_positions(
        environment_name=environment_name,
        start_time=tz_aware_datetime_now - timedelta(minutes=minutes),
        end_time=tz_aware_datetime_now,
    )

    df_positions_without_wos = _remove_wos_signal(df_positions=df_positions)

    if len(df_positions) == 0:
        message = f"No positions found for {environment_name} between {classroom_start_time} - {classroom_end_time}"
        logger.warning(message)
        alert_messages.append(message)

    # Verify position data is flowing
    are_device_positions_reporting_properly, warning_message = _verify_recent_data(
        df_positions=df_positions, end_time=tz_aware_datetime_now, valid_delay_threshold=upload_delay
    )
    if not are_device_positions_reporting_properly:
        alert_messages.append(warning_message)
    if warning_message is not None:
        logger.warning(f"_verify_recent_data method returned the following warning: {warning_message}")

    # Verify position data is relatively distributed over each minute
    is_data_evenly_distributed, _, warning_message = _verify_data_disbursement(
        df_positions=df_positions_without_wos,
        minutes=minutes,
        end_time=tz_aware_datetime_now,
    )
    if not is_data_evenly_distributed:
        alert_messages.append(warning_message)
    if warning_message is not None:
        logger.warning(
            f"_verify_data_disbursement method returned the following warning against {environment_name}: {warning_message}"
        )

    # # Verify devices are reporting data at a reasonable hertz
    # # DISABLED ON 5/16/2023 - WAS PRODUCING TOO MANY FALSE POSITIVES
    # # THE ISSUE WAS CAUSED BY TAGS HAVING POOR CONNECTIONS DUE TO VERY
    # # NATURAL AND EXPECTED REASONS (TAG OUTSIDE, IN BACK ROOM, ETC)
    # are_device_positions_reporting_properly, _, warning_message = _verify_per_device_hz(
    #     df_positions=df_positions_without_wos
    # )
    # if not are_device_positions_reporting_properly:
    #     alert_messages.append(warning_message)
    # if warning_message is not None:
    #     logger.warning(
    #         f"_verify_per_device_hz method returned the following warning against {environment_name}: {warning_message}"
    #     )

    if len(alert_messages) == 0:
        logger.info(f"UWB data for {environment_name} appears healthy")
    else:
        formatted_messages = "\n\n • ".join(alert_messages)
        message_args = {
            "subject": f"UWB Alert(s) for {environment_name}",
            "message": f"Validations run at (T): {tz_aware_datetime_now}\nValidations run with upload delay of {upload_delay} minutes\nTesting window from T-{minutes} to T-{upload_delay} ({tz_aware_datetime_now - timedelta(minutes=minutes)} - {tz_aware_datetime_now - timedelta(minutes=upload_delay)})\n\nLogged {len(alert_messages)} alerts against {environment_name}:\n\n{formatted_messages}",
        }
        logger.info(f"Raising alert(s): {message_args}")
        notifier.send_message(**message_args)


# The WoS behavior doesn't stop position updates. It slows updates to 1/60 hz (1 per minute)
def _remove_wos_signal(df_positions):
    df_positions = df_positions.copy()

    lst_positions_filtered: list[pd.DataFrame] = []
    grouped = df_positions.sort_values(by="position_timestamp").groupby("device_id")
    for device_id, df_positions_by_device in grouped:
        # diff() computes the amount of time that's passed between position records
        df_positions_by_device["time_diff"] = df_positions_by_device["position_timestamp"].diff()

        # diff() sets the first item's time difference value to NAT
        # update that first record to the median time_diff value
        df_positions_by_device.loc[df_positions_by_device.index[0], ["time_diff"]] = df_positions_by_device[
            "time_diff"
        ].median()

        # filter out position records that have lapsed over 55 seconds since the last position update.
        # These are the WoS records
        df_valid_positions = df_positions_by_device[
            df_positions_by_device["position_timestamp"].diff() <= pd.to_timedelta("50 seconds")
        ]
        lst_positions_filtered.append(df_valid_positions)

    if len(lst_positions_filtered) == 0:
        return None

    return pd.concat(lst_positions_filtered)


def _verify_data_disbursement(
    df_positions: Optional[pd.DataFrame], minutes: int, end_time: datetime, valid_device_threshold: int = 5
) -> (bool, pd.DataFrame, str):
    """
    Test disbursement of positions data by checking how many position updates
    are captured per 1 second block. Because of WoS, this test only works if there is some
    threshold of devices reporting their positions

    :param df_positions:
    :param minutes: How many minutes before end time to check disbursement
    :param end_time:
    :param valid_device_threshold:
    :return: (success, disbursement dataframe, error message)
    """
    if df_positions is None or len(df_positions) == 0:
        return True, None, "No positions provided in the supplied df_positions object"

    # Skip this test if there are less than X devices emitting data
    # With WoS, the "even" data disbursement becomes less relevant with fewer devices
    if len(pd.unique(df_positions["device_id"])) < valid_device_threshold:
        return (
            True,
            None,
            f"Skipping test due to too few devices, found {len(pd.unique(df_positions['device_id']))} expected {valid_device_threshold}",
        )

    start_time = end_time - timedelta(minutes=minutes)

    sample_range_seconds_frequency = 1
    samples = pd.date_range(
        start=start_time,
        end=end_time,
        freq=pd.Timedelta(seconds=sample_range_seconds_frequency),
    )
    samples = pd.DatetimeIndex(pd.Series(samples).dt.round(f"{sample_range_seconds_frequency}S"))

    lst_sample_aggregates = []
    for sample in samples:
        positions_for_delta = df_positions[
            (
                (df_positions["position_timestamp"] >= sample)
                & (df_positions["position_timestamp"] < sample + pd.Timedelta(seconds=sample_range_seconds_frequency))
            )
        ]
        df_positions_summary_for_delta = (
            positions_for_delta.reset_index()
            .groupby("environment_id")
            .agg(
                N=("position_id", "count"),
                devices_unique_count=("device_id", "nunique"),
                data_rate_hz=("position_id", lambda x: x.count() / sample_range_seconds_frequency),
                quality_min=("position_quality", "min"),
                quality_max=("position_quality", "max"),
                anchor_count_min=("position_anchor_count", "min"),
                anchor_count_max=("position_anchor_count", "max"),
            )
            .assign(timestamp=sample)
            .set_index("timestamp")
        )
        lst_sample_aggregates.append(df_positions_summary_for_delta)

    df_sample_aggregates = pd.concat(lst_sample_aggregates)

    if len(df_sample_aggregates) == 0:
        return True, None, f"No positions found last {minutes} minutes"

    df_sample_aggregates["data_rate_hz_per_device"] = (
        df_sample_aggregates["data_rate_hz"] / df_sample_aggregates["devices_unique_count"]
    )
    df_sample_aggregates[f"seconds_grouper"] = df_sample_aggregates.index.strftime("%S")

    # Use grouper_every_ten_seconds to divide moments in 10 second long buckets. Then group on these buckets to get
    # an insight into average flow of data every 10s seconds. Look for instances where data is not evenly distributed.
    # df_positions_last_x_minutes = df_sample_aggregates[
    #     ((df_sample_aggregates.index >= classroom_end_time - pd.Timedelta(minutes=minutes)) & (df_sample_aggregates.index < classroom_end_time))
    # ]
    df_position_frequency_buckets = (
        df_sample_aggregates.reset_index()
        .groupby("seconds_grouper")
        .agg(
            N=("N", "sum"),
            data_rate_hz_mean=("data_rate_hz", "mean"),
            data_rate_hz_per_device_mean=("data_rate_hz_per_device", "mean"),
        )
    )

    df_position_frequency_buckets["n_distribution"] = (
        df_position_frequency_buckets["N"] / df_position_frequency_buckets["N"].sum()
    )
    # Test whether data is overly condensed
    #
    # Looks for grouping across all 60 seconds of every minute and tests if
    # data is over consolidating in a bucket. Fail if any one second has more
    # than 18% of the data
    message = None
    is_data_evenly_distributed = (df_position_frequency_buckets["n_distribution"] < 0.18).all()
    if not is_data_evenly_distributed:
        message = f"""UWB data is not evenly distributed over last {minutes} minutes. This may signify an issue proxying Ciholas' UDP port through Kubernetes.

{df_position_frequency_buckets.to_string()}
"""
    return is_data_evenly_distributed, df_position_frequency_buckets, message


def _verify_recent_data(
    df_positions: Optional[pd.DataFrame], end_time: datetime, valid_delay_threshold: int = 13
) -> (bool, str):
    are_position_updating_as_expected = False

    # Test if more than X minutes have passed since last position datapoint was captured
    # Data should get synced every 10 minutes plus 3 minutes for data processing
    last_position_timestamp = df_positions["position_timestamp"].max()
    if isinstance(last_position_timestamp, pd.Timestamp):
        minutes_since_last_position = (end_time - last_position_timestamp).total_seconds() / 60.0
        are_position_updating_as_expected = minutes_since_last_position <= valid_delay_threshold

        message = None
        if not are_position_updating_as_expected:
            message = f"No recorded sensor position in last {minutes_since_last_position} minutes. We expect no more than a {valid_delay_threshold} minute delay."
    else:
        are_position_updating_as_expected = False
        message = f"No recorded sensor position today. We expect no more than a {valid_delay_threshold} minute delay."

    return are_position_updating_as_expected, message


def _verify_per_device_hz(
    df_positions: Optional[pd.DataFrame], valid_hz_threshold: float = 3.0
) -> (bool, pd.DataFrame, str):
    df_positions = df_positions.copy()

    if df_positions is None or len(df_positions) == 0:
        return True, None, "No positions provided in the supplied df_positions object"

    lst_device_hz: list[dict] = []
    grouped = df_positions.sort_values(by="position_timestamp").groupby(["device_id", "device_name"])
    for (device_id, device_name), df_positions_by_device in grouped:
        lst_device_hz.append(
            {
                "device_id": device_id,
                "device_name": device_name,
                "device_hz": len(df_positions_by_device) / len(pd.unique(df_positions_by_device["position_timestamp"])),
            }
        )
    df_device_hz = pd.DataFrame(lst_device_hz)
    are_device_positions_reporting_properly = (df_device_hz["device_hz"] > valid_hz_threshold).all()

    message = None
    if not are_device_positions_reporting_properly:
        message = f"""Device position data hz is below threshold '{valid_hz_threshold}'
        
{df_device_hz.to_string()}
"""
    return are_device_positions_reporting_properly, df_device_hz, message
