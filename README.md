 * have grants and sell orders, but should transition to starting
   grants, sell orders, and ending grants.  that allows computing of
   final position, and maintains cache coherency.

 * Does not do anything with long-term capital gains

 * The tax tables and standard deductions assume you are a married
   couple filing jointly

 * you MUST MUST MUST run `model.clear_cache()` after you execute the
   `sell` method in one of the `Grant` objects because it will
   invalidate the cache, but pylink won't know...yeah yeah yeah, I
   need to add a `cache_invalidate(node)` routine to the DAGModel in
   pylink....get off my back.

 * unit tests for selling

 * unit tests for income tracking

 * need to do a meticulous walkthrough on the unit tests in general

 * There can be some weirdness regarding around the number of options
   -- adjust using the cliff_n as needed.

 * 
