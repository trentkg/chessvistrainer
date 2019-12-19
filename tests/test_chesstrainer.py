import chesstrainer as ct

def test_get_brother_square():
    a1_answer = ct.get_brother_square('a:1')
    assert a1_answer =='h:8'
    h8_answer = ct.get_brother_square('h:8')
    assert h8_answer =='a:1'
    e4_answer = ct.get_brother_square('e:4')
    assert e4_answer =='d:5'
    d5_answer = ct.get_brother_square('d:5')
    assert d5_answer =='e:4'
    b6_answer = ct.get_brother_square('b:6')
    assert b6_answer =='g:3'
    g3_answer = ct.get_brother_square('g:3')
    assert g3_answer =='b:6'


def test_get_diagonal_squares():
    a1_answer = ct.get_diagonal_squares('a:1')
    expected =sorted(['b:2', 'c:3', 'd:4', 'e:5', 'f:6', 'g:7','h:8'])
    assert a1_answer == expected 

    h8_answer = ct.get_diagonal_squares('h:8')
    assert h8_answer == sorted(['a:1', 'b:2', 'c:3', 'd:4', 'e:5', 'f:6', 'g:7'])
    
    e4_answer = ct.get_diagonal_squares('e:4')
    assert e4_answer == sorted(['b:1', 'c:2', 'd:3', 'b:7','a:8', 'c:6', 'd:5',
        'f:5', 'g:6', 'h:7', 'f:3', 'g:2', 'h:1'])
