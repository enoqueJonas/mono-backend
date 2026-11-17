"""Virtual-money ledger for controlled tests only. No real money moves."""
from decimal import Decimal

from django.conf import settings
from django.db import transaction

from core.exceptions import DomainException
from wallets.models import SandboxAccount, SandboxEntry, SandboxTransfer


class SandboxUnavailable(DomainException):
    default_message = "A sandbox de pagamentos está desactivada."


class SandboxInsufficientFunds(DomainException):
    default_message = "Saldo fictício insuficiente no grupo."


class SandboxTransferConflict(DomainException):
    default_message = "Referência da sandbox já utilizada para outra operação."


class SandboxLedgerService:
    @staticmethod
    def require_enabled():
        if not getattr(settings, "SANDBOX_PAYMENTS_ENABLED", False):
            raise SandboxUnavailable()

    @staticmethod
    def group_key(group_id, currency):
        return f"GROUP:{group_id}:{currency}"

    @staticmethod
    def member_key(user_id, currency):
        return f"MEMBER:{user_id}:{currency}"

    @staticmethod
    def _account(key, role, currency):
        account, _ = SandboxAccount.objects.get_or_create(
            key=key,
            defaults={"role": role, "currency": currency, "balance": Decimal("0.00")},
        )
        if account.role != role or account.currency != currency:
            raise SandboxTransferConflict("Sandbox account identity has changed.")
        return account

    @classmethod
    def _record(cls, *, key, purpose, source, destination, amount, currency, reference):
        """Must be invoked inside the caller's transaction.

        Locks accounts in stable PK order; the transfer and its two signed entries
        commit or roll back together. A replay returns the same transfer and
        can never debit the account a second time.
        """
        amount = Decimal(str(amount))
        if amount <= 0 or amount != amount.quantize(Decimal("0.01")):
            raise SandboxTransferConflict("Invalid test payment amount.")
        if source.pk == destination.pk:
            raise SandboxTransferConflict("Source and recipient cannot be the same.")

        # The original transfer is an immutable idempotency receipt.
        existing = SandboxTransfer.objects.select_for_update().filter(idempotency_key=key).first()
        if existing:
            if (
                existing.purpose != purpose
                or existing.source_id != source.pk
                or existing.destination_id != destination.pk
                or existing.amount != amount
                or existing.currency != currency
                or existing.reference != reference
            ):
                raise SandboxTransferConflict()
            return existing

        locked = {
            account.pk: account
            for account in SandboxAccount.objects.select_for_update()
            .filter(pk__in=[source.pk, destination.pk]).order_by("pk")
        }
        source = locked[source.pk]
        destination = locked[destination.pk]
        if source.currency != currency or destination.currency != currency:
            raise SandboxTransferConflict("Currency mismatch in sandbox ledger.")
        if source.role != SandboxAccount.Role.ISSUER and source.balance < amount:
            raise SandboxInsufficientFunds()

        transfer = SandboxTransfer.objects.create(
            idempotency_key=key,
            purpose=purpose,
            source=source,
            destination=destination,
            amount=amount,
            currency=currency,
            reference=reference,
        )
        source.balance -= amount
        destination.balance += amount
        source.save(update_fields=["balance"])
        destination.save(update_fields=["balance"])
        SandboxEntry.objects.bulk_create([
            SandboxEntry(transfer=transfer, account=source, signed_amount=-amount),
            SandboxEntry(transfer=transfer, account=destination, signed_amount=amount),
        ])
        return transfer

    @classmethod
    @transaction.atomic
    def record_contribution(cls, contribution):
        """Backs ONLY a confirmed, authenticated SIMULATED provider callback."""
        cls.require_enabled()
        from contributions.models import Contribution
        if (
            contribution.source != Contribution.Source.MOBILE_WALLET
            or contribution.status != Contribution.Status.CONFIRMED
        ):
            raise SandboxTransferConflict("Only simulated provider contributions can fund the sandbox.")
        currency = contribution.currency
        issuer = cls._account(f"ISSUER:{currency}", SandboxAccount.Role.ISSUER, currency)
        group = cls._account(
            cls.group_key(contribution.member.group_id, currency),
            SandboxAccount.Role.GROUP, currency,
        )
        return cls._record(
            key=f"CONTRIBUTION:{contribution.pk}",
            purpose=SandboxTransfer.Purpose.CONTRIBUTION,
            source=issuer,
            destination=group,
            amount=contribution.amount,
            currency=currency,
            reference=contribution.reference,
        )

    @classmethod
    @transaction.atomic
    def pay_disbursement(cls, disbursement):
        """Debit a group and credit a member in fictitious MZN, idempotently."""
        cls.require_enabled()
        currency = disbursement.currency
        group = cls._account(
            cls.group_key(disbursement.group_id, currency),
            SandboxAccount.Role.GROUP, currency,
        )
        member = cls._account(
            cls.member_key(disbursement.beneficiary.user_id, currency),
            SandboxAccount.Role.MEMBER, currency,
        )
        return cls._record(
            key=f"DISBURSEMENT:{disbursement.pk}",
            purpose=SandboxTransfer.Purpose.PAYOUT,
            source=group,
            destination=member,
            amount=disbursement.amount,
            currency=currency,
            reference=str(disbursement.pk),
        )
