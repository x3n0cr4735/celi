from celi_framework.core.section_processor import SectionProcessor


def test_check_for_duplicates_easy():
    assert SectionProcessor.check_for_duplicates([("user", "first message")]) == False


def test_check_for_duplicates_blanks():
    assert (
        SectionProcessor.check_for_duplicates(
            [
                ("assistant", ""),
                ("assistant", ""),
                ("assistant", ""),
                ("assistant", ""),
                ("assistant", ""),
                ("assistant", ""),
            ]
        )
        == True
    )


def test_check_for_duplicates_blanks_interrupted():
    assert (
        SectionProcessor.check_for_duplicates(
            [
                ("assistant", ""),
                ("assistant", ""),
                ("function", "some response"),
                ("assistant", ""),
                ("assistant", ""),
                ("assistant", ""),
                ("assistant", ""),
            ]
        )
        == False
    )


def test_check_for_alternating():
    assert (
        SectionProcessor.check_for_duplicates(
            [
                ("assistant", ""),
                ("function", "some response"),
                ("assistant", ""),
                ("function", "some response"),
                ("assistant", ""),
                ("function", "some response"),
            ]
        )
        == True
    )
