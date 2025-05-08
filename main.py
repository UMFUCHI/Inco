import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider, Web3
import random
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from config import TX_DELAY
from hangman import play_hangman
import config
from comfy import mint_usdc, mint_cusdc, shield_usdc, unshield_cusdc

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mint_operations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)




async def process_wallet(w3, wallet, functions):
    random.shuffle(functions)
    public = w3.to_checksum_address(Web3().eth.account.from_key(wallet).address)
    balance = w3.from_wei(await w3.eth.get_balance(public), 'ether')
    if balance < 0.0001:
        logger.warning(f"[{public}] has low balance: {balance} ETH")
        return
    for func in functions:
        try:
            await func(w3, wallet, public)
            await asyncio.sleep(random.uniform(TX_DELAY[0], TX_DELAY[1]))
        except Exception as e:
            pass
            # logger.error(f"Function {func.__name__} failed for wallet {wallet}: {str(e)}")


async def main():
    try:
        with open('wallets.txt', 'r') as f:
            wallets = [line.strip() for line in f if line.strip()]

        num_threads = int(input("Enter number of threads: "))

        if config.shuffle_wallets:
            random.shuffle(wallets)

        w3 = AsyncWeb3(AsyncHTTPProvider('https://sepolia.base.org'))
        if not await w3.is_connected():
            raise Exception("Failed to connect to testnet")

        logger.info("Connected to testnet")

        functions = [mint_usdc, mint_cusdc, shield_usdc, unshield_cusdc, play_hangman]

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            tasks = [
                loop.run_in_executor(
                    executor,
                    partial(
                        asyncio.run,
                        process_wallet(w3, wallet, functions.copy())
                    )
                )
                for wallet in wallets
            ]
            await asyncio.gather(*tasks)

        logger.info("All wallet operations completed")

    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")
        raise


if __name__ == '__main__':
    asyncio.run(main())
