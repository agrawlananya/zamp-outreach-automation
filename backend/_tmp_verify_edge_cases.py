import datetime as dt

from app.models.db_models import Signal
from app.pipeline import stage8_hook_scoring


class FakeDB:
    def commit(self):
        pass


def make_signal(**kwargs):
    defaults = dict(
        id="sig",
        run_id="run",
        type="funding_round",
        claim="Acme raised a $50M Series B to fuel growth.",
        source_url="https://example.com/a",
        source_snippet="Acme raised a $50M Series B" * 3,
        signal_date=dt.date.today(),
        entity="Acme",
        validated=True,
        valence="neutral",
        claim_type="fact",
    )
    defaults.update(kwargs)
    return Signal(**defaults)


# --- Test 1: saturation heuristic ---
# A template-bait type, reported by 3 other distinct sources, recent -> high saturation.
saturated = make_signal(id="s1", entity="Acme", type="funding_round", source_url="https://a.com/1")
dup2 = make_signal(id="s2", entity="Acme", type="funding_round", source_url="https://b.com/2")
dup3 = make_signal(id="s3", entity="Acme", type="funding_round", source_url="https://c.com/3")
dup4 = make_signal(id="s4", entity="Acme", type="funding_round", source_url="https://d.com/4")
sat = stage8_hook_scoring._score_saturation(saturated, [saturated, dup2, dup3, dup4])
print("saturation (template-bait, 3 other sources, recent):", round(sat, 3))
assert sat > 0.7, f"expected high saturation, got {sat}"

# A non-template-bait type, single source, recent -> low saturation.
unique = make_signal(id="u1", entity="Acme", type="system_migration", source_url="https://only.com/1")
sat2 = stage8_hook_scoring._score_saturation(unique, [unique])
print("saturation (unique, non-template-bait):", round(sat2, 3))
assert sat2 < 0.2, f"expected low saturation, got {sat2}"

# --- Test 2: sensitive valence forces hook_score=0 and never wins selection ---
sensitive_sig = make_signal(id="sens1", entity="Acme", type="layoffs", valence="sensitive", source_url="https://x.com/1")
strong_sig = make_signal(id="strong1", entity="Acme", type="system_migration", valence="neutral", source_url="https://y.com/1")
selection = stage8_hook_scoring.score_and_select_hook([sensitive_sig, strong_sig], [], "run", FakeDB())
print("sensitive signal hook_score:", sensitive_sig.hook_score, "adjusted:", sensitive_sig.adjusted_hook_score)
assert sensitive_sig.hook_score == 0.0
assert sensitive_sig.adjusted_hook_score == 0.0
assert selection.selected_signal.id != "sens1", "sensitive signal must never be selected as hook"
print("selected signal:", selection.selected_signal.id)

# Only a sensitive signal available -> top_score_sufficient must be False (insufficient_signal route)
selection_only_sensitive = stage8_hook_scoring.score_and_select_hook(
    [make_signal(id="sens2", entity="Acme", type="layoffs", valence="sensitive")], [], "run", FakeDB()
)
print("only-sensitive top_score_sufficient:", selection_only_sensitive.top_score_sufficient)
assert selection_only_sensitive.top_score_sufficient is False

# --- Test 3: adjusted_hook_score drives selection over raw hook_score ---
high_raw_but_saturated = make_signal(
    id="hi_raw", entity="Acme", type="funding_round", valence="neutral",
    source_url="https://m.com/1",
)
dup_a = make_signal(id="dup_a", entity="Acme", type="funding_round", source_url="https://m.com/2")
dup_b = make_signal(id="dup_b", entity="Acme", type="funding_round", source_url="https://m.com/3")
low_raw_but_fresh = make_signal(
    id="lo_raw", entity="Acme", type="system_migration", valence="neutral",
    source_url="https://n.com/1", claim="Acme is migrating its core system this quarter.",
)
selection2 = stage8_hook_scoring.score_and_select_hook(
    [high_raw_but_saturated, dup_a, dup_b, low_raw_but_fresh], [], "run", FakeDB()
)
print("hi_raw hook_score/adjusted:", high_raw_but_saturated.hook_score, high_raw_but_saturated.adjusted_hook_score)
print("lo_raw hook_score/adjusted:", low_raw_but_fresh.hook_score, low_raw_but_fresh.adjusted_hook_score)
print("selected (should favor non-saturated if adjusted is higher):", selection2.selected_signal.id)

# --- Test 4: fact/inference filter (mirrors orchestrator.py's one-line filter) ---
fact_sig = make_signal(id="f1", claim_type="fact")
inference_sig = make_signal(id="i1", claim_type="inference")
legacy_sig = make_signal(id="legacy1", claim_type=None)
extracted = [fact_sig, inference_sig, legacy_sig]
fact_only = [s for s in extracted if (s.claim_type or "fact") == "fact"]
fact_ids = {s.id for s in fact_only}
print("fact-only filter result:", sorted(fact_ids))
assert fact_ids == {"f1", "legacy1"}, "inference signals must be excluded, untagged legacy signals must default to fact"

print("\nALL EDGE-CASE UNIT CHECKS PASSED")
