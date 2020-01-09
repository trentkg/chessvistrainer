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

def test_generate_knight_neighbors():
    a1_neighbors = [ct.get_chess_notation(x,y) for x,y in ct.generate_knight_neighbors(1,1)]
    a1_neighbors.sort()
    expected = ['b:3', 'c:2']
    assert a1_neighbors == expected

    e4_neighbors = [ct.get_chess_notation(x,y) for x,y in ct.generate_knight_neighbors(5,4)]
    e4_neighbors.sort()
    expected = ['d:6','c:5', 'f:6','g:5', 'd:2', 'c:3', 'f:2', 'g:3']
    expected.sort()
    assert e4_neighbors == expected

def test_find_shortest_path_for_knight():
    node = ct.find_shortest_path_for_knight("a:1", "b:3")
    assert node.distance == 1
    assert node.route == ['a:1', 'b:3']
    assert node.name == 'b:3'
