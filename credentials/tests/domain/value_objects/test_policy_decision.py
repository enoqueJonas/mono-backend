import pytest

from credentials.domain.value_objects import PolicyDecision


def test_allow_returns_allowed_decision() -> None:
    decision = PolicyDecision.allow()

    assert decision.allowed is True
    assert decision.reason is None


def test_deny_returns_denied_decision_with_reason() -> None:
    decision = PolicyDecision.deny(
        "Credential cannot be issued."
    )

    assert decision.allowed is False
    assert decision.reason == (
        "Credential cannot be issued."
    )


@pytest.mark.parametrize(
    "reason",
    [
        "",
        " ",
        "\n",
    ],
)
def test_deny_rejects_empty_reason(
    reason: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="Policy denial reason cannot be empty.",
    ):
        PolicyDecision.deny(reason)
