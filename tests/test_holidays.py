from datetime import date

import pytest

from gdai_core.holidays import (
    BrazilianState,
    Holiday,
    HolidayKind,
    HolidayScope,
    InvalidHolidayRange,
    UnknownBrazilianState,
    brazilian_holidays,
    brazilian_holidays_between,
    easter_sunday,
)


def days_of(holidays: list[Holiday]) -> dict[date, Holiday]:
    return {holiday.day: holiday for holiday in holidays}


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2024, date(2024, 3, 31)),
        (2025, date(2025, 4, 20)),
        (2026, date(2026, 4, 5)),
        (2027, date(2027, 3, 28)),
        (2038, date(2038, 4, 25)),
        (2285, date(2285, 3, 22)),
    ],
)
def test_easter_sunday_matches_the_gregorian_calendar(year, expected):
    assert easter_sunday(year) == expected


def test_national_fixed_holidays_of_2026():
    days = days_of(brazilian_holidays(2026))
    expected = {
        date(2026, 1, 1): "Confraternização Universal",
        date(2026, 4, 21): "Tiradentes",
        date(2026, 5, 1): "Dia do Trabalho",
        date(2026, 9, 7): "Independência do Brasil",
        date(2026, 10, 12): "Nossa Senhora Aparecida",
        date(2026, 11, 2): "Finados",
        date(2026, 11, 15): "Proclamação da República",
        date(2026, 11, 20): "Dia Nacional de Zumbi e da Consciência Negra",
        date(2026, 12, 25): "Natal",
    }
    for day, name in expected.items():
        assert days[day].name == name
        assert days[day].scope is HolidayScope.NATIONAL
        assert days[day].kind is HolidayKind.HOLIDAY


def test_moving_holidays_follow_easter():
    days = days_of(brazilian_holidays(2026))
    assert days[date(2026, 2, 16)].name == "Carnaval"
    assert days[date(2026, 2, 17)].name == "Carnaval"
    assert days[date(2026, 4, 3)].name == "Sexta-feira Santa"
    assert days[date(2026, 6, 4)].name == "Corpus Christi"


def test_carnival_and_corpus_christi_are_optional_and_good_friday_is_not():
    days = days_of(brazilian_holidays(2026))
    assert days[date(2026, 2, 16)].is_optional
    assert days[date(2026, 2, 17)].is_optional
    assert days[date(2026, 6, 4)].is_optional
    assert not days[date(2026, 4, 3)].is_optional


def test_black_consciousness_is_national_only_from_2024():
    assert date(2023, 11, 20) not in days_of(brazilian_holidays(2023))
    assert (
        days_of(brazilian_holidays(2024))[date(2024, 11, 20)].scope
        is HolidayScope.NATIONAL
    )


def test_black_consciousness_was_a_state_holiday_before_it_became_national():
    holiday = days_of(brazilian_holidays(2023, "RJ"))[date(2023, 11, 20)]
    assert holiday.scope is HolidayScope.STATE


def test_state_holidays_are_added_to_the_national_ones():
    days = days_of(brazilian_holidays(2026, "SP"))
    assert days[date(2026, 7, 9)].scope is HolidayScope.STATE
    assert date(2026, 1, 1) in days


def test_without_state_no_state_holiday_shows_up():
    assert date(2026, 7, 9) not in days_of(brazilian_holidays(2026))


def test_state_is_case_insensitive():
    assert brazilian_holidays(2026, "sp") == brazilian_holidays(2026, BrazilianState.SP)


def test_a_state_holiday_on_a_national_holiday_keeps_the_national_one():
    assert (
        days_of(brazilian_holidays(2026, "MG"))[date(2026, 4, 21)].scope
        is HolidayScope.NATIONAL
    )


def test_a_state_holiday_with_a_start_year_is_absent_before_it():
    assert date(2007, 3, 6) not in days_of(brazilian_holidays(2007, "PE"))
    assert date(2008, 3, 6) in days_of(brazilian_holidays(2008, "PE"))


def test_every_state_is_accepted():
    for state in BrazilianState:
        assert brazilian_holidays(2026, state)


def test_unknown_state_is_rejected():
    with pytest.raises(UnknownBrazilianState):
        brazilian_holidays(2026, "XX")


def test_holidays_come_sorted_by_day_without_repeats():
    holidays = brazilian_holidays(2026, "RJ")
    days = [holiday.day for holiday in holidays]
    assert days == sorted(set(days))


def test_range_crosses_years():
    holidays = brazilian_holidays_between(date(2026, 12, 20), date(2027, 1, 5))
    assert [holiday.day for holiday in holidays] == [
        date(2026, 12, 25),
        date(2027, 1, 1),
    ]


def test_range_includes_both_ends():
    holidays = brazilian_holidays_between(date(2026, 11, 2), date(2026, 11, 2))
    assert [holiday.name for holiday in holidays] == ["Finados"]


def test_range_that_ends_before_it_starts_is_rejected():
    with pytest.raises(InvalidHolidayRange):
        brazilian_holidays_between(date(2026, 2, 1), date(2026, 1, 1))
