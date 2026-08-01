from pathlib import Path

from local_assist.stocks import analyze_csv


def test_signal_contains_uncertainty():
    result = analyze_csv(Path("examples/vedanta.synthetic.csv"))
    assert 0 <= result.probability_up <= 1
    assert result.uncertainty_95[0] < result.uncertainty_95[1]
    assert result.observations == 25
