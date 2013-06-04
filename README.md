LiveCodea
=========

Live edit [Codea](http://twolivesleft.com/Codea/) project from desktop computer.  
Announcements will take place [here](http://twolivesleft.com/Codea/Talk/discussion/2831/codea-as-repl).  
**A big thanks to TwoLivesLeft for their nice app**

## Recommendations
Before use, backup all your Codea projects and SpritePacks. Read carefully the server and LiveCodea.lua sources. If you find something wrong with it, don't go further. I wouldn't be responsible for any damage caused on your Codea app or computer.  
This being said, the system is at an early state, it's a toy for now. If you like to play, you're welcome!

## Purpose and principle
Edit a running Codea project from a desktop computer. Keep the system simple: flat files witch can be edited from any text editor. Minimum computation for Codea. Don't know if I could do that...  
An http server running on the desktop computer who reflect the project files and grab files changes. A Codea lib which send output prints, save files changes and evaluate chunks of code.  
An override to the Codea `class` function to keep the 'core' methods/propertys of the created instances when code (re)evaluated.

## Installation
Need Python >= 2.5

Grab the repository.  
From Codea create a project named LiveCodea and copy Documents/LiveCodea/Main.lua and Documents/LiveCodea/LiveCodea.lua in their respective tabs.

## Usage
1 Start the server
- From terminal : python server.py.
- Or from Sublime Text 2 : open the root folder as a project, open server.py and build it (super+b). Keep the output opened and you will have the "prints" return from Codea.

2 From Codea
- Create or open a project. The Main tab must contains the project name as a comment. ex: -- My Project
- Add the LiveCodea project as dependency.
- Run the project.

From now you should be able to see and edit the reflected project files located in the Documents folder. A simple test is to open the Main.lua of the current running project, add some code in the draw function and save it. If Codea reflect the changes, you've got it!  
The Sublime Text 2 package provide some shortcuts :  
`alt+enter` evaluate current selection or current line (if no selection)  
`alt+p` add a parameter (width the prompt for parameter type and arguments) for the selected var (word) or var under caret.

## Know bugs, limitations and workarounds
The request polling used is a battery drainer for the device.   
Dependencies of the running project are not synchronized with the server.  
From Codea, when you close the viewer and return to the ide or project screen, http polling is alive. Mean that if you save a project file from the computer, Codea will continue to save the associated tab.  
Fatal error can't be handled. You have to close the viewer and re-run the project.  
The main setup function is evaluated once (like the normal Codea process). So, if you edit this function and save the file, Codea viewer won't eval the last modification until you re-run the project or explicitely fire an evaluation of the modified code.  
Files added/created from the desktop when a project is running will be saved evaluated. But if the viewer is closed and project re-run just after, Codea won't find the new tab(s). You will have to go back to the project screen and re-open the project.  
Files removed from desktop does not remove associated tabs in Codea. You must remove it from both parts.  
Restart project from the viewer crash Codea.  
Instances are not retained on code evaluation.  
... some others I don't have in mind and/or not yet discover.

## Want to Contribute ?
Bring ideas, feedback, bug report, patches, package/plugins for your prefered text editor...

## So, what next
- Grab current project name from plist rather than the Main tab
- Extract changed parts in the main setup function for evaluation
- Retain instances on code evaluation
- Synchronize project dependencies
- Find a way to handle fatal errors and restart properly
- ...