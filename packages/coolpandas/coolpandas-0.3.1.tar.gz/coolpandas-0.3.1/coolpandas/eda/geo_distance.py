"""GeoDistance module for calculating road distances between two points on Earth."""
import time
import warnings
from math import asin, cos, radians, sin, sqrt

import openrouteservice
from openrouteservice.exceptions import ApiError


class GeoDistance:
    """GeoDistance class for calculating road distances between two points on Earth.

    Attributes:
        api_keys (list[str]): List of API keys for the OpenRouteService API.
        client (openrouteservice.Client): Client for the OpenRouteService API.

    Methods:
        get_geodistance(origin_latitude: float, origin_longitude: float,
        destination_latitude: float, destination_longitude: float) -> float:

    """

    api_keys: list[str]
    client: openrouteservice.Client

    def __init__(self, api_keys: list[str] = []) -> None:
        """Initialize GeoDistance class.

        Args:
            api_keys (list[str]): List of API keys for the OpenRouteService API.
            Defaults to [].
        """
        if api_keys:
            self.api_keys = api_keys
            self.client = self._initialize_client(self.api_keys[0])

    @staticmethod
    def _initialize_client(api_key: str) -> openrouteservice.Client:
        """Initialize OpenRouteService client.

        Args:
            api_key (str): API key for the OpenRouteService API.
        """
        client = openrouteservice.Client(api_key)
        return client

    def get_openroute_distance(
        self,
        origin_latitude: float,
        origin_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
        null_value: any = None,
    ) -> tuple[float, float]:
        """Calculate road distance between two points on Earth.

        Args:
            origin_latitude (float): Latitude of origin point.
            origin_longitude (float): Longitude of origin point.
            destination_latitude (float): Latitude of destination point.
            destination_longitude (float): Longitude of destination point.
            null_value (any, optional): Value to return if distance cannot be calculated.

        Returns:
            tuple[float, float]: Tuple of distance in meters and duration in seconds.
        """
        coords: tuple[tuple[int]] = (
            (origin_longitude, origin_latitude),
            (destination_longitude, destination_latitude),
        )
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            try:
                response: dict[str, dict] = self.client.directions(coords)
            except (UserWarning, ApiError) as exception:
                print(exception)
                if len(self.api_keys) == 1:
                    raise IndexError("No more API keys available.") from exception
                self.api_keys.append(self.api_keys.pop(0))
                self.client = self._initialize_client(self.api_keys[0])
                time.sleep(2)
                return self.get_geodistance(
                    origin_latitude,
                    origin_longitude,
                    destination_latitude,
                    destination_longitude,
                )
        kilometers_distance: any = null_value
        minutes_distance: any = null_value
        try:
            kilometers_distance = response["routes"][0]["summary"]["distance"] / 1000
            minutes_distance = response["routes"][0]["summary"]["duration"] / 60
        except KeyError:
            pass
        return (kilometers_distance, minutes_distance)

    def get_harvesine_distance(
        self,
        origin_latitude: float,
        origin_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
    ) -> float:
        """Calculate the distance in kilometers between two points on the earth.

        Args:
            origin_latitude (float): Latitude of origin point.
            origin_longitude (float): Longitude of origin point.
            destination_latitude (float): Latitude of destination point.
            destination_longitude (float): Longitude of destination point.

        Returns:
            float: Distance in kilometers.
        """
        lon1, lat1, lon2, lat2 = map(
            radians,
            [
                origin_longitude,
                origin_latitude,
                destination_longitude,
                destination_latitude,
            ],
        )
        dlon: float = lon2 - lon1
        dlat: float = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return 6371 * c
