# SPDX-License-Identifier: MIT
"""Ansible test plugin: number, non-empty string, or list of numbers / non-empty strings."""

from __future__ import annotations

import numbers


def _is_number(value):
    """True for int/float/etc., but never for bool (bool is a Number subclass in Python)."""
    if isinstance(value, bool):
        return False
    return isinstance(value, numbers.Number)


def _is_nonempty_str(value):
    return isinstance(value, str) and value.strip() != ""


def auditd_scalar_or_mixed_list(value):
    """
    Return True if value is:
      - a number (not bool), or
      - a non-empty string (after strip), or
      - a non-empty list/tuple whose elements are each a number or non-empty string.
    """
    if value is None:
        return False
    if _is_number(value) or _is_nonempty_str(value):
        return True
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return False
        return all(_is_number(item) or _is_nonempty_str(item) for item in value)
    return False


def auditd_non_empty_str_or_list(value):
    """
    Return True if value is:
      - a non-empty string (after strip), or
      - a non-empty list/tuple whose elements are each a non-empty string.
    """
    if value is None:
        return False
    if _is_nonempty_str(value):
        return True
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return False
        return all(_is_nonempty_str(item) for item in value)
    return False


class TestModule:
    """Jinja test: ``value is auditd_scalar_or_mixed_list`` or ``value is auditd_non_empty_str_or_list``."""

    def tests(self):
        return {
            "auditd_scalar_or_mixed_list": auditd_scalar_or_mixed_list,
            "auditd_non_empty_str_or_list": auditd_non_empty_str_or_list,
        }
