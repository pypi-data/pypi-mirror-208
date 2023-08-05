""".. module:: emulsion.tools.calendar

Classes and functions for the definition of Emulsion calendars.
"""


# EMULSION (Epidemiological Multi-Level Simulation framework)
# ===========================================================
# 
# Contributors and contact:
# -------------------------
# 
#     - Sébastien Picault (sebastien.picault@inrae.fr)
#     - Yu-Lin Huang
#     - Vianney Sicard
#     - Sandie Arnoux
#     - Gaël Beaunée
#     - Pauline Ezanno (pauline.ezanno@inrae.fr)
# 
#     INRAE, Oniris, BIOEPAR, 44300, Nantes, France
# 
# 
# How to cite:
# ------------
# 
#     S. Picault, Y.-L. Huang, V. Sicard, S. Arnoux, G. Beaunée,
#     P. Ezanno (2019). "EMULSION: Transparent and flexible multiscale
#     stochastic models in human, animal and plant epidemiology", PLoS
#     Computational Biology 15(9): e1007342. DOI:
#     10.1371/journal.pcbi.1007342
# 
# 
# License:
# --------
# 
#     Copyright 2016 INRAE and Univ. Lille
# 
#     Inter Deposit Digital Number: IDDN.FR.001.280043.000.R.P.2018.000.10000
# 
#     Agence pour la Protection des Programmes,
#     54 rue de Paradis, 75010 Paris, France
# 
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
# 
#         http://www.apache.org/licenses/LICENSE-2.0
# 
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.


from   sortedcontainers      import SortedDict


#  ______                    _   _
# |  ____|                  | | (_)
# | |__  __  _____ ___ _ __ | |_ _  ___  _ __  ___
# |  __| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \/ __|
# | |____ >  < (_|  __/ |_) | |_| | (_) | | | \__ \
# |______/_/\_\___\___| .__/ \__|_|\___/|_| |_|___/
#                     | |
#                     |_|

class InvalidIntervalException(Exception):
    """Exception raised when trying to insert an inconsistent event in the
    calendar. An event is considered inconsistent if the begin date is
    posterior to the send date in a non-periodic calendar.

    """
    def __init__(self, begin, end):
        """Create the exception with the incorrect *begin* and *end* dates."""
        super().__init__()
        self.value = (begin, end)

    def __str__(self):
        return 'Invalid dates interval {}'.format(self.value)


#  ______                _   _
# |  ____|              | | (_)
# | |__ _   _ _ __   ___| |_ _  ___  _ __  ___
# |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# | |  | |_| | | | | (__| |_| | (_) | | | \__ \
# |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/

def date_in(begin, end, period=None):
    """Returns a callable class which tests if a date belongs to the
    specified interval (from *begin* to *end*). If a *period* is
    specified, the test relies upon the periodicity, otherwise dates
    are considered absolute.

    Parameters
    ----------
    begin: ``datetime.datetime``
        the date when the interval begins
    end: ``datetime.datetime``
        the date when the interval ends
    period: ``datetime.timedelta``
        the duration of the period after which the calendar cycles

    Returns
    -------
    class:
        a callable class which depends on relations between parameter
        values and can be called on a date (``datetime.datetime``) to
        return a ``bool`` which indicates whether or not the date
        belongs to the *begin*-*end* interval.

    Raises
    ------
    InvalidIntervalexception
        if *begin* is posterior to *end* in a non-periodic calendar

    """
    if period is not None:
        begin, end = begin % period, end % period
        if begin <= end:
            return periodic_date_tester(begin, end, period)
        else:
            return periodic_date_tester_inverted(begin, end, period)
    else:
        if begin <= end:
            return date_tester(begin, end)
        else:
            raise InvalidIntervalException(begin, end)

class periodic_date_tester:
    def __init__(self, begin, end, period):
        self.begin = begin
        self.end = end
        self.period = period

    def __call__(self, date):
        """Check that the specified date belongs to the event interval,
            considering the periodicity.

        """
        return self.begin <= (date % self.period) <= self.end

class periodic_date_tester_inverted:
    def __init__(self, begin, end, period):
        self.begin = begin
        self.end = end
        self.period = period
    def __call__(self, date):
        """Check that the specified date belongs to the event interval,
           considering the periodicity and the fact that the end date
           appears before the begin date in a civil year.

        """
        return (date % self.period) <= self.end or (date % self.period) >= self.begin

class date_tester:
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end

    def __call__(self, date):
        """Check that the specified date belongs to the event interval,
        considered as absolute (no periodicity).

        """
        return self.begin <= date <= self.end


#  ______               _    _____      _                _
# |  ____|             | |  / ____|    | |              | |
# | |____   _____ _ __ | |_| |     __ _| | ___ _ __   __| | __ _ _ __
# |  __\ \ / / _ \ '_ \| __| |    / _` | |/ _ \ '_ \ / _` |/ _` | '__|
# | |___\ V /  __/ | | | |_| |___| (_| | |  __/ | | | (_| | (_| | |
# |______\_/ \___|_| |_|\__|\_____\__,_|_|\___|_| |_|\__,_|\__,_|_|


class EventCalendar:
    """The EventCalendar class is intended to handle events and
    periods of time. Dates/times are given to the calendar in a
    human-readable format, and converted to integers (simulation
    steps).

    """
    def __init__(self, calendar_name, step_duration, origin,
                 period=None, **initial_dates):
        """Initialize the calendar using the specified information.

        Parameters
        ----------
        calendar_name: string
            the name of the calendar
        step_duration: ``datetime.timedelta``
            actual duration of one simulation step
        origin: ``datetime.datetime``
            date/time value of the beginning of the calendar
        period: ``datetime.timedelta``
            if the calendar is periodic, actual duration of the
            period, None otherwise
        initial_dates: dict
             initial dictionary of events (event name as key, dict as
             value with either begin/end dates or one single date if
             punctual event)

        """
        self.calendar_name = calendar_name
        self.step = 0
        self.step_duration = step_duration
        self.origin = origin
        self.current_date = self.origin
        self.events = SortedDict()
        self.description = SortedDict()
        self.period = None if period is None\
          else period // self.step_duration
        for name, value in initial_dates.items():
            self.add_event(name, value)


    def increment(self, steps=1):
        """Advance the current date by the specified number of
        simulation steps.

        Parameters
        ----------
        steps: int
            number of steps to 'add' to the current date
        """
        self.current_date += self.step_duration * steps

    def step_to_date(self, step):
        """Return the date when the specified step begins.

        Parameters
        ----------
        step: int
            the time step to convert to a date

        Returns
        -------
        d: ``datetime.datetime``
            the corresponding date
        """
        return self.origin + self.step_duration * step

    def date_to_step(self, date):
        """Return the step corresponding the specified date.

        Parameters
        ----------
        date: ``datetime.datetime``
            the date to convert into time steps

        Returns
        -------
        t: int
            the time step during which the specified date occurs (the
            date occurs between the returned time step *t* and time
            step *t+1*)

        """
        return (date - self.origin) // self.step_duration


    def add_event(self, name, begin_end):
        """Add the specified event to the calendar. An event is characterized
        by its *name* and a *begin_end* tuple indicating the begin and
        end dates.

        Parameters
        ----------
        name: str
            the name of the event
        begin_end: tuple
           a tuple composed of the begin date and the end date
           (possibly identical for handling punctual events)

        """
        begin_date, end_date = begin_end
        begin = self.date_to_step(begin_date)
        end = self.date_to_step(end_date)
        if end < begin and self.period is None:
            raise InvalidIntervalException(begin, end)
        self.description[name] = begin_end
        self.events[name] = date_in(begin, end, self.period)

    def get_events(self):
        """Return the list of events contained in the current calendar.

        Returns
        -------
        l: list
            the list of all event names
        """
        return list(self.description.keys())

    def __getitem__(self, name):
        return self.events[name]
