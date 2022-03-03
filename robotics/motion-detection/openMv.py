# Advanced Frame Differencing Example
#
# This example demonstrates using frame differencing with your OpenMV Cam. This
# example is advanced because it preforms a background update to deal with the
# backgound image changing overtime.

import sensor, image, pyb, os, time, ustruct

TRIGGER_THRESHOLD = 5

BG_UPDATE_FRAMES = 1 # How many frames before blending.
BG_UPDATE_BLEND = 128 # How much to blend by... ([0-256]==[0.0-1.0]).

# Timing
total_movement_time = 0
trig_time = 0

# Keep track of triggers: The trigger value turns False once when the
# BG_UPDATE_FRAMES theshold is reached, the stopping of the object
# is indicated through the fact that the triggered value is False MULTIPLE TIMES
trigger_count = 0

# Utility functions
def send_data(data):
    try:
        bus.send(ustruct.pack("<h", len(data)), timeout=10000) # Send the len first (16-bits).
        try:
            bus.send(data, timeout=10000) # Send the data second.
            #print("Sent Data!") # Only reached on no error.
        except OSError as err:
            pass # Don't care about errors - so pass.
            # Note that there are 3 possible errors. A timeout error, a general purpose error, or
            # a busy error. The error codes are 116, 5, 16 respectively for "err.arg[0]".
    except OSError as err:
        pass

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # or sensor.RGB565
sensor.set_framesize(sensor.QVGA) # or sensor.QQVGA (or others)
sensor.skip_frames(time = 2000) # Let new settings take affect.
sensor.set_auto_whitebal(False) # Turn off white balance.
clock = time.clock() # Tracks FPS.

#arduino
# The hardware I2C bus for your OpenMV Cam is always I2C bus 2.
bus = pyb.I2C(2, pyb.I2C.SLAVE, addr=0x12)
bus.deinit() # Fully reset I2C device...
bus = pyb.I2C(2, pyb.I2C.SLAVE, addr=0x12)
print("Waiting for Arduino...")

# Take from the main frame buffer's RAM to allocate a second frame buffer.
# There's a lot more RAM in the frame buffer than in the MicroPython heap.
# However, after doing this you have a lot less RAM for some algorithms...
# So, be aware that it's a lot easier to get out of RAM issues now. However,
# frame differencing doesn't use a lot of the extra space in the frame buffer.
# But, things like AprilTags do and won't work if you do this...
extra_fb = sensor.alloc_extra_fb(sensor.width(), sensor.height(), sensor.RGB565)

print("About to save background image...")
sensor.skip_frames(time = 2000) # Give the user time to get ready.
extra_fb.replace(sensor.snapshot())
print("Saved background image - Now frame differencing!")

triggered = False

frame_count = 0
while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    frame_count += 1
    if (frame_count > BG_UPDATE_FRAMES):
        frame_count = 0
        # Blend in new frame. We're doing 256-alpha here because we want to
        # blend the new frame into the backgound. Not the background into the
        # new frame which would be just alpha. Blend replaces each pixel by
        # ((NEW*(alpha))+(OLD*(256-alpha)))/256. So, a low alpha results in
        # low blending of the new image while a high alpha results in high
        # blending of the new image. We need to reverse that for this update.
        img.blend(extra_fb, alpha=(256-BG_UPDATE_BLEND))
        extra_fb.replace(img)

    # Replace the image with the "abs(NEW-OLD)" frame difference.
    img.difference(extra_fb)

    hist = img.get_histogram()
    # This code below works by comparing the 99th percentile value (e.g. the
    # non-outlier max value against the 90th percentile value (e.g. a non-max
    # value. The difference between the two values will grow as the difference
    # image seems more pixels change.
    diff = hist.get_percentile(0.99).l_value() - hist.get_percentile(0.90).l_value()
    triggered = diff > TRIGGER_THRESHOLD


    # Increment or 0 the `tigger_count` according to the motions of the object
    if triggered:
        trig_time = time.ticks_ms()
        trigger_count = 0

    else:
        trigger_count += 1
        send_data(str(total_movement_time))

    if trigger_count > 1: # It's definetly stopped
        total_movement_time = 0 # Reset all the timer values
        trig_time = 0

    else:
        total_movement_time += time.ticks_diff(time.ticks_ms(), trig_time)
        if total_movement_time > 500:
            send_data("fire!")
        else:
            send_data(str(total_movement_time))

    print(trigger_count) # Note: Your OpenMV Cam runs about half as fast while
    # connected tro your computer. The FPS should increase once disconnected.
