import asyncio
import telegram
import config
async def main() -> None:
    await telegram.start_bot(config.get_config())

if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
