from datetime import datetime, date, timedelta
from uuid import uuid4

from pytz import timezone

from shuttlis.serialization import serialize
from shuttlis.time import MilitaryTime, TimeWindow, time_now

IST_TIMEZONE = timezone("Asia/Kolkata")


def test_serialize_with_None():
    res = serialize(None)
    assert res is None


def test_serialize_with_military_time():
    time = MilitaryTime(800, IST_TIMEZONE)
    res = serialize(time)
    assert {"time": 800, "timezone": "Asia/Kolkata"} == res


def test_serialize_with_uuid():
    uuid = uuid4()
    res = serialize(uuid)
    assert str(uuid) == res


def test_serialize_with_datetime():
    ts = datetime(2019, 1, 1, 8, 30, 0)
    res = serialize(ts)
    assert "2019-01-01T08:30:00" == res
    assert datetime.fromisoformat(res) == ts


def test_serialize_with_date():
    dt = date(2019, 1, 1)
    res = serialize(dt)
    assert "2019-01-01" == res
    assert date.fromisoformat(res) == dt


def test_serialize_with_byte_array():
    bytes = b"Hey Dude!!!!"
    res = serialize(bytes)
    assert "Hey Dude!!!!" == res


def test_serialize_with_list():
    uuid = uuid4()
    res = serialize([uuid])
    assert [str(uuid)] == res


def test_serialize_with_frozen_set_converts_it_to_list():
    uuid = uuid4()
    res = serialize(frozenset([uuid]))
    assert [str(uuid)] == res


def test_serialize_with_set_converts_it_to_list():
    uuid = uuid4()
    res = serialize({uuid})
    assert [str(uuid)] == res


def test_serialize_with_time_window():
    from_date = time_now()
    to_date = time_now() + timedelta(hours=5)
    time_window = TimeWindow(from_date=from_date, to_date=to_date)
    res = serialize(time_window)

    assert {"from_date": from_date.isoformat(), "to_date": to_date.isoformat()} == res
