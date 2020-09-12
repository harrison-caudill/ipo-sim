#!/usr/bin/env python

import math
import pylink

import income as myMeager
import position as anAwkward
import taxes as deathAnd


class Investigator(object):
""" Question we want to ask:

 1. What is the minimum/automatic number of withheld RSUs?

 2. What is the remaining RSU tax burden (in dollars)?

 3. How many RSUs must be sold on day 1 to cover the RSU tax burden?

 4. Percentage of RSUs that the answer to question 3 represents?

 5. If we sold everything we could, how much cash would we clear?

 6. If we sold all RSUs, and max number of NSOs, what percentage of
 full exercise price for all ISOs could be achieved without hitting
 AMT? (i.e. assume they're all priced the same)

 7. For a range of FMVs, graph 6
"""

    def __init__(self, model):
        self.m = model

    def go(self):
        
