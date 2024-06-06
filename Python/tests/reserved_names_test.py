import asyncio


class A:
	async def asyncio_wait(self, timeout=None):
		event = asyncio.Event()
		def on_notify(*args, **kwargs):
			event.set()
		cb_id = self.subscribe(on_notify)
		await asyncio.wait_for(event.wait(), timeout)
		self.unsubscribe(cb_id)
		return event.is_set()