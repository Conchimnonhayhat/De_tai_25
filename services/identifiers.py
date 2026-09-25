"""Business codes are strings, including legacy codes made only of digits."""

import re
import secrets


CODE_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$')


def normalize_code(value, label='Mã'):
    code = str(value or '').strip().upper()
    if not CODE_PATTERN.fullmatch(code):
        raise ValueError(f'{label} phải có 1–32 ký tự chữ/số, dấu gạch ngang hoặc gạch dưới.')
    return code


def new_code(prefix):
    """Generate a non-sequential public code without relying on database row IDs."""
    return prefix + secrets.token_hex(8).upper()
