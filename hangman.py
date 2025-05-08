import asyncio
from web3 import Web3
import random
import logging
from eth_abi import encode
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mint_operations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


WORDS = [
    "play", "time", "home", "mind", "work", "jump", "farm", "cake",
    "bake", "fire", "wind", "gold", "road", "love", "rock", "rain",
    "star", "fish", "desk", "news", "team", "care", "peak", "golf",
    "mesh", "ping", "dock", "lamb", "comb", "stem", "grow", "clan",
    "hint", "glad", "vile", "zone", "xray", "kids", "pony", "germ",
    "bank", "ship", "bark", "dust", "made", "sake", "corn", "pail",
    "tuck", "boil", "ramp", "vase", "blow", "chat", "drum", "flop",
    "grim", "hazy", "jolt", "keen", "lurk", "moat", "numb", "oath",
    "pace", "quit", "rude", "dope", "tail", "urge", "veto", "yarn",
    "zinc"
]
MAX_LIVES = 8

HANGMAN_FACTORY_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "player", "type": "address"},
            {"indexed": False, "internalType": "address", "name": "gameContract", "type": "address"}
        ],
        "name": "GameCreated",
        "type": "event"
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "getGameAddressByPlayer",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]


def simulate_game_state(word, guessed_letters, lives):
    display_word = ''.join(letter if letter in guessed_letters else '_' for letter in word)
    has_won = display_word == word
    has_lost = lives <= 0 and not has_won
    return {
        'display_word': display_word,
        'lives': lives,
        'has_won': has_won,
        'has_lost': has_lost
    }


async def create_game(w3, wallet):
    try:
        public = w3.to_checksum_address(Web3().eth.account.from_key(wallet).address)
        tx = {
            "chainId": 84532,
            "data": f"0x9feb6c1b000000000000000000000000{public.lower()[2:]}",
            "from": public,
            "gas": random.randint(1700000, 2300000),
            "gasPrice": await w3.eth.gas_price,
            "nonce": await w3.eth.get_transaction_count(public),
            "to": '0x9d0C9Cde372c3b50e953E6dD620B503f2Bddc6A2'
        }

        for attempt in range(3):
            try:
                gas_estimate = await w3.eth.estimate_gas(tx)
                tx['gas'] = int(gas_estimate * 1.2)
                break
            except Exception as e:
                if attempt == 2:
                    raise Exception(f"Gas estimation failed: {str(e)}")

        signed_tx = w3.eth.account.sign_transaction(tx, wallet)
        tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] != 1:
            raise Exception(f"[{public}] create_game transaction failed")

        factory_contract = w3.eth.contract(address='0x9d0C9Cde372c3b50e953E6dD620B503f2Bddc6A2', abi=HANGMAN_FACTORY_ABI)
        game_address = None
        for log in receipt['logs']:
            if log['topics'][0].hex() == Web3.keccak(text="GameCreated(address,address)").hex():
                try:
                    game_address = Web3.to_checksum_address('0x' + log['data'][-40:])
                except Exception as e:
                    # logger.warning(f"[{public}] Failed to parse GameCreated event: {str(e)}")
                    break

        if not game_address:
            game_address = await factory_contract.functions.getGameAddressByPlayer(public).call()

        if not game_address:
            raise Exception(f"[{public}] Failed to get HangmanGame address")

        logger.info(f"[{public}] create_game DONE | 0x{tx_hash.hex()} | Game address: {game_address}")
        return game_address

    except Exception as e:
        logger.error(f"[{public}] create_game failed | {str(e)}")
        raise


async def guess_letter(w3, wallet, game_address, letter):
    try:
        public = w3.to_checksum_address(Web3().eth.account.from_key(wallet).address)
        encoded_string = encode(['string'], [letter]).hex()[2:]
        tx_data = f"0x662a655900{encoded_string}"
        tx = {
            "chainId": 84532,
            "data": tx_data,
            "from": public,
            "gas": random.randint(1100000, 1500000),
            "gasPrice": await w3.eth.gas_price,
            "nonce": await w3.eth.get_transaction_count(public),
            "to": game_address
        }

        for attempt in range(3):
            try:
                gas_estimate = await w3.eth.estimate_gas(tx)
                tx['gas'] = int(gas_estimate * 1.2)
                break
            except Exception as e:
                if attempt == 2:
                    raise Exception(f"Gas estimation failed: {str(e)}")

        signed_tx = w3.eth.account.sign_transaction(tx, wallet)
        tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] != 1:
            raise Exception(f"[{public}] guess_letter transaction failed")

        logger.info(f"[{public}] guess_letter('{letter}') DONE | 0x{tx_hash.hex()}")
        return tx_hash.hex()

    except Exception as e:
        logger.error(f"[{public}] guess_letter('{letter}') failed | {str(e)}")
        raise


async def play_hangman(w3, wallet, public):
    try:
        game_address = await create_game(w3, wallet)

        secret_word = random.choice(WORDS)
        logger.info(f"[{public}] Simulated secret word: {secret_word}")
        guessed_letters = set()
        lives = MAX_LIVES
        word_letters = list(secret_word)
        available_wrong_letters = [c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in secret_word]

        while lives > 0 and word_letters:
            if random.random() < config.ERROR_PROBABILITY and available_wrong_letters:
                letter = random.choice(available_wrong_letters)
                available_wrong_letters.remove(letter)
            else:
                letter = random.choice(word_letters)
                word_letters.remove(letter)

            await guess_letter(w3, wallet, game_address, letter)
            guessed_letters.add(letter)
            if letter not in secret_word:
                lives -= 1

            state = simulate_game_state(secret_word, guessed_letters, lives)
            # logger.info(f"[{public}] State after guessing '{letter}': {state}")

            if state['has_won']:
                logger.info(f"[{public}] Game completed: Won!")
                break
            if state['has_lost']:
                logger.info(f"[{public}] Game completed: Lost!")
                break

            await asyncio.sleep(random.uniform(config.TX_DELAY[0], config.TX_DELAY[1]))

        return True

    except Exception as e:
        logger.error(f"[{public}] play_hangman failed | {str(e)}")
        raise
