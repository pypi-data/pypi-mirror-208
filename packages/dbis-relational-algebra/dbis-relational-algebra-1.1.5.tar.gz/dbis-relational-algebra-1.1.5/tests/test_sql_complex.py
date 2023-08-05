import pytest

from relational_algebra import *


def test_track_refs(session):
    r = session.execute("SELECT circuitRef FROM circuits;")
    solution = set(r.fetchall())
    assert len(solution) > 0

    cR = Projection("circuits", "circuitRef").evaluate(sql_con=session)

    assert len(cR.rows) == len(solution)
    assert set(cR.rows) == solution


def test_tracks_germany(session):
    r = session.execute(
        "SELECT Name, Location FROM circuits WHERE Country = 'Germany';"
    )
    solution = set(r.fetchall())
    assert len(solution) > 0

    ra = Projection(
        Selection("circuits", Equals("Country", "Germany")), ["Name", "Location"]
    ).evaluate(sql_con=session)

    assert len(ra.rows) == len(solution)
    assert set(ra.rows) == solution


def test_tracks_northeast_southwest(session):
    r = session.execute(
        "SELECT * FROM circuits WHERE (Lat >= 0 AND Lng >= 0) OR (Lat < 0 AND Lng < 0);"
    )
    solution = set(r.fetchall())
    assert len(solution) > 0

    ra = Selection(
        "circuits",
        Or(
            And(GreaterEquals("Lat", 0), GreaterEquals("Lng", 0)),
            And(LessThan("Lat", 0), LessThan("Lng", 0)),
        ),
    ).evaluate(sql_con=session)

    assert len(ra.rows) == len(solution)
    assert set(ra.rows) == solution


@pytest.mark.skip("Too memory intensive - uses cartesian product")
def test_fastest_race_laps(session):
    r = session.execute(
        """SELECT circuits.name, drivers.forename, drivers.surname, lapTimes.milliseconds
        FROM circuits
        JOIN races ON circuits.circuitId = races.circuitId
        JOIN lapTimes ON races.raceId = lapTimes.raceId
        JOIN drivers ON lapTimes.driverId = drivers.driverId
        WHERE NOT EXISTS (
            SELECT *
            FROM lapTimes lT
            WHERE lT.raceId = lapTimes.raceId
            AND (lapTimes.driverID != lT.driverID OR lapTimes.lap != lT.lap)
            AND lapTimes.milliseconds < lT.milliseconds
        );"""
    )
    solution = set(r.fetchall())
    assert len(solution) > 0

    r2 = session.execute(
        """SELECT circuits.name, drivers.forename, drivers.surname, lapTimes.milliseconds
FROM circuits
JOIN races ON circuits.circuitId = races.circuitId
JOIN lapTimes ON races.raceId = lapTimes.raceId
JOIN drivers ON lapTimes.driverId = drivers.driverId
LEFT JOIN lapTimes lT ON lT.raceId = lapTimes.raceId
  AND (lapTimes.driverID != lT.driverID OR lapTimes.lap != lT.lap)
  AND lapTimes.milliseconds < lT.milliseconds
WHERE lT.raceId IS NULL;
"""
    )
    solution2 = set(r2.fetchall())
    assert len(solution2) > 0
    assert len(solution) == len(solution2)
    assert solution == solution2

    # see https://en.wikipedia.org/wiki/Relational_algebra#Left_outer_join_(%E2%9F%95)

    blank_lapTimes = Relation("lapTimes")
    blank_lapTimes.add_attributes(
        ["diverId", "lap", "position", "time", "milliseconds"]
    )
    blank_lapTimes.add_row(tuple([None] * 5))

    join_attributes = [
        "circuits.name",
        "drivers.forename",
        "drivers.surname",
        "lapTimes.milliseconds",
        "lapTimes.raceId",
        "lapTimes.driverId",
        "lapTimes.lap",
    ]

    tj1 = ThetaJoin(
        "circuits",
        "races",
        Equals("circuits.circuitId", "races.circuitId"),
    ).evaluate(sql_con=session)

    assert len(tj1.rows) > 0

    tj2 = ThetaJoin(
        "lapTimes",
        "drivers",
        Equals("lapTimes.driverId", "drivers.driverId"),
    ).evaluate(sql_con=session)

    assert len(tj2.rows) > 0

    left = Projection(
        ThetaJoin(
            tj1,
            tj2,
            Equals("races.raceId", "lapTimes.raceId"),
        ),
        join_attributes,
    ).evaluate()

    assert len(left.rows) > 0

    right = Rename("lapTimes", "lT").evaluate(sql_con=session)

    assert len(right.rows) > 0

    theta = ThetaJoin(
        left,
        right,
        And(
            And(
                Equals("lT.raceId", "lapTimes.raceId"),
                Or(
                    Not(Equals("lapTimes.driverId", "lT.driverId")),
                    Not(Equals("lapTimes.lap", "lT.lap")),
                ),
            ),
            LessThan("lapTimes.milliseconds", "lT.milliseconds"),
        ),
    ).evaluate()

    assert len(theta.rows) > 0

    difference = (
        left
        - Projection(
            theta,
            join_attributes,
        )
    ).evaluate()

    assert len(difference.rows) > 0

    cross = CrossProduct(difference, blank_lapTimes).evaluate()

    assert len(cross.rows) > 0

    union = Union(cross, theta).evaluate()

    assert len(union.rows) > 0

    selection = Selection(union, Equals("lT.raceId", None)).evaluate()

    assert len(selection.rows) > 0

    result = Projection(
        selection,
        [
            "circuits.name",
            "drivers.forename",
            "drivers.surname",
            "lapTimes.milliseconds",
        ],
    )

    ra = result.evaluate(sql_con=session)

    assert len(ra.rows) == len(solution)
    assert set(ra.rows) == solution
