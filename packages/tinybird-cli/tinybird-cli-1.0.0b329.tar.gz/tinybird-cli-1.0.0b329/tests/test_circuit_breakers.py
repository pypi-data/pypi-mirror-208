import unittest

from tinybird.hfi.circuit_breakers import INITIAL_WAIT, MAX_CONSECUTIVE_ERRORS, MAX_WAIT, CircuitBreakers, CircuitBreakersException


class TestCircuitBreakers(unittest.TestCase):
    def test_circuit_breaker_simple(self):
        cb = CircuitBreakers()
        for i in range(MAX_CONSECUTIVE_ERRORS + 1):
            cb.check('test', 0.1 * i)
            cb.failed('test', 'fake_error')
        error_time = 0.1 * MAX_CONSECUTIVE_ERRORS
        self.assertRaises(CircuitBreakersException, lambda: cb.check('test', error_time))
        self.assertRaises(CircuitBreakersException, lambda: cb.check('test', error_time + INITIAL_WAIT - 0.001))
        # Should pass after INITIAL_WAIT
        cb.check('test', error_time + INITIAL_WAIT + 0.001)
        # should fail: second check during half open period
        self.assertRaises(CircuitBreakersException, lambda: cb.check('test', error_time + INITIAL_WAIT + 0.002))

        cb.check('test', error_time + 2)  # should pass after wait
        cb.failed('test', 'fake_error')
        self.assertRaises(CircuitBreakersException, lambda: cb.check('test', error_time + 2.2))

        cb.succeeded('test')
        for _ in range(MAX_CONSECUTIVE_ERRORS + 1):
            cb.failed('test', 'fake_error')
        # should pass, there were errors, but not MAX_CONSECUTIVE_ERRORS since last success
        cb.check('test', error_time + 2.3)

    def test_circuit_breaker_max_wait(self):
        cb = CircuitBreakers()
        last_pass = 0
        passes = 0
        for i in range(200):
            try:
                cb.check('test', i)
            except Exception:
                continue
            last_pass = i
            passes += 1
            cb.failed('test', 'fake_error')
        assert passes == 15
        self.assertRaises(CircuitBreakersException, lambda: cb.check('test', last_pass + MAX_WAIT - 1))
        cb.check('test', 200 + last_pass + 0.001)
