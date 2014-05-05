Rust Completion
==================
Note that this package is not currently working for Mac OS X. 

This sublime package provides autocompletion for Rust. This includes auto-completion for structs, traits, modules, crates, functions, enums, and structfields. 

(Note: we cannot ensure that all of these are 100% complete, but from the testing we performed it does capture the majority of them.) 

We used Phil Dawes' RACER program (located at https://github.com/phildawes/racer.git) as the starter for our package. It looks through Rust's source code for possible auto-complete options and returns the line that corresponds. We added additional functionality to RACER to accommodate more functions, and traits, and a few other things. 

For functions, the auto-complete pop-up shows the function name and its arguments and their types, then selecting the function prints the function with just the arguments that you can tab through to edit. 
