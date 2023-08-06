from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock

from chaanbot.modules.weather import Weather


class TestWeather(IsolatedAsyncioTestCase):
    api_key = "123123"

    def setUp(self) -> None:
        config = Mock()
        config.get.return_value = self.api_key
        self.event = Mock()
        self.event.sender = "user_id"
        self.requests = Mock()
        self.room = AsyncMock()
        self.room.room_id = 1234
        self.matrix = AsyncMock()
        self.weather = Weather(config, self.matrix, Mock(), self.requests)

    def test_disabled_if_no_database(self):
        cfg = Mock()
        cfg.get.return_value = self.api_key
        self.weather = Weather(cfg, Mock(), None, Mock())
        self.assertTrue(self.weather.disabled)

    def test_disabled_if_no_api_key(self):
        cfg = Mock()
        cfg.get.return_value = None
        self.weather = Weather(cfg, Mock(), Mock(), Mock())
        self.assertTrue(self.weather.disabled)

    async def test_not_ran_if_wrong_command(self):
        ran = await self.weather.run(self.room, None, "weather")
        self.assertFalse(ran)

    def test_config_has_properties(self):
        self.assertLess(0, len(self.weather.operations))
        self.assertFalse(self.weather.always_run)

    async def test_send_todays_weather_if_no_argument(self):
        conn = Mock()
        latitude = 1.123
        longitude = -12.123
        self._mock_get_coordinates(conn, latitude, longitude)

        current_temp = 12
        min_temp = 45
        max_temp = 92
        summary = "Summary"
        response = Mock()
        self.requests.get.return_value = response
        response.json.return_value = {
            "current": {
                "temp": current_temp,
                "weather":
                    [
                        {
                            "description": summary
                        }
                    ]
            },
            "daily": [
                {
                    "temp": {
                        "min": min_temp,
                        "max": max_temp
                    }
                }
            ]
        }

        expected_send_message = "Currently: {} (Max: {}, Min: {})\t{}".format(current_temp, max_temp, min_temp,
                                                                              summary)

        await self.weather.run(self.room, self.event, "!weather")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)
        self.requests.get.assert_called_once()

    async def test_send_several_days_weather(self):
        conn = Mock()
        latitude = 1.123
        longitude = -12.123
        self._mock_get_coordinates(conn, latitude, longitude)

        min_temp1, min_temp2, min_temp3 = 45, 46, 47
        max_temp1, max_temp2, max_temp3 = 92, 93, 94
        summary1, summary2, summary3 = "Summary1", "Summary2", "Summary3"
        response = Mock()
        self.requests.get.return_value = response
        response.json.return_value = {
            "daily":
                [
                    {
                        "temp": {
                            "min": min_temp1,
                            "max": max_temp1
                        },
                        "weather": [
                            {
                                "description": summary1
                            }
                        ]
                    },
                    {
                        "temp": {
                            "min": min_temp2,
                            "max": max_temp2
                        },
                        "weather": [
                            {
                                "description": summary2
                            }
                        ]
                    },
                    {
                        "temp": {
                            "min": min_temp3,
                            "max": max_temp3
                        },
                        "weather": [
                            {
                                "description": summary3
                            }
                        ]
                    },
                ],
        }
        
        today = "{} Max: {}, Min: {}\t{}".format("Today\t\t\t", max_temp1, min_temp1, summary1)
        tomorrow = "{} Max: {}, Min: {}\t{}".format("Tomorrow\t\t", max_temp2, min_temp2, summary2)
        third_day = "{} Max: {}, Min: {}\t{}".format("2 days from now\t", max_temp3, min_temp3, summary3)
        expected_send_message = "{}\n{}\n{}\n".format(today, tomorrow, third_day)

        await self.weather.run(self.room, self.event, "!weather 0 1 2")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)
        self.requests.get.assert_called_once()

    async def test_cant_send_more_than_max_days(self):
        conn = Mock()
        latitude = 1.123
        longitude = 12.123
        self._mock_get_coordinates(conn, latitude, longitude)

        expected_send_message = "Can only look up {} days at once.".format(
            self.weather.max_days_to_send_at_once)

        message = "!weather "
        for i in range(self.weather.max_days_to_send_at_once + 1):
            message += "{} ".format(i)
        await self.weather.run(self.room, self.event, message)

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    async def test_remind_user_to_set_coordinates_if_trying_to_send_weather_without_coordinates_set(self):
        conn = Mock()
        self._mock_get_coordinates(conn, None, None)

        await self.weather.run(self.room, self.event, "!weather")

        expected_send_message = "Set your coordinates by using !setcoordinates [LATITUDE] [LONGITUDE]."
        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    def _mock_get_coordinates(self, conn, latitude, longitude):
        self.weather.database.connect.return_value = conn

        rows = Mock()
        conn.execute.return_value = rows
        rows.fetchone.return_value = (latitude, longitude)

    async def test_add_coordinates(self):
        conn = Mock()
        self._mock_add_coordinates(conn)

        latitude = 1.123
        longitude = -5.13
        expected_send_message = "Coordinates set to {},{}.".format(latitude, longitude)
        await self.weather.run(self.room, self.event, "!addcoordinates {}, {}".format(latitude, longitude))

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    def _mock_add_coordinates(self, conn):
        self.weather.database.connect.return_value = conn

        rows = Mock()
        conn.execute.return_value = rows

        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.lastrowid = 123

    async def test_max_two_digits_in_lat_and_long_when_adding_coordinates(self):
        latitude, longitude = 111, 5
        ran = await self.weather.run(self.room, self.event, "!addcoordinates {},{}".format(latitude, longitude))
        self.assertFalse(ran)

        latitude, longitude = 5, 111
        ran = await self.weather.run(self.room, self.event, "!addcoordinates {},{}".format(latitude, longitude))
        self.assertFalse(ran)
