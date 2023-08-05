from __future__ import annotations
import typing as t
import re

from flask import current_app
from sqlalchemy import select
from sqlalchemy.orm import Session


__all__ = (
    'generate_slug',
    'get_sqla_session',
)


def generate_slug(
    slug_field: t.Any,
    slug: str,
    session: t.Optional[Session] = None,
) -> str:
    """
    Generates a unique slug based on the passed value.

    Arguments:
        slug_field: Model attribute containing slug.
        slug (str): The desired slug value.
        session (Session): SQLAlchemy session.
    """
    if session is None:
        session = get_sqla_session()

    pattern = r'^%s(?:-([0-9]+))?$' % slug

    stmt = (
        select(slug_field)
            .where(slug_field.regexp_match(pattern))
            .order_by(slug_field.desc())
            .limit(1)
    )
    found = session.scalar(stmt)

    if not found:
        return slug

    match = re.match(pattern, found)

    if match is None:
        raise AssertionError('The query found one result for the regular expression.')

    return '{}-{}'.format(slug, int(match.group(1)) + 1)


def get_sqla_session() -> Session:
    """Returns the current session instance from application context."""
    ext = current_app.extensions.get('sqlalchemy')

    if ext is None:
        raise RuntimeError(
            'An extension named sqlalchemy was not found '
            'in the list of registered extensions for the current application.'
        )

    return t.cast(Session, ext.db.session)
