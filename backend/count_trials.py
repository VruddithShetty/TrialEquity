import asyncio
from database import init_db
from models import Trial

async def count():
    await init_db()
    trials = await Trial.find_all().to_list()
    print(f'Remaining trials: {len(trials)}')

asyncio.run(count())
