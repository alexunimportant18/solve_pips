import pytest

from board import find_combinations


def test_find_combinations_basic():
    """
    Tests a basic case with n=2 and t=5.
    The expected combinations are [0, 5], [1, 4], [2, 3].
    """
    assert find_combinations(n=2, t=5) == [[0, 5], [1, 4], [2, 3]]


def test_find_combinations_no_solution():
    """
    Tests a case where no combination is possible.
    n=2, t=13. The maximum sum for n=2 is 12 (6+6), so no solution should be found.
    """
    assert find_combinations(n=2, t=13) == []


def test_find_combinations_n_is_1():
    """
    Tests the case where n=1.
    The combination should be just the target sum t.
    """
    assert find_combinations(n=1, t=4) == [[4]]


def test_find_combinations_t_is_0():
    """
    Tests the case where t=0.
    The only combination is a list of n zeros.
    """
    assert find_combinations(n=3, t=0) == [[0, 0, 0]]


def test_find_combinations_large_n_and_t():
    """
    Tests a more complex case with larger n and t.
    """
    # This is just one of many possible combinations.
    # The goal is to ensure the function can handle larger inputs.
    result = find_combinations(n=4, t=10)
    assert [0, 0, 4, 6] in result
    assert [0, 1, 3, 6] in result
    assert [0, 1, 4, 5] in result
    assert [0, 2, 2, 6] in result
    assert [0, 2, 3, 5] in result
    assert [0, 2, 4, 4] in result
    assert [0, 3, 3, 4] in result
    assert [1, 1, 2, 6] in result
    assert [1, 1, 3, 5] in result
    assert [1, 1, 4, 4] in result
    assert [1, 2, 2, 5] in result
    assert [1, 2, 3, 4] in result
    assert [1, 3, 3, 3] in result
    assert [2, 2, 2, 4] in result
    assert [2, 2, 3, 3] in result


def test_find_combinations_impossible_sum_high():
    """
    Tests that no combinations are returned when the target sum is too high.
    """
    assert find_combinations(n=3, t=19) == []


def test_find_combinations_impossible_sum_low():
    """
    Tests that no combinations are returned when the target sum is too low,
    although the recursive function's structure naturally prevents this
    by starting loops at 0. This test is for completeness.
    """
    # With n > 0, the minimum possible sum is 0. A negative target is impossible.
    # The initial check in find_combinations handles t < n * 0, but t can't be negative.
    # This scenario is more about logical impossibility within the problem's constraints
    # rather than a direct input that would be negative.
    # The function is designed for t >= 0.
    # A test for t < 0 isn't directly applicable unless the function's contract changes.
    # However, the initial check `if n * 6 < t or n * 0 > t:` handles this.
    # For example, if t was -1, n*0 > t would be 0 > -1, which is true, returning [].
    # Let's test this implicit behavior.
    assert find_combinations(n=3, t=-1) == []
