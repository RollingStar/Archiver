Archiver 
===============

This small tool archives files in this way:

1. Get a password & directory name
2. Create a split 7-zip archive for each entry (file or folder) in the input directory
3. Generate parity files for each archive with [parpar](https://github.com/animetosho/ParPar)

It should be suitable for the avalanche of low-cost file hosting websites and tools that are now available. It requires zero trust in a website's privacy policy or their ability to withstand a cyberattack.

It does require trust in these:

1. The program itself
2. 7-zip
3. parpar
4. Your operating system's implementation of Python's `os.urandom()` [function](https://docs.python.org/3.6/library/os.html#os.urandom), at a software and hardware level.

Windows-only
============

This only works on Windows. It should be trivial to alter the script to work on other platforms.

Other Tools
=======

[Restic](https://github.com/restic/restic/) is a relevant Linux tool.

License
=======

[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)
