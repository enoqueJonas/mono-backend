from rest_framework import serializers


class CompleteDisbursementSerializer(serializers.Serializer):
    # The manager declares a payment made OUTSIDE Mono, not verified settlement.
    transfer_reference = serializers.RegexField(
        regex=r"^[A-Za-z0-9][A-Za-z0-9._/-]{4,99}$",
        min_length=5,
        max_length=100,
        trim_whitespace=True,
        error_messages={"invalid": "Introduza uma referência válida da transferência externa."},
    )
