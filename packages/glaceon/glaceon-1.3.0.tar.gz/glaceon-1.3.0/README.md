# `🐙` **GLACEON**

> __Glaceon is a simple and very clean logging library that can be used for any type of application that you may want to use it for. This project is completely open source and noob friendly. Feel free to use it and get your console logs looking clean.__

# `📜` **DOCS**

__Example Usage Of Glaceon:__


```py
from glaceon import cli

g = cli(debug=True, speed=2)

g.print("INFO", "This is an info message")
g.print("WARNING", "This is a warning message")
g.print("ERROR", "This is an error message")
g.print("SUCCESS", "This is a success message")
g.print("DEBUG", "This is a debug message")
```

__Output:__ 

*https://media.discordapp.net/attachments/1106381310085308416/1107275928066850886/Screenshot_2023-05-14_055856.png*


> __`debug=True` is if you wanna put debug messages inbetween functions and lines of code. Instead of having to delete all the debug messages you put in the code, you can simply turn the debug value to `False` which makes the debug messages not visible. You can simply turn them back on by turning the debug value back to `True`.__

> __You can also adjust the speed of the text by changing the `speed` value when you initialize glaceon. Example: `g = cli(debug=False, speed=5)`__

# `🌈` **COLORS**

- __INFO:__ *Purple*
- __WARNING:__ *Orange/Yelow Fade*
- __ERROR:__ *Red*
- __SUCCESS:__ *Green*
- __DEBUG:__ *Blue*

I made this half asleep while I was bored so there mayyyyyyy be some bugs and it might be a little slow but I will make sure to fix all bugs (if there are any) and make it a little faster. Enjoy this library :)