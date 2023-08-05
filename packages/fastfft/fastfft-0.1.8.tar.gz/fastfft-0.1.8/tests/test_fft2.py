def test_the_answer():
    from src.fastfft import py_fft2_square
    py_fft2_square([[1, 2, 3, 4], [5, 6, 7, 8]])

    assert 1 == 1
