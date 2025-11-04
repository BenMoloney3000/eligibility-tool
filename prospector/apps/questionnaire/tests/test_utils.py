from prospector.apps.questionnaire import utils


def test_generate_id():
    generated_id = utils.generate_id()
    assert "0O" not in generated_id
    assert len(generated_id) == 10

    numbers = []
    letters = []
    for item in generated_id:
        if item in "ABCDEFGHIJKLMNPQRSTUVWXYZ":
            letters.append(item)
        elif item in "123456789":
            numbers.append(item)
    assert len(numbers) == 5
    assert len(letters) == 5


def test_is_valid_64_bit_integer():
    assert utils.is_valid_64_bit_integer(1000) == True
    assert utils.is_valid_64_bit_integer(utils.MAX_64_BIT_INT) == True
    assert utils.is_valid_64_bit_integer(utils.MIN_64_BIT_INT) == True
    assert utils.is_valid_64_bit_integer(utils.MAX_64_BIT_INT + 1) == False
    assert utils.is_valid_64_bit_integer(utils.MIN_64_BIT_INT - 1) == False
