"""Module containing the Activity class."""


class Activity:

    r"""Class representing an activity.

    Args:
    ----
        activity_type (str): Type of the activity (biking, running, ...)
        total_distance (float): Total distance of the activity in meters.
        duration (float): Duration of the activity in seconds.
        calories (float): Calories burned during the activity.
        hr_avg (float): Average heart rate during the activity.
        hr_min (float): Minimum heart rate during the activity.
        hr_max (float): Maximum heart rate during the activity.
        altitude_avg (float): Average altitude during the activity.
        altitude_min (float): Minimum altitude during the activity.
        altitude_max (float): Maximum altitude during the activity.
        ascent (float): Ascent during the activity.
        descent (float): Descent during the activity.
        speed_max (float): Maximum speed during the activity.
        speed_avg (float): Average speed during the activity.
        file_name (str): Name of the file containing the activity.
    """

    def __init__(
        self: 'Activity',
        activity_type: str = None,
        distance: float = None,
        duration: float = None,
        calories: float = None,
        hr_avg: float = None,
        hr_min: float = None,
        hr_max: float = None,
        altitude_avg: float = None,
        altitude_min: float = None,
        altitude_max: float = None,
        ascent: float = None,
        descent: float = None,
        speed_max: float = None,
        speed_avg: float = None,
        file_name: str = None,
    ) -> None:
        """Initialize the activity."""
        self.activity_type = activity_type
        self.duration = duration
        self.distance = distance
        self.calories = calories
        self.hr_avg = hr_avg
        self.hr_min = hr_min
        self.hr_max = hr_max
        self.altitude_avg = altitude_avg
        self.altitude_min = altitude_min
        self.altitude_max = altitude_max
        self.ascent = ascent
        self.descent = descent
        self.speed_max = speed_max
        self.speed_avg = speed_avg
        self.file_name = file_name

    def __str__(self: 'Activity') -> str:
        """Return the string representation of the activity."""
        return (
            f'Activity: {self.activity_type}, '
            f'Total duration: {self.duration} seconds, '
            f'Total distance: {self.distance} meters, '
            f'Calories burned: {self.calories}, '
            f'Average hertrate: {self.hr_avg}, '
            f'Minimum heartrate: {self.hr_min}, '
            f'Maximum heartrate: {self.hr_max}, '
            f'Average altitude: {self.altitude_avg}, '
            f'Minimum altitude: {self.altitude_min}, '
            f'Maximum altitude: {self.altitude_max}, '
            f'Ascent: {self.ascent}, '
            f'Descent: {self.descent}, '
            f'Maximum speed: {self.speed_max}, '
            f'Average speed: {self.speed_avg}, '
            f'Original filename: {self.file_name}'
        )

    def get_activity_type(self: 'Activity') -> str:
        """Return the type of the activity."""
        return self.activity_type

    def get_total_duration(self: 'Activity') -> float:
        """Return the total duration of the activity."""
        return self.duration

    def get_total_distance(self: 'Activity') -> float:
        """Return total distance in seconds of the activity."""
        return self.distance

    def get_calories(self: 'Activity') -> float:
        """Return the calories burned during the activity."""
        return self.calories

    def get_avg_hr(self: 'Activity') -> float:
        """Return the average heartrate during the activity."""
        return self.hr_avg

    def get_min_hr(self: 'Activity') -> float:
        """Return the minimum heartrate during the activity."""
        return self.hr_min

    def get_max_hr(self: 'Activity') -> float:
        """Return the maximum heartrate during the activity."""
        return self.hr_max

    def get_avg_altitude(self: 'Activity') -> float:
        """Return the average altitude during the activity."""
        return self.altitude_avg

    def get_min_altitude(self: 'Activity') -> float:
        """Return the minimum altitude during the activity."""
        return self.altitude_min

    def get_max_altitude(self: 'Activity') -> float:
        """Return the maximum altitude during the activity."""
        return self.altitude_max

    def get_ascent(self: 'Activity') -> float:
        """Return the ascent during the activity."""
        return self.ascent

    def get_descent(self: 'Activity') -> float:
        """Return the descent during the activity."""
        return self.descent

    def get_max_speed(self: 'Activity') -> float:
        """Return the maximum speed during the activity."""
        return self.speed_max

    def get_avg_speed(self: 'Activity') -> float:
        """Return the average speed during the activity."""
        return self.speed_avg

    def get_file_name(self: 'Activity') -> str:
        """Return the original filename of the activity."""
        return self.file_name
