# gd-io, by lcd_seansystem
*Alternative title: [gd.py](https://pypi.org/project/gd.py/) (Taylor's Version)*

This library is my version of the local-level I/O functionality of some of the gd-python libraries I've seen floating around the net, a lot of which I've had my own major issues with. This was developed mostly out of necessity during the creation of my level [How to Disappear](https://www.youtube.com/watch?v=tJGxaICiD_A), in order to expedite and automate the process of otherwise tedious tasks. The aim is to bring scripting capabilities to users who aren't necessarily familiar with the ins and outs of Python at a technical level but who are capable enough to do basic programming in the language, to help out people who want the same sort of extra power over the editor as I did with as little overhead as possible. I wasn't initially going to put this code out, out of fear of the release of 2.2 breaking the library entirely, but my own recent testing has revealed that everything seems to be operational; making this code open-source and available to as many people as possible felt like something worth doing in that case. As always with these GD-related coding things I'm indebted to the work of [Spu7nix](https://www.youtube.com/@Spu7Nix), who developed an early version of `levelStringImporter.py` a long time ago (as early as 2019!) that I've since rewritten and cleaned up.

If you'd like to get started, check out the documentation and examples below. Alternatively if you'd like to get in touch with me about any questions, you can contact me on Discord at __@lcd_seansystem__; I'm generally available to field any questions you might have.

Major disclaimer: __Please use gd-io at your own discretion.__ I've personally encountered zero issues with data corruption thus far in my extensive use of this library for myself, but I'm also a solo developer on this stuff; there may be issues I haven't caught. I am ultimately not liable for whatever happens on your machine. In other words: **Make backups of everything!**

### Important notes about usage
- gd-io has been verified for **Geometry Dash 2.204**, **Python 3.10.0**, and **Windows 10.0.19045 Build 19045**. If you are having any issues, ensure you have these versions at a minimum. 
- gd-io has not been verified for any sort of Mac OS or Linux-based system.
- Reading from and writing to a level can only be done __while the game is closed__. Unfortunately the game does not load a level's information from `CCLocalLevels.dat` anywhere except on game startup, and on game exit it will overwrite your data in `CCLocalLevels.dat` with whatever is in game.
- There is a known issue with trying to read from an empty level; the game doesn't create the headers for a level that is empty. If you want to populate an empty level please include a singular block somewhere for your own sake.
- This version of gd-io will only read and write to your top-most level; make sure you move your level to the top using the up-arrow on your level editor browsing screen to access the particular level you would like to read or write to.
- gd-io doesn't interact with RobTop's servers or endpoints in any way. Check out [gd.py](https://pypi.org/project/gd.py/) if you'd like to do that type of stuff.

---

## Documentation

There isn't much in this library, so this section will likely be all the documentation I write for it - ultimately a full site didn't feel necessary. My goal was to simplify the manipulation of objects and colors and levels in a way that made intuitive sense to myself, and in doing so, a lot of the strange abstractions some other libraries made aren't present here (likely substituted for my own flavor of strange abstractions). If you'd like further clarification about something, be sure to contact me using the details provided above.

### Object types

#### `gdLevel`

Representing a level, which is comprised of objects, color channels, and headers.

- `objs: list[gdObject]` - A list comprising all objects of the level.
- `cols: list[gdColor]` - A list comprising all color channels of the level.
- `headers: str` - A string comprising additional information of the level.

#### `gdObject`

Representing a single Geometry Dash object, which has a series of attributes.

- `ID: int` - The object ID of the object, which tells you what it is (a block, a spike, a trigger, etc).
- `x: float` - The position of the object along the horizonal axis, with a scale of 30 units = 1 grid space.
- `y: float` - The position of the object along the vertical axis, with a scale of 30 units = 1 grid space.

All other attributes outside of these 3 are optional for any object; the game will automatically populate objects with default values for necessary attributes if that data is not provided by the user. If you provide an attribute for an object that doesn't use it, the game will generally ignore it - though I haven't tested this extensively; maybe you'll find something weird!

A mostly-comprehensive list of these attributes, associating each numerical attribute ID with a title and data type, can be found in `attributeData.py`. Since gd-io was developed almost entirely in 2.1, information regarding the attributes of objects has not been updated for 2.2. If you'd like to help with the population and naming of these attributes to something more readable and appropriate, feel free to put up an issue on this repository page (assuming I've provided the permissions to do so).

#### `gdColor`

Representing a single Geometry Dash color channel, which has a series of attributes.

NOTE: These are for the colors set at the start of the level, NOT for color triggers set during the course of the level (which are nominally objects).

- `ID: int` - The color channel number of the object. Special color channels are generally at 1000 and above.
- `red: int` - The red value for the color channel.
- `green: int` - The green value for the color channel.
- `blue: int` - The blue value for the color channel.

All other attributes outside of these 4 are optional for any color channel; the game will automatically populate the channel with default values for necessary attributes if that data is not provided by the user.

### Useful class methods

Most of the class methods used throughout gd-io are pretty much exclusively used internally and are of no use to most people, but a few aren't, so here they are for your pleasure.

Structure for a method signature:
`class: method(self, parameter1, parameter2) -> return_type`

NOTE: Python structures class methods with the first parameter being "self"; this is not an actual parameter you fill in and should be ignored as though it weren't even there. They are included in the function signature to be in-line with Python standards but may be confusing if you're not familiar with Python.

- `gdLevel: objs_printable(self, filter: Callable[[gdObject], bool] = None) -> str`

Returns a string comprising every object (gdObject) within a level (gdLevel), for pretty printing.
A filter, which is a reference to a method that accepts a gdObject and returns a boolean, can be passed in as an argument to only print out particular objects.

- `gdLevel: cols_printable(self, filter: Callable[[gdColor], bool] = None) -> str`

Returns a string comprising every color (gdColor) within a level (gdLevel), for pretty printing.
A filter, which is a reference to a method that accepts a gdColor and returns a boolean, can be passed in as an argument to only print out particular colors.

- `gdLevel: map(self, func: Callable[[gdObject], None], filter: Callable[[gdObject], bool] = None) -> None`

Modifies all the objects in a level according to a function (func) that edits the object in-place. 
A filter, which is a reference to a method that accepts a gdObject and returns a boolean, can be passed in as an argument to only modify particular objects.

- `gdLevel: get_color_channel(self, val: int) -> gdColor`

Gets a particular color channel from a level based on an ID. If there exists no color with the specified ID, the method returns the default white that all channels are initially set to.

---

## Example code

This section provides a series of examples on how to do basic functions with gd-io, written with the current layout and import structure of `main.py` in mind. These examples also demonstrate the functionality of some lesser-known python functions that are generally very useful in operating the library. If you'd like to test them out, the following examples should be pasted in where it says "Put your script here!" in `main.py`.

### Creating an object

```
    obj = gdObject({
        "ID": 1,
        "x": 45.0,
        "y": 45.0
    })
```

This code example creates a `gdObject` that represents a default block placed at (45, 45). This has not been added to the level; it merely exists in code.

### Adding an object to a level

```
    obj = gdObject({
        "ID": 1,
        "x": 45.0,
        "y": 45.0
    })
    lvl.objs.append(obj)
```

This code example creates a `gdObject` that represents a default block placed at (45, 45), and then adds this block to the level.

### Creating a color

```
    col = gdColor({
        "ID": 1,
        "red": 255,
        "green": 0,
        "blue": 255
    })
```

This code example creates a `gdColor` that represents color channel 1 with the color set to red. This has not been added to the level; it merely exists in code.

### Adding a color to a level

```
    col = gdColor({
        "ID": 1,
        "red": 255,
        "green": 0,
        "blue": 255
    })
    lvl.cols.append(col)
```

This code example creates a `gdColor` that represents color channel 1 with the color set to red, and then adds this color to the level.

### Creating an object with many attributes

```
    obj = gdObject({
        "ID": 207,
        "x": 45.0,
        "groups": [2, 4],
        "y": 90.0,
        "color": 1,
        "color-secondary": 2
    })
```

This code example creates a `gdObject` that represents a block with two colors placed at (45, 90), where the primary color is channel 1 and the secondary color is channel 2. The block also has groups 2 & 4. Please note that attributes may be ordered within the dictionary in any order - here we have the 'y' attribute below the groups attribute.
Please see `attributeData.py` for information on existing attributes and their associated data types.

### Updating an object's attribute

```
    obj = gdObject({
        "ID": 1,
        "x": 45.0,
        "y": 45.0
    })
    setattr(obj, "y", 90.0)
```

This code example creates a `gdObject` that represents a default block placed at (45, 45), and then sets the 'y' attribute of the object to 90.0.

### Adding an attribute to an object

```
    obj = gdObject({
        "ID": 1,
        "x": 45.0,
        "y": 45.0
    })
    setattr(obj, "color", 5)
```

This code example creates a `gdObject` that represents a default block placed at (45, 45), and then adds the 'color' attribute to the object with a value of 5.

### Reading an attribute of an object

```
    obj = gdObject({
        "ID": 1,
        "x": 45.0,
        "y": 45.0
    })
    print(getattr(obj, "x", "no x"))
    print(getattr(obj, "color", "no color"))
```

This code example creates a `gdObject` that represents a default block placed at (45, 45), and then attempts to print out the 'x' & 'color' attributes, respectively. In this scenario, the output will look like the following:
```
45.0
no color
```
Because the object has an 'x' attribute, the value of the 'x' attribute is printed. However, because the object does not have a 'color' attribute, the code will instead print out the default value provided by the third argument of the function attemping to pull the value of the 'color' attribute from the object. 

Generally when using `getattr()`, you'll want to have a default value (it'll save yourself a lot of headaches).

### Removing an attribute of an object

```
    obj = gdObject({
        "ID": 1,
        "x": 45.0,
        "y": 45.0,
        "color": 5
    })
    delattr(obj, "color")
```

This code example creates a gdObject that represents a default block placed at (45, 45) with a primary color of channel 5, and then removes the color attribute from the object. Note that, in general, if an object requires that attribute in-game, completing this operation is equivalent to resetting the value of the attribute to its default.