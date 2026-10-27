from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum


class BrazilianState(StrEnum):
    AC = "AC"
    AL = "AL"
    AM = "AM"
    AP = "AP"
    BA = "BA"
    CE = "CE"
    DF = "DF"
    ES = "ES"
    GO = "GO"
    MA = "MA"
    MG = "MG"
    MS = "MS"
    MT = "MT"
    PA = "PA"
    PB = "PB"
    PE = "PE"
    PI = "PI"
    PR = "PR"
    RJ = "RJ"
    RN = "RN"
    RO = "RO"
    RR = "RR"
    RS = "RS"
    SC = "SC"
    SE = "SE"
    SP = "SP"
    TO = "TO"


class HolidayScope(StrEnum):
    NATIONAL = "national"
    STATE = "state"


class HolidayKind(StrEnum):
    HOLIDAY = "holiday"
    OPTIONAL = "optional"


@dataclass(frozen=True, order=True)
class Holiday:
    day: date
    name: str
    scope: HolidayScope
    kind: HolidayKind = HolidayKind.HOLIDAY

    @property
    def is_optional(self) -> bool:
        return self.kind is HolidayKind.OPTIONAL


@dataclass(frozen=True)
class _FixedHoliday:
    month: int
    day: int
    name: str
    since: int | None = None
    until: int | None = None

    def falls_in(self, year: int) -> bool:
        started = self.since is None or year >= self.since
        not_ended = self.until is None or year <= self.until
        return started and not_ended


@dataclass(frozen=True)
class _EasterHoliday:
    days_from_easter: int
    name: str
    kind: HolidayKind


class UnknownBrazilianState(ValueError):
    def __init__(self, state: str) -> None:
        super().__init__(f"unknown Brazilian state: {state}")
        self.state = state


class InvalidHolidayRange(ValueError):
    def __init__(self, start: date, end: date) -> None:
        super().__init__(f"holiday range ends before it starts: {start} > {end}")


BLACK_CONSCIOUSNESS_NATIONAL_SINCE = 2024
BLACK_CONSCIOUSNESS_STATE_UNTIL = BLACK_CONSCIOUSNESS_NATIONAL_SINCE - 1
BLACK_CONSCIOUSNESS = "Dia Nacional de Zumbi e da Consciência Negra"

NATIONAL_FIXED_HOLIDAYS = (
    _FixedHoliday(1, 1, "Confraternização Universal"),
    _FixedHoliday(4, 21, "Tiradentes"),
    _FixedHoliday(5, 1, "Dia do Trabalho"),
    _FixedHoliday(9, 7, "Independência do Brasil"),
    _FixedHoliday(10, 12, "Nossa Senhora Aparecida"),
    _FixedHoliday(11, 2, "Finados"),
    _FixedHoliday(11, 15, "Proclamação da República"),
    _FixedHoliday(
        11, 20, BLACK_CONSCIOUSNESS, since=BLACK_CONSCIOUSNESS_NATIONAL_SINCE
    ),
    _FixedHoliday(12, 25, "Natal"),
)

CARNIVAL_MONDAY_OFFSET = -48
CARNIVAL_TUESDAY_OFFSET = -47
GOOD_FRIDAY_OFFSET = -2
CORPUS_CHRISTI_OFFSET = 60

NATIONAL_EASTER_HOLIDAYS = (
    _EasterHoliday(CARNIVAL_MONDAY_OFFSET, "Carnaval", HolidayKind.OPTIONAL),
    _EasterHoliday(CARNIVAL_TUESDAY_OFFSET, "Carnaval", HolidayKind.OPTIONAL),
    _EasterHoliday(GOOD_FRIDAY_OFFSET, "Sexta-feira Santa", HolidayKind.HOLIDAY),
    _EasterHoliday(CORPUS_CHRISTI_OFFSET, "Corpus Christi", HolidayKind.OPTIONAL),
)


def _state_black_consciousness() -> _FixedHoliday:
    return _FixedHoliday(
        11,
        20,
        BLACK_CONSCIOUSNESS,
        until=BLACK_CONSCIOUSNESS_STATE_UNTIL,
    )


MARANHAO_INDEPENDENCE = "Adesão do Maranhão à Independência do Brasil"
MATO_GROSSO_DO_SUL_CREATION = "Criação do Estado de Mato Grosso do Sul"
PARA_INDEPENDENCE = "Adesão do Pará à Independência do Brasil"

STATE_FIXED_HOLIDAYS: dict[BrazilianState, tuple[_FixedHoliday, ...]] = {
    BrazilianState.AC: (
        _FixedHoliday(1, 23, "Dia do Evangélico"),
        _FixedHoliday(3, 8, "Dia Internacional da Mulher"),
        _FixedHoliday(6, 15, "Aniversário do Acre"),
        _FixedHoliday(9, 5, "Dia da Amazônia"),
        _FixedHoliday(11, 17, "Assinatura do Tratado de Petrópolis"),
    ),
    BrazilianState.AL: (
        _FixedHoliday(6, 24, "São João"),
        _FixedHoliday(6, 29, "São Pedro"),
        _FixedHoliday(9, 16, "Emancipação Política de Alagoas"),
        _state_black_consciousness(),
        _FixedHoliday(11, 30, "Dia do Evangélico", since=2013),
    ),
    BrazilianState.AM: (
        _FixedHoliday(9, 5, "Elevação do Amazonas à Categoria de Província"),
        _state_black_consciousness(),
        _FixedHoliday(12, 8, "Nossa Senhora da Conceição"),
    ),
    BrazilianState.AP: (
        _FixedHoliday(3, 19, "São José"),
        _FixedHoliday(7, 25, "São Tiago", since=2012),
        _FixedHoliday(10, 5, "Criação do Estado do Amapá"),
        _state_black_consciousness(),
    ),
    BrazilianState.BA: (_FixedHoliday(7, 2, "Independência da Bahia"),),
    BrazilianState.CE: (
        _FixedHoliday(3, 19, "São José"),
        _FixedHoliday(3, 25, "Data Magna do Ceará"),
    ),
    BrazilianState.DF: (_FixedHoliday(11, 30, "Dia do Evangélico"),),
    BrazilianState.MA: (_FixedHoliday(7, 28, MARANHAO_INDEPENDENCE),),
    BrazilianState.MS: (_FixedHoliday(10, 11, MATO_GROSSO_DO_SUL_CREATION),),
    BrazilianState.MT: (_state_black_consciousness(),),
    BrazilianState.PA: (_FixedHoliday(8, 15, PARA_INDEPENDENCE),),
    BrazilianState.PB: (
        _FixedHoliday(7, 26, "Homenagem à memória do ex-presidente João Pessoa"),
        _FixedHoliday(8, 5, "Fundação do Estado da Paraíba"),
    ),
    BrazilianState.PE: (
        _FixedHoliday(3, 6, "Data Magna de Pernambuco", since=2008),
        _FixedHoliday(6, 24, "São João"),
    ),
    BrazilianState.PI: (
        _FixedHoliday(3, 13, "Dia da Batalha do Jenipapo"),
        _FixedHoliday(10, 19, "Dia do Piauí"),
    ),
    BrazilianState.PR: (_FixedHoliday(12, 19, "Emancipação Política do Paraná"),),
    BrazilianState.RJ: (
        _FixedHoliday(4, 23, "Dia de São Jorge"),
        _state_black_consciousness(),
    ),
    BrazilianState.RN: (
        _FixedHoliday(6, 29, "São Pedro"),
        _FixedHoliday(10, 3, "Mártires de Cunhaú e Uruaçu", since=2007),
    ),
    BrazilianState.RO: (
        _FixedHoliday(1, 4, "Criação do Estado de Rondônia"),
        _FixedHoliday(6, 18, "Dia do Evangélico", since=2002),
    ),
    BrazilianState.RR: (_FixedHoliday(10, 5, "Criação do Estado de Roraima"),),
    BrazilianState.RS: (_FixedHoliday(9, 20, "Revolução Farroupilha"),),
    BrazilianState.SE: (_FixedHoliday(7, 8, "Autonomia Política de Sergipe"),),
    BrazilianState.SP: (_FixedHoliday(7, 9, "Revolução Constitucionalista de 1932"),),
    BrazilianState.TO: (
        _FixedHoliday(3, 18, "Autonomia do Estado do Tocantins", since=1998),
        _FixedHoliday(9, 8, "Nossa Senhora da Natividade"),
        _FixedHoliday(10, 5, "Criação do Estado do Tocantins"),
    ),
}


def easter_sunday(year: int) -> date:
    golden = year % 19
    century, year_of_century = divmod(year, 100)
    leap_centuries, century_rest = divmod(century, 4)
    moon_correction = (century + 8) // 25
    solar_correction = (century - moon_correction + 1) // 3
    epact = (19 * golden + century - leap_centuries - solar_correction + 15) % 30
    leap_years, year_rest = divmod(year_of_century, 4)
    weekday_offset = (32 + 2 * century_rest + 2 * leap_years - epact - year_rest) % 7
    month_shift = (golden + 11 * epact + 22 * weekday_offset) // 451
    month, day = divmod(epact + weekday_offset - 7 * month_shift + 114, 31)
    return date(year, month, day + 1)


def brazilian_state(state: str) -> BrazilianState:
    try:
        return BrazilianState(state.upper())
    except ValueError:
        raise UnknownBrazilianState(state) from None


def _fixed(
    year: int, holidays: tuple[_FixedHoliday, ...], scope: HolidayScope
) -> list[Holiday]:
    return [
        Holiday(date(year, holiday.month, holiday.day), holiday.name, scope)
        for holiday in holidays
        if holiday.falls_in(year)
    ]


def _moving(year: int) -> list[Holiday]:
    easter = easter_sunday(year)
    return [
        Holiday(
            easter + timedelta(days=holiday.days_from_easter),
            holiday.name,
            HolidayScope.NATIONAL,
            holiday.kind,
        )
        for holiday in NATIONAL_EASTER_HOLIDAYS
    ]


def _without_repeated_days(holidays: list[Holiday]) -> list[Holiday]:
    by_day: dict[date, Holiday] = {}
    for holiday in holidays:
        kept = by_day.get(holiday.day)
        if kept is None or (kept.is_optional and not holiday.is_optional):
            by_day[holiday.day] = holiday
    return sorted(by_day.values())


def brazilian_holidays(year: int, state: str | None = None) -> list[Holiday]:
    national = _fixed(year, NATIONAL_FIXED_HOLIDAYS, HolidayScope.NATIONAL) + _moving(
        year
    )
    regional = (
        []
        if state is None
        else _fixed(
            year,
            STATE_FIXED_HOLIDAYS.get(brazilian_state(state), ()),
            HolidayScope.STATE,
        )
    )
    return _without_repeated_days(sorted(national) + regional)


def brazilian_holidays_between(
    start: date, end: date, state: str | None = None
) -> list[Holiday]:
    if end < start:
        raise InvalidHolidayRange(start, end)
    return [
        holiday
        for year in range(start.year, end.year + 1)
        for holiday in brazilian_holidays(year, state)
        if start <= holiday.day <= end
    ]
