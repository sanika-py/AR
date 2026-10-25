"""JWT-protected REST endpoints for calls, notes, summaries, and officer actions."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.auth import (
    create_access_token,
    require_roles,
    verify_password,
)
from backend.database import get_db
from backend.models import AuditLog, Call, Flag, Note, Officer, Summary
from backend.schemas import (
    ActionResponse,
    CallCreatedResponse,
    EscalateRequest,
    FlagRequest,
    LoginRequest,
    NoteRequest,
    SummaryRequest,
    TokenResponse,
    TransferRequest,
)

router = APIRouter()
Db = Annotated[Session, Depends(get_db)]
AuthenticatedOfficer = Annotated[
    Officer, Depends(require_roles("officer", "supervisor", "admin"))
]


def _record_audit(
    db: Session,
    *,
    actor_id: str | None,
    call_id: str | None,
    action: str,
    details: dict,
) -> AuditLog:
    entry = AuditLog(
        actor_id=actor_id,
        call_id=call_id,
        action=action,
        details=details,
    )
    db.add(entry)
    return entry


def _commit(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The action could not be committed",
        ) from exc


def _call_or_404(db: Session, call_id: str) -> Call:
    call = db.get(Call, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


@router.post("/auth/token", response_model=TokenResponse)
def issue_token(payload: LoginRequest, db: Db) -> TokenResponse:
    officer = db.scalar(select(Officer).where(Officer.username == payload.username))
    if (
        officer is None
        or not officer.active
        or not verify_password(payload.password, officer.password_hash)
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, expires_in = create_access_token(officer)
    _record_audit(
        db,
        actor_id=officer.id,
        call_id=None,
        action="auth.login",
        details={"role": officer.role},
    )
    _commit(db)
    return TokenResponse(access_token=token, expires_in=expires_in, role=officer.role)


@router.post("/calls", response_model=CallCreatedResponse, status_code=201)
def create_call(db: Db, officer: AuthenticatedOfficer) -> CallCreatedResponse:
    call = Call(created_by=officer.id)
    db.add(call)
    db.flush()
    audit = _record_audit(
        db,
        actor_id=officer.id,
        call_id=call.id,
        action="call.created",
        details={},
    )
    _commit(db)
    return CallCreatedResponse(call_id=call.id, status=call.status, audit_id=audit.id)


@router.post("/calls/{call_id}/escalate", response_model=ActionResponse)
def escalate_call(
    call_id: str,
    payload: EscalateRequest,
    db: Db,
    officer: AuthenticatedOfficer,
) -> ActionResponse:
    call = _call_or_404(db, call_id)
    if call.status == "closed":
        raise HTTPException(status_code=409, detail="Closed calls cannot be escalated")
    call.escalated = True
    call.escalation_count += 1
    call.status = "escalated"
    audit = _record_audit(
        db,
        actor_id=officer.id,
        call_id=call.id,
        action="call.escalated",
        details={"reason": payload.reason, "escalation_count": call.escalation_count},
    )
    _commit(db)
    return ActionResponse(
        call_id=call.id,
        action="escalate",
        audit_id=audit.id,
        status=call.status,
        assigned_team=call.assigned_team,
    )


@router.post("/calls/{call_id}/flag", response_model=ActionResponse, status_code=201)
@router.post("/calls/{call_id}/flags", response_model=ActionResponse, status_code=201)
def flag_call(
    call_id: str,
    payload: FlagRequest,
    db: Db,
    officer: AuthenticatedOfficer,
) -> ActionResponse:
    call = _call_or_404(db, call_id)
    flag = Flag(call_id=call.id, officer_id=officer.id, reason=payload.reason)
    db.add(flag)
    db.flush()
    audit = _record_audit(
        db,
        actor_id=officer.id,
        call_id=call.id,
        action="call.flagged_for_review",
        details={"flag_id": flag.id, "reason": payload.reason},
    )
    _commit(db)
    return ActionResponse(
        call_id=call.id,
        action="flag_for_review",
        audit_id=audit.id,
        status=flag.status,
        assigned_team=call.assigned_team,
    )


@router.post("/calls/{call_id}/transfer", response_model=ActionResponse)
def transfer_call(
    call_id: str,
    payload: TransferRequest,
    db: Db,
    officer: Annotated[Officer, Depends(require_roles("supervisor", "admin"))],
) -> ActionResponse:
    call = _call_or_404(db, call_id)
    if call.status == "closed":
        raise HTTPException(status_code=409, detail="Closed calls cannot be transferred")
    call.assigned_team = payload.target_team
    call.status = "transferred"
    details = {"target_team": payload.target_team}
    if payload.reason:
        details["reason"] = payload.reason
    audit = _record_audit(
        db,
        actor_id=officer.id,
        call_id=call.id,
        action="call.transferred",
        details=details,
    )
    _commit(db)
    return ActionResponse(
        call_id=call.id,
        action="transfer",
        audit_id=audit.id,
        status=call.status,
        assigned_team=call.assigned_team,
    )


@router.post("/calls/{call_id}/notes", response_model=ActionResponse, status_code=201)
def save_note(
    call_id: str,
    payload: NoteRequest,
    db: Db,
    officer: AuthenticatedOfficer,
) -> ActionResponse:
    call = _call_or_404(db, call_id)
    note = Note(call_id=call.id, officer_id=officer.id, content=payload.content)
    db.add(note)
    db.flush()
    audit = _record_audit(
        db,
        actor_id=officer.id,
        call_id=call.id,
        action="call.note_saved",
        details={"note_id": note.id},
    )
    _commit(db)
    return ActionResponse(
        call_id=call.id,
        action="save_note",
        audit_id=audit.id,
        status=call.status,
        assigned_team=call.assigned_team,
    )


@router.post("/calls/{call_id}/summaries", response_model=ActionResponse, status_code=201)
def save_summary(
    call_id: str,
    payload: SummaryRequest,
    db: Db,
    officer: AuthenticatedOfficer,
) -> ActionResponse:
    call = _call_or_404(db, call_id)
    summary = Summary(call_id=call.id, **payload.model_dump())
    db.add(summary)
    db.flush()
    audit = _record_audit(
        db,
        actor_id=officer.id,
        call_id=call.id,
        action="call.summary_saved",
        details={"summary_id": summary.id},
    )
    _commit(db)
    return ActionResponse(
        call_id=call.id,
        action="save_summary",
        audit_id=audit.id,
        status=call.status,
        assigned_team=call.assigned_team,
    )
