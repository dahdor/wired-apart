"""Tests para utilidades de encoding cross-platform."""
from __future__ import annotations

import io
import sys

import pytest

from wired_apart import force_utf8_stdout


def test_force_utf8_stdout_is_idempotent() -> None:
    """Llamarla 2 veces seguidas no debe lanzar excepciones."""
    force_utf8_stdout()
    force_utf8_stdout()  # segunda vez debe ser no-op
    # Si llegó hasta acá, ya pasó
    assert True


def test_force_utf8_stdout_handles_non_reconfigurable_stream() -> None:
    """Si el stream no tiene reconfigure (Python < 3.7), no debe fallar."""
    # Simulamos un stream sin reconfigure (caso edge de streams exóticos)
    class FakeStream:
        encoding = "utf-8"

    original_stdout = sys.stdout
    try:
        sys.stdout = FakeStream()  # type: ignore[assignment]
        force_utf8_stdout()  # debe swallow el AttributeError
    finally:
        sys.stdout = original_stdout


def test_force_utf8_stdout_handles_oserror() -> None:
    """Si reconfigure lanza OSError (stream capturado por pytest), no falla."""
    class BrokenStream:
        def reconfigure(self, **kwargs):
            raise OSError("I/O operation on closed file")

    original_stdout = sys.stdout
    try:
        sys.stdout = BrokenStream()  # type: ignore[assignment]
        force_utf8_stdout()  # debe swallow
    finally:
        sys.stdout = original_stdout


def test_unicode_print_works_after_force_utf8_stdout(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Reproduce el bug que rompió el CI en Windows.

    En Windows, imprimir '✓' (U+2713) a stdout con code page cp1252
    lanza UnicodeEncodeError. Después de force_utf8_stdout(), el
    print() debe completarse sin error y el carácter debe llegar
    intacto a la captura.
    """
    # Aplicamos el fix (no-op en Linux, vital en Windows).
    force_utf8_stdout()
    # Caracteres problemáticos en cp1252:
    problematic = "✓ OK — año 2024: í ó ú ñ → ●"
    print(problematic)
    captured = capsys.readouterr()
    # En Windows, antes del fix esto lanzaba UnicodeEncodeError y el
    # print() no llegaba a stdout. Después del fix, el texto completo
    # debe estar en captured.out.
    assert "✓" in captured.out
    assert "í" in captured.out
    assert "→" in captured.out


def test_unicode_print_raises_without_fix_on_windows_code_page(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Demuestra el bug original: sin el fix, charmap falla con ✓.

    Forzamos el encoding de stdout a charmap (lo que Windows hace por
    defecto) y verificamos que imprimir '✓' sin el fix lanza
    UnicodeEncodeError. Esto es lo que rompía el CI en Windows.
    """
    # Forzamos encoding charmap (el bug original de Windows)
    fake_stdout = io.TextIOWrapper(
        io.BytesIO(), encoding="charmap", errors="strict", line_buffering=True
    )
    monkeypatch.setattr(sys, "stdout", fake_stdout)
    # Sin force_utf8_stdout(), imprimir '✓' debe fallar
    # (cp1252/charmap y latin-1 son ambos code pages de 1 byte que
    # no pueden representar U+2713; el mensaje exacto depende de la
    # versión de Python, así que aceptamos cualquiera).
    with pytest.raises(UnicodeEncodeError, match=r"charmap|latin-1"):
        print("✓ test")
    fake_stdout.close()
