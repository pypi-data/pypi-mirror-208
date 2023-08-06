from datetime import datetime, timedelta

import pandas as pd
import dateutil

from wf_data_monitor.log import logger
from wf_data_monitor.notifications import notifier
from wf_data_monitor.video_service import VideoClient


def verify_video_capture(
    environment_id: str,
    environment_name: str,
    classroom_start_time: datetime,
    classroom_end_time: datetime,
    timezone: dateutil.tz,
    upload_delay: int = 10,
):
    alert_messages = []
    # tz_aware_datetime_now = datetime.strptime("2023-04-07 10:05:00-0700", "%Y-%m-%d %H:%M:%S%z")
    tz_aware_datetime_now = datetime.now(tz=timezone)
    minutes = 30

    if ((tz_aware_datetime_now - classroom_start_time).total_seconds() / 60) <= upload_delay:
        logger.warning(
            f"Video capture validation started, but waiting to run validations until the upload_delay of {upload_delay} minutes has passed"
        )
        return

    logger.info(f"Verifying Video capture for {environment_name}")

    video_client = VideoClient()
    df_video_metadata = video_client.fetch_video_metadata(
        environment_id=environment_id,
        start=tz_aware_datetime_now - timedelta(minutes=minutes),
        end=tz_aware_datetime_now,
        output_format="dataframe",
    )
    # pre - abandon check if we just haven't had enough time for a video to have uploaded

    are_all_cameras_reporting, _, warning_message = _verify_all_cameras_reporting(
        environment_id=environment_id, df_video_metadata=df_video_metadata, video_client=video_client
    )
    if not are_all_cameras_reporting:
        alert_messages.append(warning_message)
    if warning_message is not None:
        logger.warning(
            f"_verify_all_cameras_reporting method returned the following warning against {environment_name}: {warning_message}"
        )

    is_video_data_continuous, _, warning_message = _verify_continous_video_feed(
        df_video_metadata=df_video_metadata,
        minutes=minutes,
        end_time=tz_aware_datetime_now,
        valid_delay_threshold=upload_delay,
    )
    if not is_video_data_continuous:
        alert_messages.append(warning_message)
    if warning_message is not None:
        logger.warning(
            f"_verify_continous_video_feed method returned the following warning against {environment_name}: {warning_message}"
        )

    if len(alert_messages) == 0:
        logger.info(f"Video upload data for {environment_name} appears healthy")
    else:
        formatted_messages = "\n\n • ".join(alert_messages)
        message_args = {
            "subject": f"Video Upload Alert(s) for {environment_name}",
            "message": f"Validations run at (T): {tz_aware_datetime_now}\nValidations run with upload delay of {upload_delay} minutes\nTesting window from T-{minutes} to T-{upload_delay} ({tz_aware_datetime_now - timedelta(minutes=minutes)} - {tz_aware_datetime_now - timedelta(minutes=upload_delay)})\n\nLogged {len(alert_messages)} alerts against {environment_name}:\n\n{formatted_messages}",
        }
        logger.info(f"Raising alert(s): {message_args}")
        notifier.send_message(**message_args)


def _verify_all_cameras_reporting(environment_id: str, df_video_metadata: pd.DataFrame, video_client: VideoClient):
    """
    # Verify all cameras are reporting videos

    :param environment_id:
    :param df_video_metadata:
    :param video_client:
    :return:
    """
    expected_cameras = video_client.fetch_active_cameras(environment_id=environment_id)

    message = None
    if len(df_video_metadata) == 0:
        message = "No videos captured in classroom. The classroom might have a connectivity issues, the control PC may be down/unresponsive, or the upload tooling may be failing"
        return False, None, message

    cameras_reporting = pd.unique(df_video_metadata["device_id"])

    # expected_cameras.index contains camera device_ids
    missing_camera_ids = expected_cameras.index.difference(cameras_reporting)

    if len(missing_camera_ids) > 0:
        df_missing_cameras = expected_cameras.loc[missing_camera_ids]
        return (
            False,
            df_missing_cameras,
            f"""Expected {len(expected_cameras)} cameras, found {len(cameras_reporting)} cameras reporting. Missing cameras:

{df_missing_cameras.to_string()}  
""",
        )

    return True, None, None


def _verify_continous_video_feed(
    df_video_metadata: pd.DataFrame, minutes: int, end_time: datetime, valid_delay_threshold: int = 10
):
    """
    Check if there are gaps in video data

    :param df_video_metadata:
    :param minutes:
    :param end_time:
    :param valid_delay_threshold:
    :return:
    """
    if len(df_video_metadata) == 0:
        message = "No videos captured in classroom, video feed inconsistent by default"
        return False, None, message

    # df_count_by_device_id = df_video_metadata.groupby(['device_id'], as_index=False).size()

    # Define a "validation" start/end window. We're not concerned with data outside this window because:
    # 1. The video data has not uploaded yet
    # 2. We don't want to keep triggering the same errors over and over
    #    even if the issue that caused the original alert was resolved moving forward
    validation_start_time = (end_time - timedelta(minutes=minutes)).astimezone(dateutil.tz.UTC)
    validation_end_time = (end_time - timedelta(minutes=valid_delay_threshold)).astimezone(dateutil.tz.UTC)
    expected_times_in_utc = pd.date_range(
        start=validation_start_time,
        end=validation_end_time,
        freq=pd.Timedelta(seconds=10),
    )
    expected_times_in_utc = pd.DatetimeIndex(pd.Series(expected_times_in_utc).dt.round("10S"))

    lst_missing_videos_by_device = []
    grouped = df_video_metadata.groupby(["device_id", "device_name"])
    for (device_id, device_name), df_videos_by_device_id in grouped:
        missing_video_timestamps = expected_times_in_utc.difference(
            pd.DatetimeIndex(df_videos_by_device_id["video_timestamp"])
        )

        lst_missing_videos_by_device.append(
            {
                "device_id": device_id,
                "device_name": device_name,
                "missing_videos_count": len(missing_video_timestamps),
                "missing_video_timestamps": missing_video_timestamps.map(str).to_list(),
            }
        )

    df_missing_videos_by_device = pd.DataFrame(lst_missing_videos_by_device)

    message = None
    is_video_data_continuous = (df_missing_videos_by_device["missing_videos_count"] >= 0).all()
    if not is_video_data_continuous:
        message = f"""Some camera devices video missing. Expected {len(expected_times_in_utc)} videos per camera between {validation_start_time} - {validation_end_time}:
        
{df_missing_videos_by_device.to_string()}
"""
    return is_video_data_continuous, df_missing_videos_by_device, message
