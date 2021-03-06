# Python Financial Model for IPO

This project was created to help us in our own decision-making for the
upcoming IPO/direct-listing/foo.  See the part in the license about us
making no rep or warrant?  Yeah, we mean that.

If people would like additional features, you have three options:

1. Use the Source, Luke

2. File a ticket and maybe in my free time between working to
eliminate diabetic retinopathy, securing america's commercial space
infrastructure from Chinese/Russian/Korean/Martian cyber attack, and
raising a tiny infant, I'll get to it.

3. Ask someone else to use the source.

There are a number of convenience APIs available to make it easy to
customize your own questions, but this is NOT a WYSIWYG system and
will require some pythoning.  If you haven't the time, inclination,
and experience to customize it, then ride with the existing questions.

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
port from Shareworks. This is also where you can set different the
price of the stock to different values to see how the outputs change.

5. `python investigator.py`

6. Let Dixon Hill do the rest.


# Example Output

`investigator.py` comes already set up with a series of examples that
may be of some use to you.  Below is sample output from the
`eg_private.py` file.


## Tax Summaries

Several `Questions` will output a summary of tax information, in the
following format:

```
%T: Rate vs the taxable income
%A: Rate vs the ACTUAL (in your bank) income

=== State Taxes ===
Taxable Income:           715,463 $
Actual Income:            150,000 $
Reg Taxes:                 62,187 $   (  41.5%A   8.7%T )
SDI Taxes:                  1,229 $   (   0.8%A   0.2%T )
State Taxes:               63,416 $   (  42.3%A   8.9%T )
Cash Withheld:             15,000 $   (  10.0%A   2.1%T )
RSU Withheld:              58,320 $   (  38.9%A   8.2%T )
Outstanding:               -9,903 $   (  -6.6%A  -1.4%T )

=== Federal Taxes ===
Fed Taxable Income:       695,200 $
Actual Income:            150,000 $
Reg Taxes:                194,373 $   ( 129.6%A  28.0%T )
SS Taxes:                   8,537 $   (   5.7%A   1.2%T )
Medicare Taxes:            14,087 $   (   9.4%A   2.0%T )
AMT Taxable Income:       606,600 $
AMT Exemption:            113,400 $   (  75.6%A  18.7%T )
AMT Taxes:                165,890 $   ( 110.6%A  27.3%T )
Federal Taxes:            216,997 $   ( 144.7%A  31.2%T )
Cash Withheld:             20,000 $   (  13.3%A   2.9%T )
RSU Withheld:             138,804 $   (  92.5%A  20.0%T )
Outstanding:               58,193 $   (  38.8%A   8.4%T )

=== Overall ===
Actual Income:            150,000 $
State Taxes:               63,416 $   (  42.3%A   8.9%T )
Federal Taxes:            216,997 $   ( 144.7%A  31.2%T )
Total Taxes:              280,414 $   ( 186.9%A         )
Outstanding:               48,290 $   (  32.2%A         )
```

Note that two percentages are displayed: one for `Actual (A)` and one
for `Taxable (T)`.  Since the taxable income includes things like ISO
exercises (counting towards AMTI) or RSU vesting (which counts towards
both AMT and regular federal taxes).  The `Actual` income represents
cash that enters your bank account.  This way we get to show fun
things like tax rates of `186.9%` (because who doesn't like to pay
double their annual income in that year's taxes?).


## Cap Table

This shows basic tabular information about your stock positions.  The
only interesting bit is that it discusses `Withheld` shares, which
illustrates shares that are liquidated by the IRS/FTB.  The `Sold` shares are those that contribute to dollars in your bank account.

```
        ID       Type  Strike        Vested        Withheld            Sold       Remaining
      RSU-TK421  rsu    0.0          41,500          14,351          27,149               0
    BonusTigers  nso    2.0          10,000               0           9,750               0
    javax.swing  iso    4.0         114,583               0          42,200          72,383
```


## Question 1: How many RSUs will be automatically withheld?
```
These numbers are for shares vesting throughout the
year, since those will affect taxes as well.  Shares
available on the big day will NOT be affected by RSU
withholdings that will happen afterwards.

Withholding:   14,351 / 47,500 (  30.2 % )
```


## Question 2: What is the outstanding tax burden?

This really just prints a tax summary, as shown above.



## Question 3:  How many RSUs need to be sold to cover tax burden?

Pretty straight forward -- what is it going to take to cover your tax
burden?



## Question 4: How much cash if we sell it all (starting with the
   expensive NSOs)?

Gives you an idea of how much money you net (post taxes) and how many
NSOs would be sold if you wanted to sell it all.



## Question 5: How much cash if we sell the RSUs?

Same as Question 4, but selling the entire RSU position, and no
options/shares.



## Question 6: If we sell it all, how many ISOs can we buy w/o AMT?

Since ISO exercises incur AMTI burden, and regular income taxes grow
more quickly than AMT taxes, it means that you'll have some number of
ISOs you can exercise, before you end up incurring additional tax
burden from AMT.



## Question 7: If we sell all RSUs, how many ISOs can we buy w/o AMT?

Same as question 6, but if you only sell the RSUs.  Less regular
income (from not selling options) means less regular income tax, means
less shielding from AMT for exercising ISOs.



## Question 8: Basic financials vs share price (RSU + NSO)

This one produces two graphs of basic financial information (y axis)
vs share price on the big day (x axis).  One graph is for RSU-only
sales and one is for RSU+NSO sales.

![Basic Financials for RSU+NSO Sales](https://user-images.githubusercontent.com/984746/93916605-a62a5780-fcbe-11ea-8f7a-f5b9257aecf2.png)

![Basic Financials for RSU Only Sales](https://user-images.githubusercontent.com/984746/93916613-a9254800-fcbe-11ea-8ace-54dc36cdd428.png)



## Question 9: What does exercisable ISOs look like vs IPO price?

This one shows the number of ISOs that can be sold without incurring
an additional AMT tax burden.

![Number of Exercisable ISOs without AMT](https://user-images.githubusercontent.com/984746/93916615-a9bdde80-fcbe-11ea-9f3a-d45b182ecc93.png)


# Architecture and Modifications

If you want more than the few random questions we've included for your
convenience, then you'll want to modify things.  The system is written
using a libary calld `pylink`, which was originally written to manage
radio link budgets for low earth orbit spacecraft, but has been
bastardized to do everything from computing `C/N0` values for Voyager
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

 * Change the values specific to you and assumptions about the stock value in `private.py`

 * Add convenience functions to implement the sales logic you want.
   Two such convenience functions exist in `income.py`

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
  
 * Does not handle mobility cases - the tax models assume all your
   vesting and sales happen in the same location. Similarly, everything 
   in here is based on US tax code.
