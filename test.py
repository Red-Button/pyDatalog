"""
pyDatalog

Copyright (C) 2012 Pierre Carbonnelle

This library is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc.  51 Franklin St, Fifth Floor, Boston, MA 02110-1301
USA

"""
import pyDatalog
import time

if __name__ == "__main__":

    # instantiate a pyDatalog engine
    datalog_engine = pyDatalog.Datalog_engine()
    
    print("Defining a datalog program...")
    
    # test of expressions
    datalog_engine.execute('+ p(a)')
    assert datalog_engine.ask('p(a)') == set([('a',)])
    
    # a decorator is used to create a program on the pyDatalog engine
    @pyDatalog.program(datalog_engine)
    def _(): # the function name is ignored
        # assert a unary fact
        + p(a) 
        # check that unary queries work
        assert ask(p(a)) == set([('a',)])
        assert ask(p(X)) == set([('a',)])
        assert ask(p(Y)) == set([('a',)])
        assert ask(p(b)) == None
        
        + p(b)
        assert ask(p(X)) == set([('a',), ('b',)])
        
        + p(b) # facts are unique
        assert ask(p(X)) == set([('a',), ('b',)])
        
        - p(b) # retract a unary fact
        assert ask(p(X)) == set([('a',)])
        
        # strings and integers
        + p('c')
        assert ask(p(c)) == set([('c',)])
        
        + p(1)
        assert ask(p(1)) == set([('1',)])

        # idem for secondary facts
        + q(a, b)
        assert ask(q(a, b)) == set([('a', 'b')])
        assert ask(q(X, b)) == set([('a', 'b')])
        assert ask(q(a, Y)) == set([('a', 'b')])
        assert ask(q(a, c)) == None
        assert ask(q(X, Y)) == set([('a', 'b')])
        
        + q(a,c)
        assert ask(q(a, Y)) == set([('a', 'b'), ('a', 'c')])
        
        - q(a,c)
        assert ask(q(a, Y)) == set([('a', 'b')])
        
        # clauses
        r(X, Y) <= p(X) & p(Y)
        assert ask(r(a, a)) == set([('a', 'a')])
        assert ask(r(a, c)) == set([('a', 'c')])
        # TODO more

        # integer
        + integer(1)
        print ask(integer(1))
        assert ask(integer(1)) == set([('1',)])
        
        # integer variable
        for _i in range(10):
            + successor(_i+1, _i)
        assert ask(successor(2, 1)) == set([('2', '1')])
        
        # recursion
        # even(N) <= (N==0)
        + even(0)
        even(N) <= successor(N, N1) & odd(N1)
        odd(N) <= successor(N, N1) & even(N1)
        assert ask(even(0)) == set([('0',)])
        assert ask(even(X)) == set([('4',), ('10',), ('6',), ('0',), ('2',), ('8',)])
        assert ask(odd(1)) == set([('1',)])
        assert ask(odd(5)) == set([('5',)])
        assert ask(even(5)) == None

        # equality (must be between parenthesis):
        s(X) <= (X == a)
        assert ask(s(X)) == set([('a',)])
        s(X) <= (X == 1)
        print(ask(s(X)))
        assert ask(s(X)) == set([('1',), ('a',)])
        
        s(X, Y) <= p(X) & (X == Y)
        assert ask(s(a, a)) == set([('a', 'a')])
        assert ask(s(a, b)) == None
        assert ask(s(X,a)) == set([('a', 'a')])
        print(ask(s(X, Y)))
        assert ask(s(X, Y)) == set([('a', 'a'),('c', 'c'),('1', '1')])
        # TODO  make this work
        # s <= (X == Y)   
        # assert ask(s(X,Y)) == set([('a', 'a'),('c', 'c'),('1', '1')])

    # reset the engine
    datalog_engine = pyDatalog.Datalog_engine()
    @pyDatalog.program(datalog_engine)
    def _(): # the function name is ignored
        # expressions
        predecessor(X,Y) <= (X==Y-1)
        assert ask(predecessor(X,11)) == set([('10', '11')])
        
        p(X,Z) <= (Y==Z-1) & (X==Y-1)
        assert ask(p(X,11)) == set([('9', '11')])
        
        # recursion
        + even('0')
        even(N) <= (N > 0) & (N1==N-1) & odd(N1)
        assert ask(even(0)) == set([('0',)])
        odd(N) <= (N > 0) & (N2==N-1) & even(N2)
        assert ask(even(0)) == set([('0',)])
        assert ask(odd(1)) == set([('1',)])
        assert ask(odd(5)) == set([('5',)])
        assert ask(even(5)) == None
        
    # a program can be entered piecemeal
    @pyDatalog.program(datalog_engine)
    def _(): # the function name is ignored
        # performance
        for _i in range(2000):
            + successor(_i+1, _i)
        assert ask(successor(1801,1800)) == set([('1801', '1800')])
        #assert ask(successor(99001,99000)) == set([('99001', '99000')])
        assert ask(odd(299)) == set([('299',)]) 
        #assert ask(odd(999)) == set([('999',)]) 
        assert ask(odd(1099)) == set([('1099',)]) # TODO stack overflow around 1100 !
        
        # TODO why is this much much slower ??
        # odd(N) <= even(N1) & successor(N, N1)

    # populate facts from python variables
    _farmers = ('Moshe dayan', 'omar')
    @pyDatalog.program(datalog_engine)
    def _(): # the function name is ignored
        # unary plus defines a fact
        for _farmer in _farmers:
            + farmer(_farmer)
        assert ask(farmer(X)) == set([('Moshe dayan',), ('omar',)])

    # execute queries in a python program
    moshe_is_a_farmer = datalog_engine.ask("farmer('Moshe dayan')")
    assert moshe_is_a_farmer == set([('Moshe dayan',)])

    # can't call a pyDatalog program
    error = False
    try:
        _()
    except: error = True
    assert error

    @pyDatalog.program(datalog_engine)
    def _():
        # literal cannot have a literal as argument
        _error = False
        try:
            + farmer(farmer(moshe))
        except: _error = True
        assert _error

    @pyDatalog.program(datalog_engine)
    def _(): # the function name is ignored
        + parent(bill,mary)
        + parent(mary,john) 
    print datalog_engine.ask('parent(X,john)')
    @pyDatalog.program(datalog_engine)
    def _(): # the function name is ignored
        ancestor(X,Y) <=  parent(X,Y)
        ancestor(X,Y) <= parent(X,Z) & ancestor(Z,Y)
    print datalog_engine.ask('ancestor(bill,X)')
    
    _parents = (('edward', 'albert'), ('edward', 'victoria'))
    
    @pyDatalog.program(datalog_engine)
    def _(): # the function name is ignored
        for _parent in _parents:
            + parent(_parent[0], _parent[1])       
    
    print("Done.")
