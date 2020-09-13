# Python Financial Model for IPO

This project was created to help us in our own decision-making for the
upcoming IPO/direct-listing/foo.  See the part in the license about us
making no rep or warrant?  Yeah, we mean that.

I recommend it be used to help guide your decision-making process;
please don't use this tool to file your taxes.

As with most models, it crunches the numbers, and then you can ask the
model a question, much as one might with a magic 8-ball.  `Will my tax
bill make me cry?`...`Try again later`.  Perhaps more appropriately,
you can ask specific numerical questions.  For example, you might be
interested in knowing what your tax bill would be if you sold all of
your RSUs at $30 per share, or how much cash you would clear after
having a heart-to-heart with the IRS.

# Quick Start (aka TL;DR)

If you're interested in moving as quickly as possible, and getting the
answers to some basic questions that we have pre-programmed for you,
then this section is for you.  I assume you're using \*nix.  If not,
go buy a mac or something.

1. Download and install [Anaconda](https://www.anaconda.com/) and get
an environment up and running with python 3.  There is plenty of
[Documentation](https://bfy.tw/P2s2) on that particular topic.

2. `pip install pylink-satcom`

3. `cp eg_private.py private.py`

4. Edit `private.py` to put in your grants, income, withholdings, etc.
The file itself has all the documentation you need to find that.  The
grants are tricky, but there are convenience functions to help you
port from Shareworks.

5. `python investigator.py`

6. Let Dixon Hill do the rest.

# Architecture and Modifications

If you want more than the few random questions we've included for your
convenience, then you'll want to modify things.  The system is written
using a libary calld `pylink`, which was originally written to manage
radio link budgets for low earth orbit spacecraft, but has been
bastardized to do everything from computing `Eb/N0` values for Voyager
1 to the Allen Telescope Array, to...well...this.  Start by reading
the documentation, and looking through the examples on the [pylink
Github page](https://github.com/harrison-caudill/pylink).

The computations are rather DAGgish in nature, which works quite
nicely with pylink.  Sale of stock is managed by processing a list of
sales orders that you get to define.  This process lets you sell
specific amounts of specific grants and specific prices.  That way,
you can model, for example, selling 25% of your RSUs on IPO day at
$15/share, and then seeing what kind of a jam you're in on taxes if
the price tanks to $5/share (or how insightful you feel if it
skyrockets to $90/share).

## Code Organization

 * `investigator.py`: This file is where the business-logic of asking
   the questions is housed.  It holds `main()` and imports everything
   it needs.  Everything else is a library.

 * `private.py`: All your private financial information, and entry in
   the `.gitignore` file so that nobody accidentally commits it.
   Anything specific to you is kept in there.  Think of it as your
   personal config file.  It doesn't contain logic, just constants.

 * `income.py`: This one processes sales orders.  It also houses a
   couple of convenience functions for generating lists of sales
   orders (currently just all or only the RSUs).

 * `position.py`: The equity position is tracked via the `Grant`
   object and convenience nodes for summation of various categories
   (such as `shares_vested_unsold_n` or
   `rem_shares_vested_unsold_rsu_n`).  The `Grant` object is one of
   the more complicated aspects as the vesting schedules can get
   interesting.  The `from_table` function exists to help you import
   data from SharePoint.

 * `report.py`: Convenience functions for printing summaries.  I'll
   add LaTeX report generation later if I get supremely bored
   (unlikely).  Always happy to review a pull request...just sayin'...

 * `taxes.py`: As expected...the tax model.  It makes a few
   simplifying assumptions (such as assuming you max out ss/sdi)

## Places to update

 * Change the values specific to you in `private.py`

 * Add convenience functions to implement the sales logic you want.
   Two such conveneince functions exist in `income.py`

 * Ask any questions of the model that you want to ask in
   `investigator.py`

# Obviously missing things

 * The system does not currently support itemized deductions.  If you
   itemize, take your itemized deduction total, and change the value
   of the standard deduction (in `private.py`) to match.  Wrong name,
   but the results should be about the same.

 * Apparently some grants transition mid-stream from monthly to
   quarterly.  This system does not support that concept.  If you
   *must* handle that case, create two `Grant` objects, one monthly
   and one quarterly.

 * Does not do anything with long-term capital gains
