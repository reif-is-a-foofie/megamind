"""
Megamind test runner — bubblegum light mode.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

MEGAMIND = Path(__file__).parent.parent
sys.path.insert(0, str(MEGAMIND))

from tests.suite import SUITES


# ─── Result types ─────────────────────────────────────────────

PASS  = "pass"
FAIL  = "fail"
SKIP  = "skip"
RUN   = "running"
WAIT  = "waiting"


# ─── Widgets ──────────────────────────────────────────────────

class SuiteItem(ListItem):
    def __init__(self, name: str, idx: int, **kwargs):
        super().__init__(**kwargs)
        self.suite_name = name
        self.suite_idx  = idx
        self._status    = WAIT

    def compose(self) -> ComposeResult:
        yield Label(f"  {self.suite_name}", classes="suite-label")

    def set_status(self, status: str) -> None:
        self._status = status
        self.remove_class("suite-pass", "suite-fail", "suite-run", "suite-wait")
        self.add_class(f"suite-{status}")


class TestRow(Static):
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self._name   = name
        self._status = WAIT
        self._detail = ""

    def render(self) -> str:
        if self._status == PASS:
            icon = "[bold #a8e6a3]✓[/bold #a8e6a3]"
        elif self._status == FAIL:
            icon = "[bold #ff6b9d]✗[/bold #ff6b9d]"
        elif self._status == RUN:
            icon = "[bold #c77dff]·[/bold #c77dff]"
        else:
            icon = "[dim]○[/dim]"

        name   = f"[dim #444]{self._name:<32}[/dim #444]"
        detail = f"[dim #888]{self._detail}[/dim #888]" if self._detail else ""
        return f"  {icon}  {name}  {detail}"

    def set_result(self, status: str, detail: str = "") -> None:
        self._status = status
        self._detail = detail
        self.refresh()


class SuiteBlock(Static):
    def __init__(self, suite: dict, **kwargs):
        super().__init__(**kwargs)
        self._suite = suite
        self._rows: dict[str, TestRow] = {}

    def compose(self) -> ComposeResult:
        name = self._suite["name"]
        yield Label(f"  ◆  {name}", classes="suite-header")
        for test_name, _ in self._suite["tests"]:
            row = TestRow(test_name, classes="test-row")
            self._rows[test_name] = row
            yield row

    def get_row(self, name: str) -> Optional[TestRow]:
        return self._rows.get(name)


# ─── App ──────────────────────────────────────────────────────

class TestApp(App):
    ENABLE_COMMAND_PALETTE = False

    CSS = """
    Screen {
        background: #fdf4ff;
        color: #222;
    }

    /* ── Top bar ── */
    #topbar {
        height: 1;
        background: #f0d6ff;
        color: #7b2d8b;
        padding: 0 2;
        text-style: bold;
    }

    /* ── Layout ── */
    #body {
        height: 1fr;
    }

    /* ── Suite list (left) ── */
    #suite-list-pane {
        width: 28;
        background: #fce4ff;
        border-right: solid #e8b4f8;
        padding: 1 0;
    }

    #suite-list-label {
        color: #9d4edd;
        text-style: bold;
        padding: 0 2;
        margin-bottom: 1;
    }

    ListView {
        background: transparent;
        border: none;
        padding: 0;
    }

    ListItem {
        background: transparent;
        padding: 0 1;
        height: 2;
    }

    ListItem:hover {
        background: #f0c6ff;
    }

    ListItem.--highlight {
        background: #e0a0ff;
    }

    .suite-label {
        color: #6b2d8b;
    }

    .suite-pass .suite-label {
        color: #2d8b4e;
    }

    .suite-fail .suite-label {
        color: #c0392b;
    }

    .suite-run .suite-label {
        color: #7b2d8b;
        text-style: bold;
    }

    /* ── Results pane (right) ── */
    #results-scroll {
        height: 1fr;
        padding: 1 0;
        background: #fdf4ff;
    }

    .suite-header {
        color: #9d4edd;
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
        padding: 0 2;
    }

    .test-row {
        height: 1;
        padding: 0;
        color: #333;
    }

    /* ── Status bar ── */
    #statusbar {
        height: 1;
        background: #f0d6ff;
        color: #7b2d8b;
        padding: 0 2;
    }
    """

    BINDINGS = [
        Binding("r",       "run_all",      "Run all"),
        Binding("enter",   "run_selected", "Run suite"),
        Binding("ctrl+q",  "quit",         "Quit"),
        Binding("q",       "quit",         "Quit"),
    ]

    passed  = reactive(0)
    failed  = reactive(0)
    running = reactive(False)

    def compose(self) -> ComposeResult:
        yield Static("  ✦  MEGAMIND TEST HARNESS", id="topbar")
        with Horizontal(id="body"):
            with Vertical(id="suite-list-pane"):
                yield Label("SUITES", id="suite-list-label")
                items = [SuiteItem(s["name"], i) for i, s in enumerate(SUITES)]
                yield ListView(*items, id="suite-list")
            yield ScrollableContainer(*[SuiteBlock(s) for s in SUITES], id="results-scroll")
        yield Static(self._status_text(), id="statusbar")

    def _status_text(self) -> str:
        p = self.passed
        f = self.failed
        total = sum(len(s["tests"]) for s in SUITES)
        done = p + f
        if self.running:
            return f"  running…   ✓ {p}  ✗ {f}  of {total}"
        elif done == 0:
            return f"  {total} tests  ·  press r to run all  ·  enter to run suite"
        elif f == 0:
            return f"  all {p} passed  ✓"
        else:
            return f"  ✓ {p} passed  ·  ✗ {f} failed  of {total}"

    def _refresh_status(self) -> None:
        try:
            bar = self.query_one("#statusbar", Static)
            bar.update(self._status_text())
        except Exception:
            pass

    def watch_passed(self, _: int) -> None:
        self._refresh_status()

    def watch_failed(self, _: int) -> None:
        self._refresh_status()

    def watch_running(self, _: bool) -> None:
        self._refresh_status()

    def action_run_all(self) -> None:
        if self.running:
            return
        self._reset()
        threading.Thread(target=self._run_suites, args=(list(range(len(SUITES))),), daemon=True).start()

    def action_run_selected(self) -> None:
        if self.running:
            return
        lv = self.query_one("#suite-list", ListView)
        idx = lv.index
        if idx is None:
            return
        self._reset_suite(idx)
        threading.Thread(target=self._run_suites, args=([idx],), daemon=True).start()

    def _reset(self) -> None:
        self.passed  = 0
        self.failed  = 0
        scroll = self.query_one("#results-scroll", ScrollableContainer)
        for block in scroll.query(SuiteBlock):
            for row in block.query(TestRow):
                row.set_result(WAIT)
        for item in self.query(SuiteItem):
            item.set_status(WAIT)

    def _reset_suite(self, idx: int) -> None:
        blocks = list(self.query(SuiteBlock))
        if idx < len(blocks):
            for row in blocks[idx].query(TestRow):
                row.set_result(WAIT)
        items = list(self.query(SuiteItem))
        if idx < len(items):
            items[idx].set_status(WAIT)

    def _run_suites(self, indices: list[int]) -> None:
        self.call_from_thread(setattr, self, "running", True)
        suite_items  = list(self.query(SuiteItem))
        suite_blocks = list(self.query(SuiteBlock))

        for idx in indices:
            suite    = SUITES[idx]
            s_item   = suite_items[idx]  if idx < len(suite_items)  else None
            s_block  = suite_blocks[idx] if idx < len(suite_blocks) else None

            if s_item:
                self.call_from_thread(s_item.set_status, RUN)

            suite_passed = True
            for test_name, test_fn in suite["tests"]:
                row = s_block.get_row(test_name) if s_block else None
                if row:
                    self.call_from_thread(row.set_result, RUN)
                try:
                    ok, detail = test_fn()
                except Exception as e:
                    ok, detail = False, f"exception: {e}"

                status = PASS if ok else FAIL
                if ok:
                    self.call_from_thread(self._inc, "passed")
                else:
                    self.call_from_thread(self._inc, "failed")
                    suite_passed = False

                if row:
                    self.call_from_thread(row.set_result, status, detail)

            if s_item:
                self.call_from_thread(s_item.set_status, PASS if suite_passed else FAIL)

        self.call_from_thread(setattr, self, "running", False)

        # Scroll to top after run
        scroll = self.query_one("#results-scroll", ScrollableContainer)
        self.call_from_thread(scroll.scroll_home, False)

    def _inc(self, attr: str) -> None:
        setattr(self, attr, getattr(self, attr) + 1)


def run():
    TestApp().run()


if __name__ == "__main__":
    run()
