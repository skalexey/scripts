import asyncio

async def task():
	print("Task started")
	await asyncio.sleep(1)
	print("Task completed")

async def main():
	# Create a task but don't await it
	t = asyncio.create_task(task())

	# Check if the task is done
	if t.done():
		print("Task is done")
	else:
		print("Task is not done")

	# Function exits without awaiting the task
	print("Function exiting")

# Run the event loop
asyncio.run(main())
