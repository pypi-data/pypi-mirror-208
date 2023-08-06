from PySide6.QtWidgets import QWidget
from datetime import datetime, time, date, timezone
from calendar import monthrange
from dateutil import parser

from ..frame import Frame
from ..layout import Layout
from ..selector import Selector
from ..label import Label


class DateTimePicker(Frame):
    DaySelector: Selector
    MonthSelector: Selector
    YearSelector: Selector
    HourSelector: Selector
    MinuteSelector: Selector
    SecondSelector: Selector

    now = datetime.now()
    default_format = '%d.%m.%Y %H:%M'

    days = [str(day).zfill(2) for day in range(1, monthrange(now.year, now.month)[1] + 1)]
    months = [str(month).zfill(2) for month in range(1, 12 + 1)]
    years = [str(year) for year in range(now.year, now.year + 10)]

    hours = [str(hour).zfill(2) for hour in range(0, 23 + 1)]
    minutes = [str(minute).zfill(2) for minute in range(0, 59 + 1)]
    seconds = [str(second).zfill(2) for second in range(0, 59 + 1)]

    def __init__(self, parent: QWidget, name: str = None, visible: bool = True):
        super().__init__(parent, name if name else self.__class__.__name__, visible)

    async def init(
            self, *,
            show_date: bool = True, show_time: bool = True,
            margins: tuple[int, ...] = (0, 0, 0, 0), spacing: int = 0, alignment: Layout.Alignment = None
    ) -> 'DateTimePicker':
        self.setLayout(await Layout.vertical().init(
            margins=margins, spacing=spacing, alignment=alignment,
            items=[
                await Frame(self, f'{self.objectName()}DateFrame').init(
                    layout=await Layout.horizontal().init(
                        items=[
                            await Label(self, f'{self.objectName()}DateLbl').init(
                                text='Date:'
                            ),
                            DaySelector := await Selector(self, f'{self.objectName()}DaySelector').init(
                                items=self.days
                            ),
                            MonthSelector := await Selector(self, f'{self.objectName()}MonthSelector').init(
                                items=self.months
                            ),
                            YearSelector := await Selector(self, f'{self.objectName()}YearSelector').init(
                                items=self.years
                            )
                        ]
                    )
                ),
                await Frame(self, f'{self.objectName()}TimeFrame').init(
                    layout=await Layout.horizontal().init(
                        items=[
                            await Label(self, f'{self.objectName()}TimeLbl').init(
                                text='Time:'
                            ),
                            HourSelector := await Selector(self, f'{self.objectName()}HourSelector').init(
                                items=self.hours
                            ),
                            MinuteSelector := await Selector(self, f'{self.objectName()}MinuteSelector').init(
                                items=self.minutes
                            ),
                            SecondSelector := await Selector(self, f'{self.objectName()}SecondSelector').init(
                                items=self.seconds
                            )
                        ]
                    )
                )
            ]
        ))
        self.DaySelector = DaySelector
        self.MonthSelector = MonthSelector
        self.YearSelector = YearSelector
        self.HourSelector = HourSelector
        self.MinuteSelector = MinuteSelector
        self.SecondSelector = SecondSelector
        return self

    def get_datetime(self, tz: bool) -> datetime:
        dt = datetime(day=int(self.DaySelector.currentText()),
                      month=int(self.MonthSelector.currentText()),
                      year=int(self.YearSelector.currentText()),
                      hour=int(self.HourSelector.currentText()),
                      minute=int(self.MinuteSelector.currentText()),
                      second=int(self.SecondSelector.currentText()),
        )
        if tz:
            dt.replace(tzinfo=timezone.utc)
        else:
            dt.replace(tzinfo=None)
        return dt

    def get_date(self) -> date:
        return date(
            day=int(self.DaySelector.currentText()),
            month=int(self.MonthSelector.currentText()),
            year=int(self.YearSelector.currentText())
        )

    def get_time(self) -> time:
        return time(
            hour=int(self.HourSelector.currentText()),
            minute=int(self.MinuteSelector.currentText()),
            second=int(self.SecondSelector.currentText())
        )

    def set_date(self, dt: date | datetime | str):
        if isinstance(dt, str):
            dt = self.parse(dt)
        self.DaySelector.setCurrentText(str(dt.day).zfill(2))
        self.MonthSelector.setCurrentText(str(dt.month).zfill(2))
        self.YearSelector.setCurrentText(str(dt.year).zfill(2))

    def set_time(self, dt: time | datetime):
        if isinstance(dt, str):
            dt = self.parse(dt)
        self.HourSelector.setCurrentText(str(dt.hour).zfill(2))
        self.MinuteSelector.setCurrentText(str(dt.minute).zfill(2))
        self.SecondSelector.setCurrentText(str(dt.second).zfill(2))

    def set_datetime(self, dt: datetime):
        self.set_date(dt)
        self.set_time(dt)

    @staticmethod
    def parse(timestr: str) -> datetime:
        return parser.parse(timestr)
