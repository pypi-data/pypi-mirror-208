from aleksis.apps.untis.util.mysql.util import (
    untis_split_first,
    untis_split_second,
    untis_split_third,
)

test_lesson_element = """49~0~302~7r;~0;~0~0~175608~~~~~"Freiraum: Naturwissenschaften, Fokus Physik"~"Nawi"~~n~~;11;12;13;14;15;16;17;,49~0~302~7r;~0;~0~0~175608~~~~~"Freiraum: Naturwissenschaften, Fokus Physik"~"Nawi"~~n~~;11;12;13;14;15;16;17;"""

test_lesson_element_partial = """49~0~302~7r;~0;~0~0~175608~~~~~"Freiraum: Naturwissenschaften, Fokus Physik"~"Nawi"~~n~~;11;12;13;14;15;16;17;"""
test_lesson_element_partial_partial = ";11;12;13;14;15;16;17;"

test_lesson_element_second = """46~0~92~45;~45;~12~11~0~~B~~~~~~n~~;18;~"Wp_Eb"~~34~0~67900~0~0~~21700,45~0~92~45;~45;~0~0~19000~~~~~~~~n~~;18;~"Wp_Eb"~~34~0~67900~0~0~~0"""


def test_untis_split_first():
    assert untis_split_first("") == []

    assert untis_split_first("a,b,c") == ["a", "b", "c"]

    assert untis_split_first("1,2,3") == ["1", "2", "3"]
    assert untis_split_first("1,2,3", int) == [1, 2, 3]

    assert len(untis_split_first(test_lesson_element)) == 2
    assert untis_split_first(test_lesson_element) == [
        """49~0~302~7r;~0;~0~0~175608~~~~~"Freiraum: Naturwissenschaften, Fokus Physik"~"Nawi"~~n~~;11;12;13;14;15;16;17;""",
        """49~0~302~7r;~0;~0~0~175608~~~~~"Freiraum: Naturwissenschaften, Fokus Physik"~"Nawi"~~n~~;11;12;13;14;15;16;17;""",
    ]

    assert len(untis_split_first(test_lesson_element_second)) == 2
    assert untis_split_first(test_lesson_element_second) == [
        """46~0~92~45;~45;~12~11~0~~B~~~~~~n~~;18;~"Wp_Eb"~~34~0~67900~0~0~~21700""",
        """45~0~92~45;~45;~0~0~19000~~~~~~~~n~~;18;~"Wp_Eb"~~34~0~67900~0~0~~0""",
    ]


def test_untis_split_second():
    assert untis_split_second("") == []

    assert untis_split_second("a~b~c") == ["a", "b", "c"]

    assert untis_split_second("1~2~3") == ["1", "2", "3"]
    assert untis_split_second("1~2~3", int) == [1, 2, 3]

    assert untis_split_second("1~~3", remove_empty=False) == ["1", None, "3"]
    assert untis_split_second("1~~3", int, remove_empty=False) == [1, None, 3]
    assert untis_split_second("1~~3", int) == [1, 3]

    assert untis_split_second(""""asdf"~"asdf"~"asdf""") == ["asdf", "asdf", "asdf"]

    assert len(untis_split_second(test_lesson_element_partial, remove_empty=False)) == 18
    assert untis_split_second(test_lesson_element_partial, remove_empty=False) == [
        "49",
        "0",
        "302",
        "7r;",
        "0;",
        "0",
        "0",
        "175608",
        None,
        None,
        None,
        None,
        "Freiraum: Naturwissenschaften, Fokus Physik",
        "Nawi",
        None,
        "n",
        None,
        ";11;12;13;14;15;16;17;",
    ]


def test_untis_split_third():
    assert untis_split_third("") == []

    assert untis_split_third("a;b;c") == ["a", "b", "c"]

    assert untis_split_third("1;2;3") == ["1", "2", "3"]
    assert untis_split_third("1;2;3", int) == [1, 2, 3]

    assert untis_split_third("1;;3", remove_empty=False) == ["1", None, "3"]
    assert untis_split_third("1;;3", int, remove_empty=False) == [1, None, 3]
    assert untis_split_third("1;;3", int) == [1, 3]

    assert untis_split_third(""""asdf";"asdf";"asdf""") == ["asdf", "asdf", "asdf"]

    assert len(untis_split_third(test_lesson_element_partial_partial)) == 7
    assert untis_split_third(test_lesson_element_partial_partial) == [
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
    ]
