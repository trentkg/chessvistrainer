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
