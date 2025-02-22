import asyncio
from app import app
import offers

async def run_flask_app():
    app.run(debug=True)

async def main():
    flask_task = asyncio.create_task(run_flask_app())
    offers_task = asyncio.create_task(offers.find_last_holiday())
    await asyncio.gather(flask_task, offers_task)

if __name__ == '__main__':
    asyncio.run(main())