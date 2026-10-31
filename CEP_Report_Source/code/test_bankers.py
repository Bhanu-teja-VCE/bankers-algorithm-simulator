#!/usr/bin/env python3
# Unit tests for bankers.py  -  run:  python3 test_bankers.py -v
import os, tempfile, unittest
from bankers import Banker, BankersError, load_state

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def textbook():
    return load_state(os.path.join(D, "textbook.txt"))


def tanenbaum(a, b, c):             # single resource type, 10 units, 3 customers
    return Banker(["U"], [10], ["A", "B", "C"], [[a], [b], [c]], [[9], [4], [7]])


class T(unittest.TestCase):
    def test01_textbook_safe(self):
        safe, seq, _, _ = textbook().safety()
        self.assertTrue(safe); self.assertEqual(seq, ["P1", "P3", "P4", "P0", "P2"])

    def test02_unsafe_state(self):
        safe, seq, _, _ = load_state(os.path.join(D, "unsafe.txt")).safety()
        self.assertFalse(safe); self.assertEqual(seq, [])

    def test03_request_granted(self):
        b = textbook(); st, _ = b.request("P1", [1, 0, 2])
        self.assertEqual(st, "GRANTED"); self.assertEqual(b.available, [2, 3, 0])

    def test04_request_waits(self):
        b = textbook(); b.request("P1", [1, 0, 2])
        self.assertEqual(b.request("P4", [3, 3, 0])[0], "WAIT")

    def test05_request_unsafe(self):
        b = textbook(); b.request("P1", [1, 0, 2])
        self.assertEqual(b.request("P0", [0, 2, 0])[0], "UNSAFE")

    def test06_exceeds_claim(self):
        b = textbook(); self.assertEqual(b.request("P1", [5, 0, 0])[0], "ERROR")

    def test07_unknown_process(self):
        self.assertEqual(textbook().request("P9", [0, 0, 0])[0], "ERROR")

    def test08_bad_vector(self):
        b = textbook()
        self.assertEqual(b.request("P0", [1, 2])[0], "ERROR")
        self.assertEqual(b.request("P0", [-1, 0, 0])[0], "ERROR")

    def test09_release(self):
        b = textbook(); freed = b.release("P3")
        self.assertEqual(freed, [2, 1, 1]); self.assertEqual(b.available, [5, 4, 3])

    def test10_granted_after_release(self):
        b = textbook(); b.request("P1", [1, 0, 2]); b.request("P1", [0, 2, 0]); b.release("P1")
        self.assertEqual(b.request("P0", [0, 2, 0])[0], "GRANTED")

    def test11_rollback_on_denial(self):
        b = textbook(); b.request("P1", [1, 0, 2])
        before = [r[:] for r in b.alloc]; b.request("P0", [0, 2, 0])
        self.assertEqual(b.alloc, before)

    def test12_max_exceeds_total(self):
        with self.assertRaises(BankersError):
            Banker(["A"], [5], ["P0"], [[0]], [[6]])

    def test13_alloc_exceeds_max(self):
        with self.assertRaises(BankersError):
            Banker(["A"], [5], ["P0"], [[3]], [[2]])

    def test14_overallocated(self):
        with self.assertRaises(BankersError):
            Banker(["A"], [5], ["P0", "P1"], [[3], [3]], [[4], [4]])

    def test15_malformed_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("RESOURCES A\nTOTAL 5\nP0 1 2 3\n")
        with self.assertRaises(BankersError):
            load_state(f.name)
        os.unlink(f.name)

    def test16_single_resource_safe(self):
        self.assertTrue(tanenbaum(3, 2, 2).safety()[0])

    def test17_single_resource_unsafe(self):
        self.assertFalse(tanenbaum(4, 2, 2).safety()[0])

    def test18_single_resource_request_denied(self):
        b = tanenbaum(3, 2, 2); self.assertEqual(b.request("A", [1])[0], "UNSAFE")

    def test19_zero_request(self):
        b = textbook(); self.assertEqual(b.request("P2", [0, 0, 0])[0], "GRANTED")

    def test20_finished_process_rejected(self):
        b = textbook(); b.release("P3"); self.assertEqual(b.request("P3", [0, 1, 1])[0], "ERROR")


if __name__ == "__main__":
    unittest.main()
