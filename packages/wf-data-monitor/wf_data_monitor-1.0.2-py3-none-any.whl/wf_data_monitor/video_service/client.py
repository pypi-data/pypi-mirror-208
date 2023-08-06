from datetime import datetime
import os
import time
from typing import Optional, Union

import dateutil
import honeycomb_io
import minimal_honeycomb
import pandas as pd
import requests
import video_io

from wf_data_monitor.log import logger


class VideoClient:
    __instance = None

    def __new__(cls):
        # pylint: disable=access-member-before-definition
        # pylint: disable=protected-access

        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(
        self,
        url=None,
        auth_domain=None,
        auth_client_id=None,
        auth_client_secret=None,
        auth_audience=None,
    ):
        # pylint: disable=access-member-before-definition
        if self.__initialized:
            return
        self.__initialized = True

        url = os.getenv("HONEYCOMB_URI", "https://honeycomb.api.wildflower-tech.org/graphql")
        auth_domain = os.getenv("HONEYCOMB_DOMAIN", os.getenv("AUTH0_DOMAIN", "wildflowerschools.auth0.com"))
        auth_client_id = os.getenv("HONEYCOMB_CLIENT_ID", os.getenv("AUTH0_CLIENT_ID", None))
        auth_client_secret = os.getenv("HONEYCOMB_CLIENT_SECRET", os.getenv("AUTH0_CLIENT_SECRET", None))
        auth_audience = os.getenv("HONEYCOMB_AUDIENCE", os.getenv("API_AUDIENCE", "wildflower-tech.org"))

        if auth_client_id is None:
            raise ValueError("HONEYCOMB_CLIENT_ID (or AUTH0_CLIENT_ID) is required")
        if auth_client_secret is None:
            raise ValueError("HONEYCOMB_CLIENT_SECRET (or AUTH0_CLIENT_SECRET) is required")

        token_uri = os.getenv("HONEYCOMB_TOKEN_URI", f"https://{auth_domain}/oauth/token")

        self.client: minimal_honeycomb.MinimalHoneycombClient = honeycomb_io.generate_client(
            uri=url,
            token_uri=token_uri,
            audience=auth_audience,
            client_id=auth_client_id,
            client_secret=auth_client_secret,
        )

        self.client_params = {
            "client": self.client,
            "uri": url,
            "token_uri": token_uri,
            "audience": auth_audience,
            "client_id": auth_client_id,
            "client_secret": auth_client_secret,
        }

    def fetch_active_cameras(self, environment_id: str, output_format="dataframe") -> Union[pd.DataFrame, list[dict]]:
        now = datetime.now(tz=dateutil.tz.UTC)
        return honeycomb_io.fetch_camera_info(environment_id=environment_id, start=now, end=now, **self.client_params)

    def fetch_video_metadata(
        self, environment_id: str, start: datetime, end: datetime, output_format="dataframe"
    ) -> Union[pd.DataFrame, list[dict]]:
        def _fetch(retry=0):
            try:
                return video_io.fetch_video_metadata(
                    client=self.client,
                    start=start,
                    end=end,
                    environment_id=environment_id,
                )
            except requests.exceptions.HTTPError as e:
                logger.warning(f"video_io.fetch_video_metadata failed w/ {e.response.status_code} code: {e}")
                if retry >= 3:
                    logger.error(f"video_io.fetch_video_metadata failed and exhausted retry attempts")
                    return None

                time.sleep(0.5)
                return _fetch(retry + 1)

        video_metadata = _fetch()

        df_video_metadata = pd.DataFrame(video_metadata)
        if len(df_video_metadata) > 0:
            all_cameras = self.fetch_active_cameras(environment_id=environment_id)
            df_video_metadata = df_video_metadata.merge(
                all_cameras[["device_name"]], left_on="device_id", right_index=True
            )

        if output_format == "list":
            return df_video_metadata.to_dict("records")

        return df_video_metadata
