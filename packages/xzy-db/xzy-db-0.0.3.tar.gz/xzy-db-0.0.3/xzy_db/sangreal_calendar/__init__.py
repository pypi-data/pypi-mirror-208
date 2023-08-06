from xzy_db.utils.engines import WIND_DB

from sangreal_calendar import *


def tmp_data():
    table = WIND_DB.ASHARECALENDAR
    df = WIND_DB.query(
        table.trade_dt.label('t')).filter(table.exchen == 'SSE').order_by(
            table.trade_dt).to_df()
    return df['t'].astype(str)


CALENDAR.inject(tmp_data())
DELISTDATE = get_delistdate_all()
DELISTDATE_TF = get_delistdate_tf_all()
