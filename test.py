import asyncio
import keyboard

async def print_continuously():
    while True:
        print("Printing something in the console...")
        await asyncio.sleep(1)  # wait for 1 second before printing again

async def listen_for_keypress():
    while True:
        if keyboard.is_pressed('l'):  # check if the 'q' key is pressed
            print("move right")
        if keyboard.is_pressed('h'):  # check if the 'q' key is pressed
            print("move left")
        await asyncio.sleep(0.1)  # wait for 0.1 seconds before checking again

async def main():
    # start both tasks concurrently
    task1 = asyncio.create_task(print_continuously())
    task2 = asyncio.create_task(listen_for_keypress())

    # wait for either of the tasks to finish
    await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)

asyncio.run(main())
