# Timing the movement of an object
This document aims to walk you through a way to time the movement of an object. The following code was used for a competition challange on March 2nd 2022. The participants were aiming to not move for more than one minute, otherwise, they'll lose.

## Caveat
Before we continue, it's important to mention that the timing isn't perfect. You should always do trial and error and compare the movement with a trusted spotwatch. 
## Debugging tip
This code has everything you need to connect with an arduino microcontroller. You can print the message from open mv on an lcd
or the serial terminal and debug :)

## Code Structure
The main motion detection module is written in python for the open mv cam, your policy as to what to do with the information 
is totally dependant on your specific needs. The arduino code is a sample for what's possible. 

## Quick, final note
You might experience delays and hang time if one module (arduino or open mv) isn't connected with a usb cable to the laptop
Either remove both of theme or have both connected.<br/>
and ofcourse, if you don't need to communicate anything with other microcontrollers, remove the I2C connection part. <br/>
Happy Using:)
