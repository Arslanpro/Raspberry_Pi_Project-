from wake_up_bright.alarm_clock.display import transfer


def test_transfer():
    minn = 0
    maxn = 3

    assert transfer(-1, minn, maxn) == 3
    assert transfer(0, minn, maxn) == 0
    assert transfer(1, minn, maxn) == 1
    assert transfer(2, minn, maxn) == 2
    assert transfer(3, minn, maxn) == 3
    assert transfer(4, minn, maxn) == 0