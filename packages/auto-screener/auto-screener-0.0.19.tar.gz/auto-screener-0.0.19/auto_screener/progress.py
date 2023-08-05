# progress.py

import sys
import warnings
import datetime as dt
import time
import threading
from typing import (
    Optional, Type, Generator,
    Iterable, Union, Any
)

from tqdm.auto import tqdm

from represent import BaseModel, Modifiers

from auto_screener.base import suppress
from auto_screener.hints import Number

__all__ = [
    "Spinner",
    "Progress",
    "progress",
    "spinner"
]

warnings.filterwarnings('ignore')

class Spinner(BaseModel):
    """
    A class to create a terminal spinning wheel.

    Using this object it is able to create a context manager for
    continuously print a progress wheel, and a message.

    attributes:

    - delay:
        The delay between output updates of iterations.

    - message:
        The printed message with the progress wheel.

    - silence:
        The value to silence the output.

    >>> from auto_screener.progress import Spinner
    >>>
    >>> with Spinner(message="Processing")
    >>>     while True:
    >>>         pass
    >>>     # end while
    >>> # end Spinner
    """

    modifiers = Modifiers(excluded=["spinner_generator"])

    RUNNING = False

    DELAY = 0.25

    instances = []

    def __init__(
            self,
            message: Optional[str] = None,
            delay: Optional[Union[Number, dt.timedelta]] = None,
            silence: Optional[bool] = None
    ) -> None:
        """
        Defines the class attributes.

        :param message: The message to display.
        :param delay: The delay value.
        :param silence: The value to hide the progress bar.
        """

        delay = delay or self.DELAY

        if isinstance(delay, dt.timedelta):
            delay = delay.total_seconds()
        # end if

        self.message = message

        self.spinner_generator = self.spinning_cursor()

        self.delay = delay

        self.silence = silence

        self.running = False
    # end __init__

    def spinning_cursor(self, message: Optional[str] = None) -> Generator[str, None, None]:
        """
        Returns the current spinner value.

        :param message: A message to display.

        :return: The current state of the cursor.
        """

        self.message = self.message or message
        message = message or self.message

        if not message:
            message = ""

        else:
            message += " "
        # end if

        while True:
            for cursor in '|/-\\':
                yield message + cursor
            # end for
        # end while
    # end spinning_cursor

    def spinner_task(self) -> None:
        """Runs the spinning wheel."""

        next_output = ""

        while self.running:
            Spinner.RUNNING = True

            next_output = next(self.spinner_generator)

            sys.stdout.write(next_output)
            sys.stdout.flush()

            if self.delay:
                time.sleep(self.delay)
            # end if

            sys.stdout.write('\b' * len(next_output))
            sys.stdout.flush()
        # end while

        sys.stdout.write('\b' * len(next_output))
        sys.stdout.flush()
    # end spinner_task

    def __enter__(self) -> None:
        """Enters the object to run the task."""

        if not self.silence:
            self.running = True

            threading.Thread(target=self.spinner_task).start()

            Spinner.instances.append(self)
        # end if
    # end __enter__

    def __exit__(
            self,
            exception_type: Type[Exception],
            exception: Exception,
            traceback
    ) -> Optional[bool]:
        """
        Exists the spinner object and ends the task.

        :param exception_type: The exception type.
        :param exception: The exception value.
        :param traceback: The traceback of the exception.

        :return: The status value
        """

        self.running = False

        Spinner.instances.remove(self)

        Spinner.RUNNING = bool(Spinner.instances)

        if self.delay:
            time.sleep(self.delay)
        # end if

        if exception is not None:
            return False
        # end if

        return True
    # end __exit__
# end Spinner

def spinner(
        delay: Optional[float] = None,
        message: Optional[str] = None,
        silence: Optional[bool] = None
) -> Spinner:
    """
    Defines the class attributes.

    :param message: The message to display.
    :param delay: The delay value.
    :param silence: The value to hide the progress bar.
    """

    return Spinner(
        delay=delay, message=message, silence=silence
    )
# end spinner

class Progress(tqdm):
    """
    A class to show progress bars.

    - delay:
        The delay between output updates of iterations.

    - message:
        The printed message with the progress wheel.

    - silence:
        The value to silence the output.

    >>> from auto_screener.progress import progress
    >>>
    >>> for i in progress(range(100), description="Processing"):
    >>>     time.sleep(0.1)
    >>> # end for
    """

    RUNNING = False

    instances = []

    def __init__(
            self,
            data: Optional[Iterable] = None,
            description: Optional[str] = None,
            start: Optional[str] = None,
            end: Optional[str] = None,
            messages: Iterable[str] = None,
            delay: Optional[Union[int, float]] = None,
            silence: Optional[bool] = None,
            **kwargs: Any
    ) -> None:
        """
        Defines the class attributes.

        :param data: The commands to iterate over.
        :param description: The description of the progress.
        :param messages: The messages to show during the process.
        :param start: The start process message.
        :param end: The end process message.
        :param delay: The delay for each iteration.
        :param kwargs: Any keyword arguments.
        :param silence: The value to silence the process.
        """

        start = start or "Processing"
        end = end or 'Processed'

        self.description = description
        self.messages = list(messages) if (messages is not None) else None
        self.start = start
        self.end = end
        self.silence = silence

        self.index = -1

        self.delay = delay

        kwargs.setdefault(
            'bar_format', (
                "{l_bar}{bar}| {n_fmt}/{total_fmt} "
                "[{remaining}s, {rate_fmt}{postfix}]"
            )
        )
        kwargs.setdefault('desc', description)

        tqdm.__init__(
            self, *((data,) if data is not None else ()),
            **kwargs
        )

        self.running = False

        Progress.instances.append(self)

        self.modifiers: Modifiers

        self.modifiers.excluded.extend(
            [
                name for name in self.__dict__ if name not in
                ["description", "index", "running", "delay"]
            ]
        )
    # end __init__

    def __str__(self) -> str:
        """
        Returns a string representation of the object.

        :return: The string representation of the object.
        """

        return BaseModel.__str__(self)
    # end __str__

    def update(self, n: Optional[int] = 1) -> Any:
        """
        Returns the next value.

        :return: The next value.
        """

        self.running = True

        self.index += 1

        start_message = (
            f"{self.description} - {self.start}"
            if self.description is not None else self.start
        )
        end_message = (
            f"{self.description} - {self.start}"
            if self.description is not None else self.start
        )

        self.set_description(
            f"{start_message}: {self.messages[self.index]}"
            if self.messages else f"{start_message}"
        )

        if self.silence:
            with suppress():
                value = super().update(n=n)
            # end suppress

        else:
            value = super().update(n=n)
        # end if

        self.set_description(
            f"{end_message}: {self.messages[self.index]}"
            if self.messages else f"{end_message}"
        )

        if self.index == self.total - 1:
            self.running = False

            self.set_description(f"{self.description} - Complete")

            Progress.instances.remove(self)

            Progress.RUNNING = bool(Progress.instances)
        # end if

        if self.delay is not None:
            time.sleep(self.delay)
        # end if

        return value
    # end update
# end Progress

def progress(
        data: Iterable,
        silence: Optional[bool] = None,
        description: Optional[str] = None,
        messages: Iterable[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        delay: Optional[Union[int, float]] = None,
        **kwargs: Any
) -> Union[Iterable, Progress]:
    """
    Shows a progress bar for the process.

    :param data: The commands to iterate over.
    :param silence: The value to hide the progress bar.
    :param description: The description of the progress.
    :param messages: The messages to show during the process.
    :param start: The start process message.
    :param end: The end process message.
    :param delay: The delay for each iteration.
    :param kwargs: Any keyword arguments.
    """

    if silence:
        return data

    else:
        return Progress(
            data, description=description, messages=messages,
            start=start, end=end, delay=delay, **kwargs
        )
    # end if
# end progress