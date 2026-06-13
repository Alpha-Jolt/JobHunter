"""Unit tests for policy objects — JobPolicy, ApplicationPolicy, VariantPolicy."""

from __future__ import annotations

import uuid

from orchestration.auth.models.user import RoleEnum, UserRecord
from orchestration.auth.policies.application_policy import ApplicationPolicy
from orchestration.auth.policies.job_policy import JobPolicy
from orchestration.auth.policies.variant_policy import VariantPolicy


def _user(role: RoleEnum, user_id=None) -> UserRecord:
    return UserRecord(
        user_id=user_id or uuid.uuid4(),
        email="u@example.com",
        password_hash="hash",
        role=role,
    )


def _job(recruiter_id=None, status="raw"):
    j = type("Job", (), {})()
    j.recruiter_id = recruiter_id
    j.status = status
    return j


def _application(user_id=None):
    a = type("App", (), {})()
    a.user_id = user_id or uuid.uuid4()
    return a


def _variant(user_id=None, approval_status="pending"):
    v = type("Variant", (), {})()
    v.user_id = user_id or uuid.uuid4()
    v.approval_status = approval_status
    return v


# ── JobPolicy.can_create ──────────────────────────────────────────────────────

def test_job_can_create_recruiter():
    assert JobPolicy.can_create(_user(RoleEnum.RECRUITER)) is True


def test_job_can_create_admin():
    assert JobPolicy.can_create(_user(RoleEnum.ADMIN)) is True


def test_job_cannot_create_hunter():
    assert JobPolicy.can_create(_user(RoleEnum.HUNTER)) is False


def test_job_cannot_create_mentor():
    assert JobPolicy.can_create(_user(RoleEnum.MENTOR)) is False


# ── JobPolicy.can_update ──────────────────────────────────────────────────────

def test_job_can_update_own_open_job():
    uid = uuid.uuid4()
    user = _user(RoleEnum.RECRUITER, user_id=uid)
    job = _job(recruiter_id=uid, status="raw")
    assert JobPolicy.can_update(user, job) is True


def test_job_cannot_update_closed_job():
    uid = uuid.uuid4()
    user = _user(RoleEnum.RECRUITER, user_id=uid)
    job = _job(recruiter_id=uid, status="closed")
    assert JobPolicy.can_update(user, job) is False


def test_job_cannot_update_other_recruiters_job():
    user = _user(RoleEnum.RECRUITER)
    job = _job(recruiter_id=uuid.uuid4(), status="raw")
    assert JobPolicy.can_update(user, job) is False


def test_job_cannot_update_scraper_owned_job():
    user = _user(RoleEnum.RECRUITER)
    job = _job(recruiter_id=None, status="raw")
    assert JobPolicy.can_update(user, job) is False


def test_job_admin_can_update_any_job():
    user = _user(RoleEnum.ADMIN)
    job = _job(recruiter_id=uuid.uuid4(), status="closed")
    assert JobPolicy.can_update(user, job) is True


def test_job_hunter_cannot_update():
    uid = uuid.uuid4()
    user = _user(RoleEnum.HUNTER, user_id=uid)
    job = _job(recruiter_id=uid, status="raw")
    assert JobPolicy.can_update(user, job) is False


def test_job_can_update_str_uuid_recruiter_id():
    uid = uuid.uuid4()
    user = _user(RoleEnum.RECRUITER, user_id=uid)
    job = _job(recruiter_id=str(uid), status="reviewed")
    assert JobPolicy.can_update(user, job) is True


# ── JobPolicy.can_close ───────────────────────────────────────────────────────

def test_job_can_close_own_job_no_applications():
    uid = uuid.uuid4()
    user = _user(RoleEnum.RECRUITER, user_id=uid)
    job = _job(recruiter_id=uid, status="raw")
    assert JobPolicy.can_close(user, job, active_application_count=0) is True


def test_job_cannot_close_with_active_applications():
    uid = uuid.uuid4()
    user = _user(RoleEnum.RECRUITER, user_id=uid)
    job = _job(recruiter_id=uid, status="raw")
    assert JobPolicy.can_close(user, job, active_application_count=3) is False


def test_job_admin_can_close_with_applications():
    user = _user(RoleEnum.ADMIN)
    job = _job(recruiter_id=uuid.uuid4(), status="raw")
    assert JobPolicy.can_close(user, job, active_application_count=5) is True


def test_job_cannot_close_other_recruiters_job():
    user = _user(RoleEnum.RECRUITER)
    job = _job(recruiter_id=uuid.uuid4(), status="raw")
    assert JobPolicy.can_close(user, job, active_application_count=0) is False


# ── ApplicationPolicy.can_view ────────────────────────────────────────────────

def test_application_owner_can_view():
    uid = uuid.uuid4()
    user = _user(RoleEnum.HUNTER, user_id=uid)
    app = _application(user_id=uid)
    assert ApplicationPolicy.can_view(user, app) is True


def test_application_other_hunter_cannot_view():
    user = _user(RoleEnum.HUNTER)
    app = _application(user_id=uuid.uuid4())
    assert ApplicationPolicy.can_view(user, app) is False


def test_application_recruiter_of_job_can_view():
    rid = uuid.uuid4()
    user = _user(RoleEnum.RECRUITER, user_id=rid)
    app = _application(user_id=uuid.uuid4())
    job = _job(recruiter_id=rid)
    assert ApplicationPolicy.can_view(user, app, job=job) is True


def test_application_other_recruiter_cannot_view():
    user = _user(RoleEnum.RECRUITER)
    app = _application(user_id=uuid.uuid4())
    job = _job(recruiter_id=uuid.uuid4())
    assert ApplicationPolicy.can_view(user, app, job=job) is False


def test_application_admin_can_view_any():
    user = _user(RoleEnum.ADMIN)
    app = _application(user_id=uuid.uuid4())
    assert ApplicationPolicy.can_view(user, app) is True


def test_application_can_view_with_str_user_id():
    uid = uuid.uuid4()
    user = _user(RoleEnum.HUNTER, user_id=uid)
    app = _application(user_id=str(uid))
    assert ApplicationPolicy.can_view(user, app) is True


# ── ApplicationPolicy.can_update_status ───────────────────────────────────────

def test_application_recruiter_job_owner_can_update_status():
    rid = uuid.uuid4()
    user = _user(RoleEnum.RECRUITER, user_id=rid)
    app = _application()
    job = _job(recruiter_id=rid)
    assert ApplicationPolicy.can_update_status(user, app, job) is True


def test_application_hunter_cannot_update_status():
    uid = uuid.uuid4()
    user = _user(RoleEnum.HUNTER, user_id=uid)
    app = _application(user_id=uid)
    job = _job(recruiter_id=uuid.uuid4())
    assert ApplicationPolicy.can_update_status(user, app, job) is False


def test_application_admin_can_update_status():
    user = _user(RoleEnum.ADMIN)
    app = _application()
    job = _job(recruiter_id=uuid.uuid4())
    assert ApplicationPolicy.can_update_status(user, app, job) is True


def test_application_other_recruiter_cannot_update_status():
    user = _user(RoleEnum.RECRUITER)
    app = _application()
    job = _job(recruiter_id=uuid.uuid4())
    assert ApplicationPolicy.can_update_status(user, app, job) is False


# ── VariantPolicy.can_release ─────────────────────────────────────────────────

def test_variant_owner_approved_can_release():
    uid = uuid.uuid4()
    user = _user(RoleEnum.HUNTER, user_id=uid)
    v = _variant(user_id=uid, approval_status="approved")
    assert VariantPolicy.can_release(user, v) is True


def test_variant_owner_pending_cannot_release():
    uid = uuid.uuid4()
    user = _user(RoleEnum.HUNTER, user_id=uid)
    v = _variant(user_id=uid, approval_status="pending")
    assert VariantPolicy.can_release(user, v) is False


def test_variant_owner_rejected_cannot_release():
    uid = uuid.uuid4()
    user = _user(RoleEnum.HUNTER, user_id=uid)
    v = _variant(user_id=uid, approval_status="rejected")
    assert VariantPolicy.can_release(user, v) is False


def test_variant_other_user_cannot_release():
    user = _user(RoleEnum.HUNTER)
    v = _variant(user_id=uuid.uuid4(), approval_status="approved")
    assert VariantPolicy.can_release(user, v) is False


def test_variant_admin_can_release_any():
    user = _user(RoleEnum.ADMIN)
    v = _variant(user_id=uuid.uuid4(), approval_status="approved")
    assert VariantPolicy.can_release(user, v) is True


def test_variant_admin_can_release_even_pending():
    user = _user(RoleEnum.ADMIN)
    v = _variant(user_id=uuid.uuid4(), approval_status="pending")
    assert VariantPolicy.can_release(user, v) is True


# ── VariantPolicy.can_view ────────────────────────────────────────────────────

def test_variant_owner_can_view():
    uid = uuid.uuid4()
    user = _user(RoleEnum.HUNTER, user_id=uid)
    v = _variant(user_id=uid)
    assert VariantPolicy.can_view(user, v) is True


def test_variant_other_user_cannot_view():
    user = _user(RoleEnum.HUNTER)
    v = _variant(user_id=uuid.uuid4())
    assert VariantPolicy.can_view(user, v) is False


def test_variant_admin_can_view_any():
    user = _user(RoleEnum.ADMIN)
    v = _variant(user_id=uuid.uuid4())
    assert VariantPolicy.can_view(user, v) is True


def test_variant_can_view_str_uuid():
    uid = uuid.uuid4()
    user = _user(RoleEnum.HUNTER, user_id=uid)
    v = _variant(user_id=str(uid))
    assert VariantPolicy.can_view(user, v) is True
