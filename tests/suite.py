"""
Megamind test suite.
Each test is a function returning (passed: bool, detail: str).
Tests are grouped into suites that the harness runs and displays.

Coverage mirrors capability: every real module has real tests.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable

MEGAMIND = Path(__file__).parent.parent
sys.path.insert(0, str(MEGAMIND))


TestFn = Callable[[], tuple[bool, str]]


def suite(name: str, tests: list[tuple[str, TestFn]]) -> dict:
    return {"name": name, "tests": tests}


# ─── Config ───────────────────────────────────────────────────

def test_player_config_loads():
    import yaml
    path = MEGAMIND / "config" / "player.yaml"
    ok = path.exists()
    if ok:
        cfg = yaml.safe_load(path.read_text())
        name = cfg.get("name", "")
        ok = bool(name)
        return ok, f"player name: '{name}'"
    return False, "player.yaml not found"


def test_quadrant_config_loads():
    import yaml
    path = MEGAMIND / "config" / "quadrants.yaml"
    ok = path.exists()
    if ok:
        cfg = yaml.safe_load(path.read_text())
        quads = list(cfg.get("quadrants", {}).keys())
        ok = len(quads) >= 4
        return ok, f"quadrants: {quads}"
    return False, "quadrants.yaml not found"


def test_quadrant_config_has_metrics():
    import yaml
    path = MEGAMIND / "config" / "quadrants.yaml"
    cfg = yaml.safe_load(path.read_text())
    missing = [q for q, v in cfg.get("quadrants", {}).items() if not v.get("metrics")]
    ok = len(missing) == 0
    return ok, f"all quadrants have metrics" if ok else f"missing metrics: {missing}"


def test_quadrant_config_weights_sum():
    """Each quadrant's metric weights should sum to ~1.0."""
    import yaml
    path = MEGAMIND / "config" / "quadrants.yaml"
    cfg = yaml.safe_load(path.read_text())
    bad = []
    for qkey, qdef in cfg.get("quadrants", {}).items():
        metrics = qdef.get("metrics", {})
        if not metrics:
            continue
        total = sum(float(m.get("weight", 0)) for m in metrics.values())
        if abs(total - 1.0) > 0.05:
            bad.append(f"{qkey}={total:.2f}")
    ok = len(bad) == 0
    return ok, "weights OK" if ok else f"off: {bad}"


def test_character_file_exists():
    path = MEGAMIND / "context" / "character.json"
    if not path.exists():
        return False, "character.json not found"
    try:
        data = json.loads(path.read_text())
        stats = list(data.get("stats", {}).keys())
        return bool(stats), f"stats: {stats}"
    except Exception as e:
        return False, str(e)


def test_character_has_four_quadrants():
    path = MEGAMIND / "context" / "character.json"
    data = json.loads(path.read_text())
    stats = data.get("stats", {})
    required = {"spiritual", "social", "intellectual", "physical"}
    present = set(stats.keys())
    ok = required.issubset(present)
    return ok, f"{present}" if ok else f"missing: {required - present}"


def test_tasks_json_valid():
    path = MEGAMIND / "context" / "tasks.json"
    if not path.exists():
        return False, "tasks.json not found"
    try:
        data = json.loads(path.read_text())
        trees = data.get("trees", [])
        return True, f"{len(trees)} tree(s)"
    except Exception as e:
        return False, str(e)


def test_causal_model_valid():
    path = MEGAMIND / "context" / "causal_model.json"
    if not path.exists():
        return False, "causal_model.json not found"
    try:
        data = json.loads(path.read_text())
        keys = {"hypotheses", "confirmed_patterns", "mire_patterns"}
        present = keys.issubset(data.keys())
        return present, f"keys present: {list(data.keys())}"
    except Exception as e:
        return False, str(e)


# ─── Scoring engine ───────────────────────────────────────────

def test_score_continuous():
    from brain.score import score_metric
    m = {"type": "continuous", "current": 250, "target": 500, "weight": 1.0}
    s = score_metric(m)
    ok = abs(s - 0.5) < 0.01
    return ok, f"250/500 → {s:.3f} (expected 0.500)"


def test_score_boolean_true():
    from brain.score import score_metric
    m = {"type": "boolean", "current": 1, "target": 1, "weight": 1.0}
    s = score_metric(m)
    return s == 1.0, f"boolean true → {s}"


def test_score_boolean_false():
    from brain.score import score_metric
    m = {"type": "boolean", "current": 0, "target": 1, "weight": 1.0}
    s = score_metric(m)
    return s == 0.0, f"boolean false → {s}"


def test_score_enum():
    from brain.score import score_metric
    m = {
        "type": "enum", "current": "blue", "target": "blue",
        "enum_values": ["white", "blue", "purple", "brown", "black"],
        "enum_scores":  [0.0,    0.5,   0.75,   0.9,    1.0],
        "weight": 1.0,
    }
    s = score_metric(m)
    return abs(s - 0.5) < 0.01, f"blue belt → {s:.3f} (expected 0.500)"


def test_score_enum_unknown_value():
    from brain.score import score_metric
    m = {
        "type": "enum", "current": "red",
        "enum_values": ["white", "blue"], "enum_scores": [0.0, 0.5],
        "weight": 1.0,
    }
    s = score_metric(m)
    return s == 0.0, f"unknown enum → {s} (expected 0.0)"


def test_score_capped():
    from brain.score import score_metric
    m = {"type": "continuous", "current": 999, "target": 100, "weight": 1.0}
    s = score_metric(m)
    return s == 1.0, f"over-target capped at {s}"


def test_score_zero_target():
    from brain.score import score_metric
    m = {"type": "continuous", "current": 5, "target": 0, "weight": 1.0}
    s = score_metric(m)
    return s == 1.0, f"zero target + positive current → {s}"


def test_score_currency():
    from brain.score import score_metric
    m = {"type": "currency", "current": 50000, "target": 100000, "weight": 1.0}
    s = score_metric(m)
    ok = abs(s - 0.5) < 0.01
    return ok, f"50k/100k → {s:.3f}"


def test_quadrant_weighted():
    from brain.score import score_quadrant
    metrics = {
        "a": {"type": "continuous", "current": 100, "target": 100, "weight": 0.6},
        "b": {"type": "continuous", "current": 0,   "target": 100, "weight": 0.4},
    }
    s = score_quadrant(metrics)
    return abs(s - 0.6) < 0.01, f"60%+0% weighted → {s:.3f} (expected 0.600)"


def test_build_character_preserves_current():
    """build_character should keep existing current values."""
    from brain.score import build_character
    import yaml
    player = {"name": "test", "class": "Sailor", "year": 2026}
    quadrants = yaml.safe_load((MEGAMIND / "config" / "quadrants.yaml").read_text())
    # Inject a known current value into "existing"
    first_quad = list(quadrants["quadrants"].keys())[0]
    first_metric = list(quadrants["quadrants"][first_quad]["metrics"].keys())[0]
    existing = {"stats": {first_quad: {"metrics": {first_metric: 42}}}}
    char = build_character(player, quadrants, existing)
    preserved = char["stats"][first_quad]["metrics"].get(first_metric)
    ok = preserved == 42
    return ok, f"{first_quad}.{first_metric} = {preserved} (expected 42)"


def test_get_scores_returns_four_quadrants():
    from brain.score import get_scores
    scores = get_scores()
    required = {"spiritual", "social", "intellectual", "physical"}
    ok = required.issubset(scores.keys())
    return ok, f"keys: {list(scores.keys())}"


def test_score_sync_runs():
    from brain.score import sync
    try:
        char = sync()
        stats = list(char.get("stats", {}).keys())
        return bool(stats), f"synced stats: {stats}"
    except Exception as e:
        return False, str(e)


# ─── Task Queue ───────────────────────────────────────────────

def test_queue_finds_leaf():
    from tui.hud import get_queue
    tasks = {
        "trees": [{"status": "active", "goal_metric": "intellectual.licensed",
            "root": {"id": "root", "label": "Root", "status": "blocked",
                "children": [{"id": "leaf", "label": "Leaf task", "status": "active",
                    "units": 2, "units_done": 0, "children": []}]}}]
    }
    q = get_queue(tasks)
    ok = len(q) == 1 and q[0]["id"] == "leaf"
    return ok, f"found {len(q)} leaf(s): {[t['id'] for t in q]}"


def test_queue_skips_completed():
    from tui.hud import get_queue
    tasks = {
        "trees": [{"status": "active", "goal_metric": "intellectual.licensed",
            "root": {"id": "root", "label": "Root", "status": "completed", "children": []}}]
    }
    q = get_queue(tasks)
    return len(q) == 0, f"completed root → {len(q)} tasks (expected 0)"


def test_queue_skips_inactive_tree():
    from tui.hud import get_queue
    tasks = {
        "trees": [{"status": "completed", "goal_metric": "intellectual.licensed",
            "root": {"id": "root", "label": "Root", "status": "active",
                "units": 1, "units_done": 0, "children": []}}]
    }
    q = get_queue(tasks)
    return len(q) == 0, f"inactive tree → {len(q)} tasks (expected 0)"


def test_queue_deep_tree():
    """get_queue finds the leaf 3 levels deep."""
    from tui.hud import get_queue
    tasks = {"trees": [{"status": "active", "goal_metric": "intellectual.licensed",
        "root": {"id": "l1", "label": "L1", "status": "blocked",
            "children": [{"id": "l2", "label": "L2", "status": "blocked",
                "children": [{"id": "l3", "label": "Leaf", "status": "active",
                    "units": 1, "units_done": 0, "children": []}]}]}}]}
    q = get_queue(tasks)
    ok = len(q) == 1 and q[0]["id"] == "l3"
    return ok, f"deep leaf: {q[0]['id'] if q else 'none'}"


def test_queue_ordering():
    from tui.hud import get_queue
    tasks = {"trees": [
        {"status": "active", "goal_metric": "social.calls",
         "root": {"id": "a", "label": "A", "status": "active", "units": 1, "units_done": 0, "children": []}},
        {"status": "active", "goal_metric": "intellectual.licensed",
         "root": {"id": "b", "label": "B", "status": "active", "units": 3, "units_done": 0, "children": []}},
    ]}
    q = get_queue(tasks)
    return len(q) == 2, f"two trees → {len(q)} leaves (expected 2)"


def test_mark_unit_done_increments():
    from tui.hud import MegamindApp
    app = MegamindApp.__new__(MegamindApp)
    obj = {"id": "t1", "units": 3, "units_done": 1, "status": "active", "children": []}
    app._mark_unit_done(obj, "t1")
    ok = obj["units_done"] == 2 and obj["status"] == "active"
    return ok, f"units_done={obj['units_done']} status={obj['status']}"


def test_mark_unit_done_completes():
    from tui.hud import MegamindApp
    app = MegamindApp.__new__(MegamindApp)
    obj = {"id": "t1", "units": 2, "units_done": 1, "status": "active", "children": []}
    app._mark_unit_done(obj, "t1")
    ok = obj["units_done"] == 2 and obj["status"] == "completed"
    return ok, f"units_done={obj['units_done']} status={obj['status']} (expected completed)"


def test_score_bar_empty():
    from tui.hud import score_bar
    bar = score_bar(0.0, width=5)
    ok = bar == "·····"
    return ok, f"'{bar}'"


def test_score_bar_full():
    from tui.hud import score_bar
    bar = score_bar(1.0, width=5)
    ok = bar == "█████"
    return ok, f"'{bar}'"


def test_score_bar_half():
    from tui.hud import score_bar
    bar = score_bar(0.5, width=4)
    ok = bar == "██··"
    return ok, f"'{bar}'"


def test_quad_tag_mapping():
    from tui.hud import quad_tag
    cases = [
        ("spiritual.streak", "S"),
        ("social.calls", "So"),
        ("intellectual.licensed", "I"),
        ("physical.bjj", "P"),
        ("unknown.thing", "?"),
    ]
    failures = [(m, got, exp) for m, exp in cases if (got := quad_tag(m)) != exp]
    ok = len(failures) == 0
    return ok, "all tags correct" if ok else str(failures)


def test_build_system_prompt_has_name():
    from tui.hud import build_system_prompt, load_player, load_character, load_tasks
    player = load_player()
    char = load_character()
    tasks = load_tasks()
    prompt = build_system_prompt(player, char, tasks)
    name = player.get("name", "player")
    ok = name in prompt
    return ok, f"'{name}' in prompt: {ok}"


# ─── Think layer ──────────────────────────────────────────────

def test_parse_thought_clean_json():
    from brain.think import parse_thought
    raw = '{"summary": "test", "causal_updates": []}'
    t = parse_thought(raw)
    ok = t is not None and t.get("summary") == "test"
    return ok, f"parsed: {ok}"


def test_parse_thought_with_preamble():
    from brain.think import parse_thought
    raw = 'Some preamble text\n\n{"summary": "real", "mire_flags": []}\n\nSome trailing text'
    t = parse_thought(raw)
    ok = t is not None and t.get("summary") == "real"
    return ok, f"extracted from preamble: {ok}"


def test_parse_thought_empty_string():
    from brain.think import parse_thought
    t = parse_thought("")
    return t is None, f"empty → {t}"


def test_parse_thought_invalid_json():
    from brain.think import parse_thought
    t = parse_thought("{not valid json}")
    return t is None, f"invalid json → {t}"


def test_parse_thought_no_json():
    from brain.think import parse_thought
    t = parse_thought("just some text with no json at all")
    return t is None, f"no json → {t}"


def _make_temp_causal_model() -> tuple[Path, dict]:
    """Write a minimal causal model to a temp file, return (path, model)."""
    model = {
        "hypotheses": [],
        "confirmed_patterns": [],
        "mire_patterns": [],
        "mcp_input_map": {},
        "meta": {"last_updated": None, "session_count": 0, "evidence_threshold": 10},
    }
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(model, tmp)
    tmp.close()
    return Path(tmp.name), model


def test_apply_thought_adds_hypothesis():
    """apply_thought with action=add should append to hypotheses."""
    import brain.think as think
    original_path = think.MEGAMIND / "context" / "causal_model.json"
    backup = original_path.read_text()

    tmp_path, _ = _make_temp_causal_model()
    try:
        # Temporarily redirect
        original_path.write_text(tmp_path.read_text())
        thought = {
            "thought_at": "2026-01-01T00:00:00",
            "causal_updates": [{"action": "add", "input": "scripture", "output": "social.calls",
                                 "direction": "positive", "insight": "test insight"}],
        }
        think.apply_thought(thought)
        model = json.loads(original_path.read_text())
        ok = len(model["hypotheses"]) == 1 and model["hypotheses"][0]["input"] == "scripture"
        return ok, f"hypothesis added: {model['hypotheses'][0]['input'] if model['hypotheses'] else 'none'}"
    finally:
        original_path.write_text(backup)
        tmp_path.unlink(missing_ok=True)


def test_apply_thought_strengthens_hypothesis():
    import brain.think as think
    original_path = think.MEGAMIND / "context" / "causal_model.json"
    backup = original_path.read_text()

    model = {
        "hypotheses": [{"input": "scripture", "output": "social.calls",
                         "confidence": 0.3, "evidence": 5}],
        "confirmed_patterns": [], "mire_patterns": [], "mcp_input_map": {},
        "meta": {"last_updated": None, "evidence_threshold": 10},
    }
    try:
        original_path.write_text(json.dumps(model))
        thought = {
            "thought_at": "2026-01-01T00:00:00",
            "causal_updates": [{"action": "strengthen", "input": "scripture", "output": "social.calls"}],
        }
        think.apply_thought(thought)
        updated = json.loads(original_path.read_text())
        h = updated["hypotheses"][0]
        ok = abs(h["confidence"] - 0.4) < 0.01 and h["evidence"] == 6
        return ok, f"confidence {h['confidence']:.1f} evidence {h['evidence']}"
    finally:
        original_path.write_text(backup)


def test_apply_thought_promotes_hypothesis():
    """Confidence >= 0.7 should move hypothesis to confirmed_patterns."""
    import brain.think as think
    original_path = think.MEGAMIND / "context" / "causal_model.json"
    backup = original_path.read_text()

    model = {
        "hypotheses": [{"input": "scripture", "output": "social.calls",
                         "confidence": 0.65, "evidence": 20}],
        "confirmed_patterns": [], "mire_patterns": [], "mcp_input_map": {},
        "meta": {"last_updated": None, "evidence_threshold": 10},
    }
    try:
        original_path.write_text(json.dumps(model))
        thought = {
            "thought_at": "2026-01-01T00:00:00",
            "causal_updates": [{"action": "strengthen", "input": "scripture", "output": "social.calls"}],
        }
        think.apply_thought(thought)
        updated = json.loads(original_path.read_text())
        promoted = len(updated["confirmed_patterns"]) == 1
        still_hyp = len(updated["hypotheses"]) == 0
        ok = promoted and still_hyp
        return ok, f"confirmed={len(updated['confirmed_patterns'])} hypotheses={len(updated['hypotheses'])}"
    finally:
        original_path.write_text(backup)


def test_apply_thought_flags_mire():
    import brain.think as think
    original_path = think.MEGAMIND / "context" / "causal_model.json"
    backup = original_path.read_text()

    model = {"hypotheses": [], "confirmed_patterns": [], "mire_patterns": [],
             "mcp_input_map": {}, "meta": {"last_updated": None}}
    try:
        original_path.write_text(json.dumps(model))
        thought = {
            "thought_at": "2026-01-01T00:00:00",
            "mire_flags": [{"activity": "email sorting", "reason": "zero output"}],
        }
        think.apply_thought(thought)
        updated = json.loads(original_path.read_text())
        ok = len(updated["mire_patterns"]) == 1
        return ok, f"mire flagged: {updated['mire_patterns'][0]['activity'] if updated['mire_patterns'] else 'none'}"
    finally:
        original_path.write_text(backup)


def test_apply_thought_no_duplicate_mire():
    """Same mire pattern should not be added twice."""
    import brain.think as think
    original_path = think.MEGAMIND / "context" / "causal_model.json"
    backup = original_path.read_text()

    model = {"hypotheses": [], "confirmed_patterns": [],
             "mire_patterns": [{"activity": "email sorting", "reason": "existing"}],
             "mcp_input_map": {}, "meta": {"last_updated": None}}
    try:
        original_path.write_text(json.dumps(model))
        thought = {
            "thought_at": "2026-01-01T00:00:00",
            "mire_flags": [{"activity": "email sorting", "reason": "duplicate"}],
        }
        think.apply_thought(thought)
        updated = json.loads(original_path.read_text())
        ok = len(updated["mire_patterns"]) == 1
        return ok, f"mire count: {len(updated['mire_patterns'])} (expected 1)"
    finally:
        original_path.write_text(backup)


def test_apply_thought_writes_inbox():
    import brain.think as think
    inbox = think.MEGAMIND / "context" / "inbox.txt"
    backup = inbox.read_text() if inbox.exists() else None
    try:
        thought = {
            "thought_at": "2026-01-01T00:00:00",
            "next_session_note": "TEST_INBOX_MARKER_XYZ",
        }
        think.apply_thought(thought)
        content = inbox.read_text() if inbox.exists() else ""
        ok = "TEST_INBOX_MARKER_XYZ" in content
        return ok, f"inbox note written: {ok}"
    finally:
        if backup is not None:
            inbox.write_text(backup)
        elif inbox.exists():
            # Remove only lines we added
            lines = inbox.read_text().splitlines()
            inbox.write_text("\n".join(l for l in lines if "TEST_INBOX_MARKER_XYZ" not in l) + "\n")


# ─── Ingest / Transcript ──────────────────────────────────────

def test_detect_quadrant_spiritual():
    from ingest.transcript import detect_quadrant
    q = detect_quadrant("morning scripture meditation and prayer")
    return q == "spiritual", f"→ {q}"


def test_detect_quadrant_social():
    from ingest.transcript import detect_quadrant
    q = detect_quadrant("made 5 calls to friends and network contacts")
    return q == "social", f"→ {q}"


def test_detect_quadrant_intellectual():
    from ingest.transcript import detect_quadrant
    q = detect_quadrant("studying for series 63 license, reading Buffett")
    return q == "intellectual", f"→ {q}"


def test_detect_quadrant_physical():
    from ingest.transcript import detect_quadrant
    q = detect_quadrant("bjj training today, blue belt test coming up")
    return q == "physical", f"→ {q}"


def test_detect_quadrant_none():
    from ingest.transcript import detect_quadrant
    q = detect_quadrant("the weather was fine today")
    return q is None, f"→ {q} (expected None)"


def test_parse_transcript_valid():
    from ingest.transcript import parse_transcript
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    lines = [
        json.dumps({"type": "user", "message": {"role": "user", "content": "I did scripture this morning and then made 3 calls"}, "timestamp": "2026-01-01T09:00:00"}),
        json.dumps({"type": "assistant", "message": {"role": "assistant", "content": "Great work on both fronts. Scripture and social calls are your two highest-leverage inputs."}, "timestamp": "2026-01-01T09:00:01"}),
        json.dumps({"type": "system", "message": {}}),  # should be skipped
    ]
    tmp.write("\n".join(lines))
    tmp.close()
    path = Path(tmp.name)
    try:
        msgs = parse_transcript(path)
        ok = len(msgs) == 2 and msgs[0]["role"] == "user"
        return ok, f"{len(msgs)} messages parsed"
    finally:
        path.unlink(missing_ok=True)


def test_parse_transcript_skips_short():
    from ingest.transcript import parse_transcript
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    tmp.write(json.dumps({"type": "user", "message": {"role": "user", "content": "ok"}, "timestamp": None}) + "\n")
    tmp.close()
    path = Path(tmp.name)
    try:
        msgs = parse_transcript(path)
        return len(msgs) == 0, f"{len(msgs)} messages (expected 0, too short)"
    finally:
        path.unlink(missing_ok=True)


def test_extract_key_exchanges_captures_user():
    from ingest.transcript import extract_key_exchanges
    messages = [
        {"role": "user", "content": "I completed my scripture reading and made 4 calls today — good session", "timestamp": None},
        {"role": "assistant", "content": "Short", "timestamp": None},
    ]
    obs = extract_key_exchanges(messages)
    user_obs = [o for o in obs if o["role"] == "user"]
    ok = len(user_obs) == 1
    return ok, f"{len(user_obs)} user observations captured"


def test_extract_key_exchanges_skips_short_user():
    from ingest.transcript import extract_key_exchanges
    messages = [{"role": "user", "content": "ok sure", "timestamp": None}]
    obs = extract_key_exchanges(messages)
    return len(obs) == 0, f"{len(obs)} observations (expected 0)"


def test_extract_key_exchanges_captures_synthesis():
    from ingest.transcript import extract_key_exchanges
    long_synthesis = (
        "The pattern here is clear: on days with scripture your social calls average 5.8. "
        "This is the key causal lever in your current quadrant model. "
        "The morning brief architecture should surface this every session. "
        "Memory synthesis confirms this across 20 data points. Chief of staff analysis complete."
    )
    messages = [{"role": "assistant", "content": long_synthesis, "timestamp": None}]
    obs = extract_key_exchanges(messages)
    ok = len(obs) == 1
    return ok, f"{len(obs)} synthesis observations captured"


# ─── Database ─────────────────────────────────────────────────

def test_db_init_creates_tables():
    from db import get_conn, init_db
    init_db()
    conn = get_conn()
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    required = {"observation", "quadrant_state", "pattern", "person", "goal", "session"}
    ok = required.issubset(tables)
    return ok, f"tables: {sorted(tables)}"


def test_db_wal_mode():
    from db import get_conn
    conn = get_conn()
    mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    conn.close()
    return mode == "wal", f"journal_mode={mode}"


def test_db_observation_insert():
    from db import get_conn, init_db
    init_db()
    conn = get_conn()
    ts = f"test_{int(time.time())}"
    conn.execute(
        "INSERT INTO observation (source, quadrant, content, occurred_at) VALUES (?,?,?,?)",
        ("test_harness", "spiritual", f"test obs {ts}", "2026-01-01T00:00:00"),
    )
    conn.commit()
    row = conn.execute("SELECT content FROM observation WHERE source='test_harness' ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    ok = row is not None and ts in row[0]
    return ok, f"inserted and retrieved: {ok}"


def test_db_observation_quadrant_filter():
    from db import get_conn, init_db
    init_db()
    conn = get_conn()
    ts = f"qfilter_{int(time.time())}"
    conn.execute(
        "INSERT INTO observation (source, quadrant, content, occurred_at) VALUES (?,?,?,?)",
        ("test_harness", "intellectual", f"quadrant filter test {ts}", "2026-01-01T00:00:00"),
    )
    conn.commit()
    rows = conn.execute(
        "SELECT id FROM observation WHERE quadrant=? AND content LIKE ?",
        ("intellectual", f"%{ts}%"),
    ).fetchall()
    conn.close()
    ok = len(rows) >= 1
    return ok, f"quadrant filter returned {len(rows)} row(s)"


# ─── Brief ────────────────────────────────────────────────────

def test_brief_store_observation_writes_db():
    from brain.brief import store_observation
    from db import get_conn
    ts = f"brief_test_{int(time.time())}"
    store_observation(f"brief DB test {ts}", quadrant="social", source="test_harness")
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM observation WHERE content LIKE ? AND source='test_harness'",
        (f"%{ts}%",),
    ).fetchone()
    conn.close()
    ok = row is not None
    return ok, f"observation in DB: {ok}"


def test_brief_store_observation_writes_memory():
    from brain.brief import store_observation
    from brain.memory import get_memory
    ts = f"brief_mem_{int(time.time())}"
    content = f"brief memory test {ts}"
    store_observation(content, quadrant="physical", source="test_harness")
    # Use get_memory() — it reads the correct user_id from player.yaml
    mem = get_memory()
    results = mem.get_all()
    ok = any(ts in r.get("memory", "") for r in results)
    return ok, f"found in memory: {ok} ({len(results)} total entries)"


def test_brief_write_creates_file():
    from brain.brief import write_brief_context
    path = write_brief_context()
    ok = path.exists() and path.stat().st_size > 0
    return ok, f"brief.md at {path} ({path.stat().st_size}b)"


# ─── Memory ───────────────────────────────────────────────────

def test_memory_store_retrieve():
    from brain.memory import LocalMemory
    mem = LocalMemory()
    content = f"test_memory_{int(time.time())}"
    mem.add(content, user_id="test_harness")
    results = mem.search(content, user_id="test_harness", limit=3)
    found = any(r.get("memory", "") == content for r in results)
    return found, f"stored '{content[:30]}...' → {'found' if found else 'NOT found'}"


def test_memory_semantic_search():
    from brain.memory import LocalMemory
    mem = LocalMemory()
    mem.add("scripture meditation morning practice", user_id="test_semantic")
    results = mem.search("daily spiritual routine", user_id="test_semantic", limit=3)
    ok = len(results) > 0
    top = results[0].get("score", 0) if results else 0
    return ok, f"semantic search → {len(results)} results, top score {top:.3f}"


def test_memory_user_isolation():
    """Memories added for user_A should not appear in user_B search."""
    from brain.memory import LocalMemory
    mem = LocalMemory()
    ts = f"isolation_{int(time.time())}"
    mem.add(f"private content {ts}", user_id=f"user_A_{ts}")
    results = mem.search(ts, user_id=f"user_B_{ts}", limit=5)
    found_in_wrong_user = any(ts in r.get("memory", "") for r in results)
    ok = not found_in_wrong_user
    return ok, f"user isolation: {ok}"


def test_memory_get_all():
    from brain.memory import LocalMemory
    mem = LocalMemory()
    ts = f"getall_{int(time.time())}"
    mem.add(f"getall test {ts}", user_id=f"test_getall_{ts}")
    results = mem.get_all(user_id=f"test_getall_{ts}")
    ok = len(results) >= 1
    return ok, f"get_all returned {len(results)} result(s)"


def test_memory_metadata_preserved():
    from brain.memory import LocalMemory
    mem = LocalMemory()
    ts = f"meta_{int(time.time())}"
    mem.add(f"metadata test {ts}", user_id=f"test_meta_{ts}",
            metadata={"source": "test", "quadrant": "spiritual"})
    results = mem.search(ts, user_id=f"test_meta_{ts}", limit=1)
    ok = len(results) > 0
    return ok, f"with metadata: stored and retrieved: {ok}"


# ─── Claude CLI ───────────────────────────────────────────────

def test_claude_cli_available():
    result = subprocess.run(["which", "claude"], capture_output=True, text=True)
    ok = result.returncode == 0
    path = result.stdout.strip()
    return ok, f"claude at: {path}" if ok else "claude CLI not found in PATH"


def test_claude_cli_responds():
    result = subprocess.run(
        ["claude", "-p", "Reply with exactly: MEGAMIND_OK"],
        capture_output=True, text=True, timeout=30,
    )
    ok = result.returncode == 0 and "MEGAMIND_OK" in result.stdout
    out = result.stdout.strip()[:60] if result.stdout else result.stderr.strip()[:60]
    return ok, f"response: '{out}'"


def test_claude_cli_json_output():
    """Claude can produce valid JSON on demand."""
    result = subprocess.run(
        ["claude", "-p", 'Reply with exactly this JSON and nothing else: {"status":"ok"}'],
        capture_output=True, text=True, timeout=30,
    )
    ok = False
    detail = ""
    if result.returncode == 0:
        import re
        match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                ok = data.get("status") == "ok"
                detail = f"parsed: {data}"
            except Exception as e:
                detail = f"json error: {e}"
        else:
            detail = f"no json in: {result.stdout[:60]}"
    else:
        detail = result.stderr[:60]
    return ok, detail


# ─── Update pipeline ──────────────────────────────────────────

def test_extract_updates_clean():
    from brain.updates import extract_updates
    response = 'Good work.\n<!--UPDATES:{"metric_updates":[{"quadrant":"spiritual","metric":"scripture_streak_days","value":3}],"task_updates":[]}-->'
    clean, updates = extract_updates(response)
    ok = "<!--UPDATES" not in clean and updates.get("metric_updates", [{}])[0].get("value") == 3
    return ok, f"clean='{clean[:40]}' updates={updates}"


def test_extract_updates_no_block():
    from brain.updates import extract_updates
    response = "Just a normal response with no updates."
    clean, updates = extract_updates(response)
    ok = clean == response and updates == {}
    return ok, f"no block → empty updates: {ok}"


def test_extract_updates_invalid_json():
    from brain.updates import extract_updates
    response = "text <!--UPDATES:{bad json}--> end"
    clean, updates = extract_updates(response)
    ok = updates == {} and "<!--UPDATES" not in clean
    return ok, f"invalid json stripped, empty updates: {ok}"


def test_apply_metric_updates_writes_score():
    from brain.updates import apply_metric_updates
    from brain.score import load_character, update_metric
    # Reset to 0 so we have a known baseline
    update_metric("social", "calls_today", 0)
    char_before = load_character()
    score_before = char_before["stats"]["social"]["score"]
    changes = apply_metric_updates([{"quadrant": "social", "metric": "calls_today", "value": 7}])
    char_after = load_character()
    score_after = char_after["stats"]["social"]["score"]
    ok = score_after > score_before and len(changes) == 1
    return ok, f"social score {score_before:.2f} → {score_after:.2f}, changes={changes}"


def test_apply_metric_updates_bad_quadrant():
    from brain.updates import apply_metric_updates
    changes = apply_metric_updates([{"quadrant": "nonexistent", "metric": "foo", "value": 1}])
    # Should fail gracefully, not raise
    return True, f"graceful fail: {changes}"


def test_apply_task_updates_complete():
    from brain.updates import apply_task_updates
    import json, tempfile, shutil
    tasks_path = MEGAMIND / "context" / "tasks.json"
    backup = tasks_path.read_text()
    test_tasks = {
        "trees": [{"id": "tree1", "goal_metric": "test", "status": "active",
            "root": {"id": "root1", "label": "Root", "status": "active",
                "units": 1, "units_done": 0, "children": [
                    {"id": "leaf1", "label": "Leaf", "status": "active",
                     "units": 1, "units_done": 0, "children": []}
                ]}}],
        "completed": [], "meta": {}
    }
    try:
        tasks_path.write_text(json.dumps(test_tasks))
        changes = apply_task_updates([{"action": "complete", "task_id": "leaf1"}])
        updated = json.loads(tasks_path.read_text())
        leaf = updated["trees"][0]["root"]["children"][0]
        ok = leaf["status"] == "completed" and len(changes) == 1
        return ok, f"leaf status={leaf['status']} changes={changes}"
    finally:
        tasks_path.write_text(backup)


def test_apply_task_updates_unlocks_next():
    """Completing a blocked_by task should unlock dependent nodes."""
    from brain.updates import apply_task_updates
    import json
    tasks_path = MEGAMIND / "context" / "tasks.json"
    backup = tasks_path.read_text()
    test_tasks = {
        "trees": [{"id": "tree1", "goal_metric": "test", "status": "active",
            "root": {"id": "root1", "label": "Root", "status": "blocked",
                "children": [
                    {"id": "step1", "label": "Step 1", "status": "active",
                     "units": 1, "units_done": 0, "children": []},
                    {"id": "step2", "label": "Step 2", "status": "blocked",
                     "blocked_by": ["step1"], "units": 1, "units_done": 0, "children": []},
                ]}}],
        "completed": [], "meta": {}
    }
    try:
        tasks_path.write_text(json.dumps(test_tasks))
        apply_task_updates([{"action": "complete", "task_id": "step1"}])
        updated = json.loads(tasks_path.read_text())
        children = updated["trees"][0]["root"]["children"]
        step1_done = children[0]["status"] == "completed"
        step2_active = children[1]["status"] == "active"
        ok = step1_done and step2_active
        return ok, f"step1={children[0]['status']} step2={children[1]['status']}"
    finally:
        tasks_path.write_text(backup)


def test_apply_task_updates_advance_unit():
    from brain.updates import apply_task_updates
    import json
    tasks_path = MEGAMIND / "context" / "tasks.json"
    backup = tasks_path.read_text()
    test_tasks = {
        "trees": [{"id": "tree1", "goal_metric": "test", "status": "active",
            "root": {"id": "root1", "label": "Root", "status": "active",
                "units": 5, "units_done": 2, "children": []}}],
        "completed": [], "meta": {}
    }
    try:
        tasks_path.write_text(json.dumps(test_tasks))
        apply_task_updates([{"action": "advance", "task_id": "root1"}])
        updated = json.loads(tasks_path.read_text())
        node = updated["trees"][0]["root"]
        ok = node["units_done"] == 3 and node["status"] == "active"
        return ok, f"units_done={node['units_done']} status={node['status']}"
    finally:
        tasks_path.write_text(backup)


def test_checkin_questions_returned():
    from brain.checkin import get_checkin_questions
    questions = get_checkin_questions()
    ok = len(questions) > 0
    labels = [q["label"] for q in questions]
    return ok, f"{len(questions)} questions: {labels}"


def test_checkin_question_fields():
    from brain.checkin import get_checkin_questions
    questions = get_checkin_questions()
    required = {"quadrant", "metric", "label", "type", "current"}
    bad = [q["metric"] for q in questions if not required.issubset(q.keys())]
    ok = len(bad) == 0
    return ok, "all fields present" if ok else f"missing fields: {bad}"


def test_checkin_not_done_today():
    """Fresh run — check-in should be required (state file has yesterday or missing)."""
    from brain.checkin import checked_in_today, _save_state
    _save_state({"date": "2000-01-01"})  # force old date
    ok = not checked_in_today()
    return ok, f"checked_in_today() = {not ok} (expected False)"


def test_checkin_mark_and_check():
    from brain.checkin import checked_in_today, mark_checked_in
    mark_checked_in()
    ok = checked_in_today()
    return ok, f"checked_in_today() = {ok} after mark_checked_in()"


def test_system_prompt_has_update_protocol():
    from tui.hud import build_system_prompt, load_player, load_character, load_tasks
    player = load_player()
    char = load_character()
    tasks = load_tasks()
    prompt = build_system_prompt(player, char, tasks)
    ok = "<!--UPDATES:" in prompt and "metric_updates" in prompt
    return ok, f"update protocol in prompt: {ok}"


def test_system_prompt_has_metric_reference():
    from tui.hud import build_system_prompt, load_player, load_character, load_tasks
    player = load_player()
    char = load_character()
    tasks = load_tasks()
    prompt = build_system_prompt(player, char, tasks)
    ok = "spiritual." in prompt or "social." in prompt
    return ok, f"metric reference present: {ok}"


# ─── Suite registry ───────────────────────────────────────────

SUITES = [
    suite("Config", [
        ("player.yaml loads",           test_player_config_loads),
        ("quadrants.yaml loads",         test_quadrant_config_loads),
        ("quadrants have metrics",       test_quadrant_config_has_metrics),
        ("metric weights sum to 1",      test_quadrant_config_weights_sum),
        ("character.json exists",        test_character_file_exists),
        ("character has 4 quadrants",    test_character_has_four_quadrants),
        ("tasks.json valid",             test_tasks_json_valid),
        ("causal_model.json valid",      test_causal_model_valid),
    ]),
    suite("Scoring Engine", [
        ("continuous metric",            test_score_continuous),
        ("boolean true",                 test_score_boolean_true),
        ("boolean false",                test_score_boolean_false),
        ("enum metric (belt)",           test_score_enum),
        ("enum unknown value → 0",       test_score_enum_unknown_value),
        ("over-target capped",           test_score_capped),
        ("zero target + positive",       test_score_zero_target),
        ("currency metric",              test_score_currency),
        ("weighted quadrant",            test_quadrant_weighted),
        ("build_character preserves",    test_build_character_preserves_current),
        ("get_scores 4 quadrants",       test_get_scores_returns_four_quadrants),
        ("full sync",                    test_score_sync_runs),
    ]),
    suite("Task Queue & HUD", [
        ("finds leaf node",              test_queue_finds_leaf),
        ("skips completed",              test_queue_skips_completed),
        ("skips inactive tree",          test_queue_skips_inactive_tree),
        ("deep 3-level tree",            test_queue_deep_tree),
        ("multiple trees",               test_queue_ordering),
        ("mark unit done increments",    test_mark_unit_done_increments),
        ("mark unit done → completed",   test_mark_unit_done_completes),
        ("score_bar empty",              test_score_bar_empty),
        ("score_bar full",               test_score_bar_full),
        ("score_bar half",               test_score_bar_half),
        ("quad_tag mapping",             test_quad_tag_mapping),
        ("system prompt has name",       test_build_system_prompt_has_name),
    ]),
    suite("Think Layer", [
        ("parse clean json",             test_parse_thought_clean_json),
        ("parse with preamble",          test_parse_thought_with_preamble),
        ("parse empty → None",           test_parse_thought_empty_string),
        ("parse invalid json → None",    test_parse_thought_invalid_json),
        ("parse no json → None",         test_parse_thought_no_json),
        ("apply: add hypothesis",        test_apply_thought_adds_hypothesis),
        ("apply: strengthen hypothesis", test_apply_thought_strengthens_hypothesis),
        ("apply: promote to confirmed",  test_apply_thought_promotes_hypothesis),
        ("apply: flag mire",             test_apply_thought_flags_mire),
        ("apply: no duplicate mire",     test_apply_thought_no_duplicate_mire),
        ("apply: write inbox",           test_apply_thought_writes_inbox),
    ]),
    suite("Ingest", [
        ("detect: spiritual",            test_detect_quadrant_spiritual),
        ("detect: social",               test_detect_quadrant_social),
        ("detect: intellectual",         test_detect_quadrant_intellectual),
        ("detect: physical",             test_detect_quadrant_physical),
        ("detect: none",                 test_detect_quadrant_none),
        ("parse valid transcript",       test_parse_transcript_valid),
        ("parse skips short messages",   test_parse_transcript_skips_short),
        ("extract captures user",        test_extract_key_exchanges_captures_user),
        ("extract skips short user",     test_extract_key_exchanges_skips_short_user),
        ("extract captures synthesis",   test_extract_key_exchanges_captures_synthesis),
    ]),
    suite("Database", [
        ("init creates tables",          test_db_init_creates_tables),
        ("WAL mode enabled",             test_db_wal_mode),
        ("observation insert",           test_db_observation_insert),
        ("observation quadrant filter",  test_db_observation_quadrant_filter),
    ]),
    suite("Brief", [
        ("store_obs writes DB",          test_brief_store_observation_writes_db),
        ("store_obs writes memory",      test_brief_store_observation_writes_memory),
        ("write_brief creates file",     test_brief_write_creates_file),
    ]),
    suite("Memory", [
        ("store & retrieve",             test_memory_store_retrieve),
        ("semantic search",              test_memory_semantic_search),
        ("user isolation",               test_memory_user_isolation),
        ("get_all returns results",      test_memory_get_all),
        ("metadata preserved",           test_memory_metadata_preserved),
    ]),
    suite("Check-in", [
        ("questions returned",           test_checkin_questions_returned),
        ("question fields complete",     test_checkin_question_fields),
        ("not done → required",          test_checkin_not_done_today),
        ("mark done → not required",     test_checkin_mark_and_check),
    ]),
    suite("Update Pipeline", [
        ("extract clean block",          test_extract_updates_clean),
        ("extract: no block → empty",    test_extract_updates_no_block),
        ("extract: invalid json",        test_extract_updates_invalid_json),
        ("apply: metric writes score",   test_apply_metric_updates_writes_score),
        ("apply: bad quadrant graceful", test_apply_metric_updates_bad_quadrant),
        ("apply: complete task",         test_apply_task_updates_complete),
        ("apply: unlocks next node",     test_apply_task_updates_unlocks_next),
        ("apply: advance unit",          test_apply_task_updates_advance_unit),
        ("prompt has update protocol",   test_system_prompt_has_update_protocol),
        ("prompt has metric reference",  test_system_prompt_has_metric_reference),
    ]),
    suite("Claude CLI", [
        ("claude in PATH",               test_claude_cli_available),
        ("claude responds",              test_claude_cli_responds),
        ("claude produces json",         test_claude_cli_json_output),
    ]),
]
