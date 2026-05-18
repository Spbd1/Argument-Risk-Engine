from argument_risk_engine.evaluation.runner import run_evaluation


def test_evaluation_runner(tmp_path):
    path = tmp_path / "eval.jsonl"
    path.write_text('{"text":"They are vermin."}\n')
    assert run_evaluation(path)["items"] == 1
