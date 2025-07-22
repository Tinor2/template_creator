1) Ensure that before any changes are created, you refer to this markdown file.
2) Ensure the CHANGELOG.md file is up to date.    
    a) When adding a new change, ensure that the change is added to the CHANGELOG.md file.
    b) When removing a change, ensure that the change is removed from the CHANGELOG.md file.
    c) When modifying a change, ensure that the change is modified in the CHANGELOG.md file.
    The point of this is to ensure that the CHANGELOG.md file has only useful information; If there is history about the way or reason a line of code was implemented, this is useful to know in the future. However, if there is a change that is made, and immeadiately scrapped, this change should be removed from the CHANGELOG.md file. 
    d) The CHANGELOG.md file be organized in chronological order, including dates. In a sense, it should double as a logbook, but remember the primary purpose is to provide context behind the history of the code.
3) Ensure that any code being implemen=ted is done with the intent of being as simple as neccesary; Do not overcomplicate, and add a plethora of features that are not needed.
    Note this does not mean you shouldnt add features that havent directly asked for, but it does mean that the code shouldnt become bogged down with code that isnt neccesarily the focus of the file.
4) Ensure that PEP 8 Standards are maintained
5) Dont be afraid to ask questions; If you dont understand something, ask for clarification. 
6) Dont be afraid to remove previous content; If there is a problem, often time scrapping the current approach is a lot easier than adding more and more code to try and fix the issue.  
7) Walk through the changes you make after you make them
    a) Ensure that the changes you make are logical and make sense.
    b) Ensure that the changes you make are not redundant.
8) After implement any code, make sure that there are no obvious errors, or potential bugs; If tehre are either fix them, or if they arent exactly pressing, but could be a source of errors in the future, notify me about it.