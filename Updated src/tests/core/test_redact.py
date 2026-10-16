from mss.core.redact import redact


def test_redact_email() -> None:
    assert redact("contact owner@example.com") == "contact [email]"


def test_redact_phone() -> None:
    assert redact("call +1 555 123 4567") == "call [phone]"


def test_redact_ip() -> None:
    assert redact("from 10.0.0.42") == "from [ip]"


def test_redact_serial() -> None:
    assert redact("serial ABCD1234EF") == "serial [serial]"