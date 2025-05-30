import asyncio
import random
import logging
from config import TX_DELAY
from eth_abi import encode

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mint_operations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
wrap_contract = '0xA449bc031fA0b815cA14fAFD0c5EdB75ccD9c80f'
usdc_contract = '0xAF33ADd7918F685B2A82C1077bd8c07d220FFA04'

async def mint_usdc(w3, wallet, public):
    try:
        amount = w3.to_wei(random.randint(1000, 10000), "ether")
        tx = {
            "chainId": 84532,
            "data": f"0x40c10f19"
                    f"000000000000000000000000{public.lower()[2:]}"
                    f"{amount:064x}",
            "from": public,
            "gas": random.randint(170000, 200000),
            "gasPrice": await w3.eth.gas_price,
            "nonce": await w3.eth.get_transaction_count(public),
            "to": usdc_contract
        }

        for attempt in range(3):
            try:
                gas_estimate = await w3.eth.estimate_gas(tx)
                tx['gas'] = int(gas_estimate * 1.2)
                break
            except Exception as e:
                if attempt == 2:
                    raise

        signed_tx = w3.eth.account.sign_transaction(tx, wallet)
        tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] != 1:
            raise Exception(f"[{public}] mint_usdc transaction failed")

        logger.info(f"[{public}] mint_usdc DONE | 0x{tx_hash.hex()}")
        return tx_hash.hex()

    except Exception as e:
        logger.error(f"[{public}] mint_usdc failed | {str(e)}")
        raise


async def mint_cusdc(w3, wallet, public):
    try:
        amount = w3.to_wei(random.randint(1000, 10000), "ether")
        tx = {
            "chainId": 84532,
            "data": f"0x40c10f19"
                    f"000000000000000000000000{public.lower()[2:]}"
                    f"{amount:064x}",
            "from": public,
            "gas": random.randint(170000, 200000),
            "gasPrice": await w3.eth.gas_price,
            "nonce": await w3.eth.get_transaction_count(public),
            "to": wrap_contract
        }

        for attempt in range(3):
            try:
                gas_estimate = await w3.eth.estimate_gas(tx)
                tx['gas'] = int(gas_estimate * 1.2)
                break
            except Exception as e:
                if attempt == 2:
                    raise

        signed_tx = w3.eth.account.sign_transaction(tx, wallet)
        tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] != 1:
            raise Exception(f"[{public}] mint_cusdc transaction failed")

        logger.info(f"[{public}] mint_cusdc DONE | 0x{tx_hash.hex()}")
        return tx_hash.hex()

    except Exception as e:
        logger.error(f"[{public}] mint_cusdc failed | {str(e)}")
        raise


async def shield_usdc(w3, wallet, public):
    try:
        amount = w3.to_wei(random.randint(100, 3000), "ether")

        tx = {
            "chainId": 84532,
            "data": f"0x095ea7b3"
                    f"000000000000000000000000{wrap_contract.lower()[2:]}"
                    f"{amount:064x}",
            "from": public,
            "gas": random.randint(170000, 200000),
            "gasPrice": await w3.eth.gas_price,
            "nonce": await w3.eth.get_transaction_count(public),
            "to": usdc_contract
        }
        for attempt in range(3):
            try:
                gas_estimate = await w3.eth.estimate_gas(tx)
                tx['gas'] = int(gas_estimate * 1.1)
                break
            except Exception as e:
                if attempt == 2:
                    raise

        signed_tx = w3.eth.account.sign_transaction(tx, wallet)
        tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] != 1:
            raise Exception(f"[{public}] approve transaction failed")

        logger.info(f"[{public}] approve DONE | 0x{tx_hash.hex()}")
        await asyncio.sleep(random.uniform(TX_DELAY[0], TX_DELAY[1]))
        
        tx = {
            "chainId": 84532,
            "data": f"0xea598cb0"
                    f"{amount:064x}",
            "from": public,
            "gas": random.randint(190000, 220000),
            "gasPrice": await w3.eth.gas_price,
            "nonce": await w3.eth.get_transaction_count(public),
            "to": wrap_contract
        }

        for attempt in range(3):
            try:
                gas_estimate = await w3.eth.estimate_gas(tx)
                tx['gas'] = int(gas_estimate * 1.1)
                break
            except Exception as e:
                if attempt == 2:
                    raise

        signed_tx = w3.eth.account.sign_transaction(tx, wallet)
        tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] != 1:
            raise Exception(f"[{public}] wrap transaction failed")

        logger.info(f"[{public}] wrap DONE | 0x{tx_hash.hex()}")
        return tx_hash.hex()

    except Exception as e:
        logger.error(f"[{public}] shield_usdc failed | {str(e)}")
        raise


async def unshield_cusdc(w3, wallet, public):
    try:
        amount = w3.to_wei(random.randint(100, 2999), "ether")
        tx = {
            "chainId": 84532,
            "data": f"0xde0e9a3e{amount:064x}",
            "from": public,
            "gas": random.randint(190000, 220000),
            "gasPrice": await w3.eth.gas_price,
            "nonce": await w3.eth.get_transaction_count(public),
            "to": wrap_contract
        }

        for attempt in range(3):
            try:
                gas_estimate = await w3.eth.estimate_gas(tx)
                tx['gas'] = int(gas_estimate * 1.2)
                break
            except Exception as e:
                if attempt == 2:
                    raise

        signed_tx = w3.eth.account.sign_transaction(tx, wallet)
        tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] != 1:
            raise Exception(f"[{public}] unshield cusdc transaction failed")

        logger.info(f"[{public}] unshield_cusdc DONE | 0x{tx_hash.hex()}")
        return tx_hash.hex()

    except Exception as e:
        logger.error(f"[{public}] unshield_cusdc failed | {str(e)}")
        raise
