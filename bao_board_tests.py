import unittest
from bao_board import *



def make_state(number=0):
    test_player_pits = \
    [
        [
            ['b{}'.format(i) for i in range(8, 0, -1)],
            ['a{}'.format(i) for i in range(8, 0, -1)]
        ][::-1],
        [
            ['A{}'.format(i) for i in range(1, 9)],
            ['B{}'.format(i) for i in range(1, 9)]
        ],
    ][::-1]
        
    empty_state = {"1": 22, "2": 22, "N1": True, "N2": True}
    for side in test_player_pits:
        for row in side:
            for pit in row:
                empty_state[pit] = number

    return empty_state


class TaxTests(unittest.TestCase):

    # if there is a functional house and it is the only occupied pit left in the front row,
    # then the player can tax it, which means to takasa it as if it was a singleton. This
    # does not destroy the house. The conditions for this move aren't being tested
    # here (that is tested in the Namu Takasa move check tests), just that the action
    # works as expected. There are only different tax moves possible, either taxing left
    # or right for both players.
    def test_tax(self):
        test_state = make_state()
        test_state["A5"] = 6
        test_state["a5"] = 6
        a = Board(test_state.copy())

        answer_1 = test_state.copy()
        answer_1["A5"] -= 1
        answer_1["1"] -= 1
        answer_2 = answer_1.copy()
        answer_1["A6"] += 1
        answer_1["A7"] += 1
        answer_2["A4"] += 1
        answer_2["A3"] += 1
        answer_3 = test_state.copy()
        answer_3["a5"] -= 1
        answer_3["2"] -= 1
        answer_4 = answer_3.copy()
        answer_3["a6"] += 1
        answer_3["a7"] += 1
        answer_4["a4"] += 1
        answer_4["a3"] += 1

        answer_1 = (0, answer_1)
        answer_2 = (0, answer_2)
        answer_3 = (0, answer_3)
        answer_4 = (0, answer_4)

        self.assertEqual(a.tax("A5R", 0), answer_1)
        self.assertEqual(a.tax("A5L", 0), answer_2)
        self.assertEqual(a.tax("a5R", 1), answer_3)
        self.assertEqual(a.tax("a5L", 1), answer_4)


class NamuTakasaMoveCheckTests(unittest.TestCase):

    # test the default state
    def test_default(self):
        a = Board()
        self.assertEqual(a.get_available_moves(0), (2, [("A6", ["R", "L"]), ("A7", ["R", "L"])]))
        self.assertEqual(a.get_available_moves(1), (2, [("a7", ["R", "L"]), ("a6", ["R", "L"])]))

    # test special rule around the kichwa:
    # The kichwa can't be emptied towards the back row if that causes the front row to be
    # temporarily empty
    def test_kichwa(self):
        # Multibatch test - multiple asserts for a single batch testing
        # variants on a single situation. Each batch is given a note and
        # not each individual assert.
        a = Board(make_state())
        b = Board(make_state())
        c = Board(make_state())
        d = Board(make_state())
        e = Board(make_state())
        f = Board(make_state())
        g = Board(make_state())
        h = Board(make_state())
        i = Board(make_state())
        j = Board(make_state())
        k = Board(make_state())
        l = Board(make_state())
        m = Board(make_state())
        n = Board(make_state())
        o = Board(make_state())
        p = Board(make_state())
        q = Board(make_state())
        r = Board(make_state())
        s = Board(make_state())
        t = Board(make_state())


        # both kichwas and an extra pit have seeds
        # expected results - both kichwas and the 
        # extra pit can be played in both directions
        a.state["A1"] = 6
        a.state["A2"] = 6
        a.state["A8"] = 6
        b.state["a1"] = 6
        b.state["a2"] = 6
        b.state["a8"] = 6

        # one kichwa and an extra pit have seeds
        # expected results - the kichwa and the 
        # extra pit can be played in both directions
        c.state["A1"] = 6
        c.state["A2"] = 6
        d.state["a1"] = 6
        d.state["a2"] = 6
        e.state["A2"] = 6
        e.state["A8"] = 6
        f.state["a2"] = 6
        f.state["a8"] = 6
        
        # both kichwas have seeds
        # expected result - both kichwas
        # can be played in both directions
        g.state["A1"] = 6
        g.state["A8"] = 6
        h.state["a1"] = 6
        h.state["a8"] = 6

        # A single kichwa has a single seed and no
        # other pits have any seeds
        # expected result - can only be played
        # towards the inner row
        # Note: This is to test how the kichwa
        # plays with the singleton rule. Despite
        # the house no longer being in play,
        # since only singletons are in play
        # they can be takasa'ed. See desciption
        # for the singleton tests and nyumba tests
        # for more details on the related rules being
        # tested here
        i.state["A1"] = 1
        j.state["A8"] = 1
        k.state["a1"] = 1
        l.state["a8"] = 1

        # A single kichwa has two seeds and no
        # other pits have any seeds
        # expected result - can only be played
        # towards the inner row
        # Note: this tests the case where the
        # singleton rule doesn't apply.
        # See previous test note for details 
        m.state["A1"] = 2
        n.state["A8"] = 2
        o.state["a1"] = 2
        p.state["a8"] = 2

        # A single kichwa has enough seeds to
        # circle back around to the front row
        # and no other pits have any seeds
        # expected result - can only be played
        # towards the inner row
        # Note: Not even the front row being
        # temporarily empty at any point is allowed.
        # Hence this test
        q.state["A1"] = 10
        r.state["A8"] = 10
        s.state["a1"] = 10
        t.state["a8"] = 10


        # First batch
        self.assertEqual(a.get_available_moves(0), (2, [("A1", ["R", "L"]), ("A2", ["R", "L"]), ("A8", ["R", "L"])]))
        self.assertEqual(b.get_available_moves(1), (2, [("a8", ["R", "L"]), ("a2", ["R", "L"]), ("a1", ["R", "L"])]))

        # Second batch
        self.assertEqual(c.get_available_moves(0), (2, [("A1", ["R", "L"]), ("A2", ["R", "L"])]))
        self.assertEqual(d.get_available_moves(1), (2, [("a2", ["R", "L"]), ("a1", ["R", "L"])]))
        self.assertEqual(e.get_available_moves(0), (2, [("A2", ["R", "L"]), ("A8", ["R", "L"])]))
        self.assertEqual(f.get_available_moves(1), (2, [("a8", ["R", "L"]), ("a2", ["R", "L"])]))

        # Third batch
        self.assertEqual(g.get_available_moves(0), (2, [("A1", ["R", "L"]), ("A8", ["R", "L"])]))
        self.assertEqual(h.get_available_moves(1), (2, [("a8", ["R", "L"]), ("a1", ["R", "L"])]))

        # Fourth batch
        self.assertEqual(i.get_available_moves(0), (2, [("A1", ["R"])]))
        self.assertEqual(j.get_available_moves(0), (2, [("A8", ["L"])]))
        self.assertEqual(k.get_available_moves(1), (2, [("a1", ["R"])]))
        self.assertEqual(l.get_available_moves(1), (2, [("a8", ["L"])]))

        # Fifth batch
        self.assertEqual(m.get_available_moves(0), (2, [("A1", ["R"])]))
        self.assertEqual(n.get_available_moves(0), (2, [("A8", ["L"])]))
        self.assertEqual(o.get_available_moves(1), (2, [("a1", ["R"])]))
        self.assertEqual(p.get_available_moves(1), (2, [("a8", ["L"])]))

        # Sixth batch
        self.assertEqual(q.get_available_moves(0), (2, [("A1", ["R"])]))
        self.assertEqual(r.get_available_moves(0), (2, [("A8", ["L"])]))
        self.assertEqual(s.get_available_moves(1), (2, [("a1", ["R"])]))
        self.assertEqual(t.get_available_moves(1), (2, [("a8", ["L"])]))

    def test_nyumba(self):
        a = Board(make_state())
        b = Board()
        c = Board()
        d = Board(make_state())
        e = Board()
        f = Board()


        # A functional nyumba, with all other pits empty
        # expected outcome - taxing the nyumba
        a.state["A5"] = 6
        a.state["a5"] = 6

        # A functional nyumba, with pit six having 2 seeds
        # expected outcome - can't takasa the nyumba, have
        # to takasa the sixth pit
        b.state = a.state.copy()
        b.state["A6"] = 2
        b.state["a6"] = 2

        # A functional nyumba, alongside a singleton pit
        # expected outcome - can't takasa the nyumba, have
        # takasa the singleton. A functional nyumba overrides
        # the takasa singleton rule, where you are not allowed to
        # takasa a singleton - see the singleton tests
        c.state = b.state.copy()
        c.state["A6"] = 1
        c.state["a6"] = 1

        # A dysfunctional nyumba, all other pits being empty
        # expected outcome - you have to takasa the nyumba
        d.state["A5"] = 5
        d.state["a5"] = 5

        # A dysfunctional nyumba, with pit six having two seeds
        # expected outcome - you can takasa both
        e.state = d.state.copy()
        e.state["A6"] = 2
        e.state["a6"] = 2

        # A dysfunctional nyumba, alongside a singleton pit
        # expected outcome - you can only takasa the nyumba
        f.state = e.state.copy()
        f.state["A6"] = 1
        f.state["a6"] = 1


        self.assertEqual(a.get_available_moves(0), (0, [("A5", ["R", "L"])]))
        self.assertEqual(a.get_available_moves(1), (0, [("a5", ["R", "L"])]))
        self.assertEqual(b.get_available_moves(0), (2, [("A6", ["R", "L"])]))
        self.assertEqual(b.get_available_moves(1), (2, [("a6", ["R", "L"])]))
        self.assertEqual(c.get_available_moves(0), (2, [("A6", ["R", "L"])]))
        self.assertEqual(c.get_available_moves(1), (2, [("a6", ["R", "L"])]))
        self.assertEqual(d.get_available_moves(0), (2, [("A5", ["R", "L"])]))
        self.assertEqual(d.get_available_moves(1), (2, [("a5", ["R", "L"])]))
        self.assertEqual(e.get_available_moves(0), (2, [("A5", ["R", "L"]), ("A6", ["R", "L"])]))
        self.assertEqual(e.get_available_moves(1), (2, [("a6", ["R", "L"]), ("a5", ["R", "L"])]))
        self.assertEqual(f.get_available_moves(0), (2, [("A5", ["R", "L"])]))
        self.assertEqual(f.get_available_moves(1), (2, [("a5", ["R", "L"])]))


        # Repeating all experiments, except the Nyumba is destroyed. Therefore it is just
        # a regular pit. This makes the expected outcome of each now:
        a.state["N1"] = False # Takasa the 5th pit
        a.state["N2"] = False 
        b.state["N1"] = False # Takasa either the 5th or 6th pit
        b.state["N2"] = False
        c.state["N1"] = False # Takasa the 5th pit
        c.state["N2"] = False
        d.state["N1"] = False # Takasa the 5th pit
        d.state["N2"] = False
        e.state["N1"] = False # Takasa either the 5th or 6th pit 
        e.state["N2"] = False
        f.state["N1"] = False # Takasa the 5th pit
        f.state["N2"] = False


        self.assertEqual(a.get_available_moves(0), (2, [("A5", ["R", "L"])]))
        self.assertEqual(a.get_available_moves(1), (2, [("a5", ["R", "L"])]))
        self.assertEqual(b.get_available_moves(0), (2, [("A5", ["R", "L"]), ("A6", ["R", "L"])]))
        self.assertEqual(b.get_available_moves(1), (2, [("a6", ["R", "L"]), ("a5", ["R", "L"])]))
        self.assertEqual(c.get_available_moves(0), (2, [("A5", ["R", "L"])]))
        self.assertEqual(c.get_available_moves(1), (2, [("a5", ["R", "L"])]))
        self.assertEqual(d.get_available_moves(0), (2, [("A5", ["R", "L"])]))
        self.assertEqual(d.get_available_moves(1), (2, [("a5", ["R", "L"])]))
        self.assertEqual(e.get_available_moves(0), (2, [("A5", ["R", "L"]), ("A6", ["R", "L"])]))
        self.assertEqual(e.get_available_moves(1), (2, [("a6", ["R", "L"]), ("a5", ["R", "L"])]))
        self.assertEqual(f.get_available_moves(0), (2, [("A5", ["R", "L"])]))
        self.assertEqual(f.get_available_moves(1), (2, [("a5", ["R", "L"])]))

    def test_singletons(self):
        a = Board()
        b = Board()
        c = Board()
        d = Board()
        e = Board()


        # Variation on default, but
        # the seventh pit is a singleton
        # instead of having two seeds
        # expected outcome - pits
        # six and seven can be takasa'ed
        # the singleton pit can be takasa'ed
        a.state["A7"] = 1
        a.state["a7"] = 1

        # Alteration on earlier test,
        # but with the nyumba disabled
        # expected outcome - pits
        # five and six can be takasa'ed,
        # but not the singleton
        b.state = a.state.copy()
        b.state["N1"] = False
        b.state["N2"] = False

        # Further alteration, now
        # the ex-house pit is empty
        # expected outcome - only
        # six can be takasa'ed,
        # not the singleton
        c.state = b.state.copy()
        c.state["A5"] = 0
        c.state["a5"] = 0

        # Further alteration, now
        # pit 6 is also a singleton,
        # leaving only singletons
        # left in the front row
        # expected outcome - both
        # singletons can be takasa'ed
        d.state = c.state.copy()
        d.state["A6"] = 1
        d.state["a6"] = 1

        # Last alteration. The sixth
        # pit is emptied, leaving only
        # one singleton
        # expected outcome - the
        # singleton can be takasa'ed
        e.state = d.state.copy()
        e.state["A6"] = 0
        e.state["a6"] = 0


        self.assertEqual(a.get_available_moves(0), (2, [("A6", ["R", "L"]), ("A7", ["R", "L"])]))
        self.assertEqual(a.get_available_moves(1), (2, [("a7", ["R", "L"]), ("a6", ["R", "L"])]))
        self.assertEqual(b.get_available_moves(0), (2, [("A5", ["R", "L"]), ("A6", ["R", "L"])]))
        self.assertEqual(b.get_available_moves(1), (2, [("a6", ["R", "L"]), ("a5", ["R", "L"])]))
        self.assertEqual(c.get_available_moves(0), (2, [("A6", ["R", "L"])]))
        self.assertEqual(c.get_available_moves(1), (2, [("a6", ["R", "L"])]))
        self.assertEqual(d.get_available_moves(0), (2, [("A6", ["R", "L"]), ("A7", ["R", "L"])]))
        self.assertEqual(d.get_available_moves(1), (2, [("a7", ["R", "L"]), ("a6", ["R", "L"])]))
        self.assertEqual(e.get_available_moves(0), (2, [("A7", ["R", "L"])]))
        self.assertEqual(e.get_available_moves(1), (2, [("a7", ["R", "L"])]))


class NamuCaptureMoveCheckTests(unittest.TestCase):

    def test_kimbi(self):
        a = Board(make_state(10))
        expected_outcome_p1 = (1, [
            ("A1", ["R"]), ("A2", ["R"]), ("A3", ["R", "L"]), ("A4", ["R", "L"]),
            ("A5", ["R", "L"]), ("A6", ["R", "L"]), ("A7", ["L"]), ("A8", ["L"])
        ])

        expected_outcome_p2 = (1, [
            ("a8", ["L"]), ("a7", ["L"]), ("a6", ["R", "L"]), ("a5", ["R", "L"]),
            ("a4", ["R", "L"]), ("a3", ["R", "L"]), ("a2", ["R"]), ("a1", ["R"])
        ])

        self.assertEqual(a.get_available_moves(0), expected_outcome_p1)
        self.assertEqual(a.get_available_moves(1), expected_outcome_p2)
    
    def test_available_options(self):
        a = Board()
        self.assertEqual(a.get_available_moves(0), (2, [("A6", ["R", "L"]), ("A7", ["R", "L"])]))
        self.assertEqual(a.get_available_moves(1), (2, [("a7", ["R", "L"]), ("a6", ["R", "L"])]))

        a.state["A4"] = 1
        self.assertEqual(a.get_available_moves(0), (1, [("A4", ["R", "L"])]))
        self.assertEqual(a.get_available_moves(1), (1, [("a5", ["R", "L"])]))

        a.state["A4"] = 0
        a.state["a4"] = 1
        self.assertEqual(a.get_available_moves(0), (1, [("A5", ["R", "L"])]))
        self.assertEqual(a.get_available_moves(1), (1, [("a4", ["R", "L"])]))

        a.state["A4"] = 1
        self.assertEqual(a.get_available_moves(0), (1, [("A4", ["R", "L"]), ("A5", ["R", "L"])]))
        self.assertEqual(a.get_available_moves(1), (1, [("a5", ["R", "L"]), ("a4", ["R", "L"])]))



if __name__ == "__main__":
    unittest.main()
