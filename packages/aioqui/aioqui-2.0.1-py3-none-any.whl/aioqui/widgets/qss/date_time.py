from . import colors

qss: str = f'''
#DateTime {{
    color: white;
    background-color: black;
    padding: 0px;
    border: none;
    font-size: 18px;
}}

QCalendarWidget QToolButton {{
    height: 30px;
    color: white;
    min-width: 75px;
    icon-size: 20px 20px;
    background-color: {colors.TRANSPARENT};
    border: none;
}}

QCalendarWidget QMenu {{ /* drop-down month selection */
    color: white;
    font-size: 18px;
    background-color: gray;
}}

QCalendarWidget QSpinBox {{ /* up and down buttons frame of changing year */
    width: 50px; 
    font-size:24px; 
    color: white; 
    background-color: {colors.TRANSPARENT};
}}

QCalendarWidget QSpinBox::up-button,
QCalendarWidget QSpinBox::down-button {{
    width: 25px;
    height: 18px;
}}

QCalendarWidget QWidget {{  /* row with day names */
    alternate-background-color: gray;
    font-size: 16px;
}}

QCalendarWidget QWidget#qt_calendar_navigationbar {{ /* most top frame */
    background-color: black;
}}

QCalendarWidget QAbstractItemView:enabled,
QCalendarWidget QAbstractItemView:disabled {{
    font-size: 16px;
}}

QCalendarWidget QAbstractItemView:enabled {{ /* days in this months */
    background-color: {colors.TRANSPARENT};
    selection-background-color: black;
    selection-color: rgb(0, 255, 0);
    color: white; 
}}

QCalendarWidget QAbstractItemView:disabled {{ /* days in other months */
    color: rgb(64, 64, 64); 
}}
'''
