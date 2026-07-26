# Mono Backend Architecture

Version: 1.0
Status: Frozen
Last Updated: 2026-07-26



# 1. Purpose

This document defines the architecture of the Mono backend.

It serves as the single source of truth for the project structure, responsibilities, design decisions and development guidelines.

Any architectural changes must be justified by implementation needs rather than speculative improvements.



# 2. Architecture Overview

The backend follows a layered architecture inspired by Domain-Driven Design (DDD) and Clean Architecture.

```
Presentation Layer
        │
        ▼
Application Layer
        │
        ▼
Domain Layer
        │
        ▼
Infrastructure Layer
```

Each layer has a single responsibility.



# 3. Layers

## Presentation

Responsible for:

- Django REST Framework Views
- Serializers
- Authentication
- HTTP Responses

No business rules are allowed here.



## Application

Responsible for orchestrating use cases.

Application Services:

- RegisterUserService
- CreateGroupService
- AddGroupMemberService
- RegisterContributionService
- IssueCredentialService
- VerifyCredentialService
- RevokeCredentialService

Application services coordinate domain services but do not implement business rules.



## Domain

Contains the business logic.

### Entities

- User
- Group
- Contribution
- Credential
- BlockchainAnchor

### Aggregate Roots

- User
- Group
- Credential

### Domain Services

- CredentialService
- CredentialAnchorService
- VerificationService

### Policies

- CredentialIssuancePolicy
- CredentialRevocationPolicy

### Factories

- CredentialDocumentFactory

### Value Objects

- CredentialDocument
- CredentialHash

### Exceptions

Domain-specific exceptions live here.



## Infrastructure

Responsible for external systems.

Includes:

- Web3.py
- Ethereum
- TransactionService
- CredentialRegistryClient
- BlockchainReceiptMapper
- HashingService

Infrastructure never contains business rules.



# 4. Project Structure

apps/

accounts/

groups/

contributions/

credentials/

blockchain/

docs/



credentials/

application/

domain/

services/

factories/

policies/

value_objects/

exceptions/

models/

enums/



# 5. Business Flow

Issue Credential

↓

Validate Eligibility

↓

Generate Credential Document

↓

Calculate SHA-256

↓

Anchor on Blockchain

↓

Create Credential

↓

Persist Blockchain Anchor

↓

Return Credential



# 6. Design Principles

## Single Responsibility

Each class has one responsibility.



## Separation of Concerns

Business rules belong to the domain.

Infrastructure contains implementation details only.



## Dependency Direction

Presentation

↓

Application

↓

Domain

↓

Infrastructure

Dependencies never point upwards.



## Explicit Business Language

Prefer:

CredentialHash

instead of bytes

CredentialDocument

instead of dict

CredentialIssuancePolicy

instead of inline if statements



## Use Cases First

Every feature starts with a use case.

The implementation follows the application service.



# 7. Development Rules

Before creating a new class, answer:

1. Is this Domain or Infrastructure?

2. Does this represent a business concept or a technical detail?

If neither answer is clear, rethink the design.



# 8. Testing Strategy

Unit Tests

- Value Objects
- Policies
- Domain Services

Integration Tests

- Blockchain
- Database

End-to-End Tests

Complete business workflows.



# 9. Blockchain Principles

Only SHA-256 hashes are stored on-chain.

Credentials remain off-chain.

Blockchain stores:

- Credential Hash
- Transaction Metadata
- Revocation State

No personal information is stored on Ethereum.



# 10. Future Features

The architecture is prepared for:

- Credential Revocation
- Credential Verification
- DID Resolution
- Selective Disclosure
- Multiple Blockchain Networks

These features should reuse the existing architecture without requiring structural changes.