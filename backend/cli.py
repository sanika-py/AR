"""Administrative commands for initial officer account provisioning."""

from __future__ import annotations

import argparse
from getpass import getpass

from sqlalchemy import select

from backend.auth import ROLES, hash_password
from backend.database import SessionLocal
from backend.models import AuditLog, Officer


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage AwazRakshak officer accounts")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-officer")
    create.add_argument("username")
    create.add_argument("--role", choices=sorted(ROLES), default="officer")
    args = parser.parse_args()

    password = getpass("Password (minimum 12 characters): ")
    confirmation = getpass("Confirm password: ")
    if password != confirmation:
        parser.error("Passwords do not match")
    try:
        password_hash = hash_password(password)
    except ValueError as exc:
        parser.error(str(exc))

    with SessionLocal() as db:
        if db.scalar(select(Officer).where(Officer.username == args.username)):
            parser.error("That username already exists")
        officer = Officer(
            username=args.username, password_hash=password_hash, role=args.role
        )
        db.add(officer)
        db.flush()
        db.add(
            AuditLog(
                actor_id=None,
                call_id=None,
                action="officer.provisioned",
                details={"officer_id": officer.id, "username": args.username, "role": args.role},
            )
        )
        db.commit()
    print(f"Created {args.role} account {args.username!r}")


if __name__ == "__main__":
    main()
