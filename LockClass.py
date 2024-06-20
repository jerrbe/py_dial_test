import logging
import random

logging.VERBOSE = 5
logging.addLevelName(logging.VERBOSE, "VERBOSE")


class LockClass:
    def __init__(self) -> None:
        '''Initialize the lock with random values'''
        self.logger = logging.getLogger(__name__)
        # The interal dial values range from 0 to 999 to represent 1/10th
        # increments on the 0 to 99 dial.
        self._A = random.randint(0, 999)
        self._B = random.randint(0, 999)
        self._C = random.randint(0, 999)
        self._D = random.randint(0, 999)
        # The following values keep track of whether the dial is on the left
        # or right hand side when two adjacent dials share a number
        self._AB = bool(random.randint(0, 1))
        self._BC = bool(random.randint(0, 1))
        self._CD = bool(random.randint(0, 1))
        self.logger.debug(f"Initial Lock Settings:  {self.A:2.1f}, "
                          f"{self.B:2.1f}, {self.C:2.1f}, {self.D:2.1f}")

    @property
    def A(self):
        '''Return the present position of the A dial'''
        return self._A/10

    @A.setter
    def A(self, value):
        self._A = round(value * 10)

    @property
    def B(self):
        '''Return the present position of the B dial'''
        return self._B/10

    @B.setter
    def B(self, value):
        self._B = round(value * 10)

    @property
    def C(self):
        '''Return the present position of the C dial'''
        return self._C/10

    @C.setter
    def C(self, value):
        self._C = round(value * 10)

    @property
    def D(self):
        '''Return the present position of the D dial'''
        return self._D/10

    @D.setter
    def D(self, value):
        self._D = round(value * 10)

    def __cmp(self, val1: int, val2: int):
        '''Compare two clamped values'''
        return (abs(int(val1) % 1000) == abs(int(val2) % 1000))

    def __add(self, val, clamp=False):
        '''Add 1 to the input and return.
        Clamp between 0 and 1000 when clamp=True'''
        val = int(val)
        val = val + 1
        if clamp:
            val = val % 1000
        return val

    def __sub(self, val, clamp=False):
        '''Subtract 1 from the input and return.
        Clamp between 0 and 1000 when clamp=True'''
        val = int(val)
        val = val - 1
        if clamp:
            val = val % 1000
        return val

    def step_ccw(self, clamp=False):
        '''Increment by 1/10th of a dial position counter-clockwise'''
        if self.__cmp(self._D, self._C) and self._CD:
            if self.__cmp(self._C, self._B) and self._BC:
                if self.__cmp(self._B, self._A) and self._AB:
                    self._A = self.__add(self._A, clamp)
                self._B = self.__add(self._B, clamp)
                if self.__cmp(self._B, self._A):
                    self._AB = True
            self._C = self.__add(self._C, clamp)
            if self.__cmp(self._C, self._B):
                self._BC = True
        self._D = self.__add(self._D, clamp)
        if self.__cmp(self._D, self._C):
            self._CD = True
        if self._D % 10 == 0:
            self.logger.log(logging.VERBOSE,
                            f"        step_ccw:   {abs(self._A % 1000):3}, "
                            f"{abs(self._B%1000):3}, {abs(self._C%1000):3}, "
                            f"{abs(self._D%1000):3} -- {self._A}, {self._B}, "
                            f"{self._C}, {self._D}")

    def step_cw(self, clamp=False):
        '''Increment by 1/10th of a dial position clockwise'''
        if self.__cmp(self._D, self._C) and not self._CD:
            if self.__cmp(self._C, self._B) and not self._BC:
                if self.__cmp(self._B, self._A) and not self._AB:
                    self._A = self.__sub(self._A, clamp)
                self._B = self.__sub(self._B, clamp)
                if self.__cmp(self._B, self._A):
                    self._AB = False
            self._C = self.__sub(self._C, clamp)
            if self.__cmp(self._C, self._B):
                self._BC = False
        self._D = self.__sub(self._D, clamp)
        if self.__cmp(self._D, self._C):
            self._CD = False
        if self._D % 10 == 0:
            self.logger.log(logging.VERBOSE,
                            f"        step_cw:   {abs(self._A % 1000):3}, "
                            f"{abs(self._B%1000):3}, {abs(self._C%1000):3}, "
                            f"{abs(self._D%1000):3} -- {self._A}, {self._B}, "
                            f"{self._C}, {self._D}")

    def move(self, dest):
        dest = round(dest*10)
        self.logger.debug(f"      Move to {dest}, starting at {self._A}, "
                          f"{self._B}, {self._C}")
        while self._D < dest:
            self.step_ccw()
        while self._D > dest:
            self.step_cw()
        # We didn't clamp during the stepping, but we want to clamp now
        # that we reached the target
        self._A = abs(self._A % 1000)
        self._B = abs(self._B % 1000)
        self._C = abs(self._C % 1000)
        self._D = abs(self._D % 1000)
