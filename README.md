Rust Completion
==================
Note that this package is not currently working for Mac OS X. 

This sublime package provides autocompletion for Rust. This includes auto-completion for structs, traits, modules, crates, functions, enums, and structfields. 
![Basic Auto-Complete](/pics/simple.tiff?raw=true)
(Note: we cannot ensure that all of these are 100% complete, but from the testing we performed it does capture the majority of them.) 

We used Phil Dawes' RACER program (located at https://github.com/phildawes/racer.git) as the starter for our package. It looks through Rust's source code for possible auto-complete options and returns the line that corresponds. We added additional functionality to RACER to accommodate traits, enums, and functions of structs, traits and enums. We also added auto-complete for personal functions (i.e. functions you wrote within the code) and for lifetime variables.

Example of Auto Complete for Personal Functions:
![Personal Functions](/pics/personalFunc.tiff?raw=true)

Example of Auto Complete for Lifetime Variables:
![Lifetime Variables](/pics/lifetimeVars.tiff?raw=true)

For functions, the auto-complete pop-up shows the function name and its arguments and their types, then selecting the function prints the function with just the arguments that you can tab through to edit. 

Example of Tabbing for function arguments:
![Argument Tabbing](/pics/arguments.tiff?raw=true)

We also added the ability to continue off of previously stated 'use' statements. 

Example of Auto Complete for previous 'use' statements:
![Continued Use Statements](/pics/continuedUse.tiff?raw=true)


