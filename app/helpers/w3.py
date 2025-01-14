import logging
import re
from functools import cache

from ens import ENS
from eth_account.messages import encode_defunct
from eth_typing import ChecksumAddress
from eth_utils import ValidationError
from web3 import Web3
from web3.exceptions import ContractLogicError

from app.config import get_settings
from app.helpers.abis import erc721_abi, erc1155_abi
from app.helpers.alchemy import get_image_url as get_alchemy_image_url
from app.helpers.alchemy import get_nft as get_alchemy_nft

logger = logging.getLogger(__name__)


def checksum_address(address: str) -> ChecksumAddress:
    return Web3().toChecksumAddress(address)


def get_wallet_address_from_signed_message(message: str, signature: str) -> str:
    encoded_message = encode_defunct(text=message)
    try:
        address = Web3().eth.account.recover_message(encoded_message, signature=signature)
    except ValidationError as e:
        raise ValueError(e)
    return address


@cache
def get_ens_primary_name_for_address(wallet_address: str) -> str:
    settings = get_settings()
    web3_client = Web3(Web3.WebsocketProvider(settings.web3_provider_url_ws))
    wallet_address = checksum_address(wallet_address)
    ens_name = ENS.fromWeb3(web3_client).name(wallet_address)
    return ens_name


async def get_wallet_short_name(address: str, check_ens: bool = True) -> str:
    address = checksum_address(address)
    short_address = f"{address[:5]}...{address[-3:]}"
    if check_ens:
        try:
            ens_name = get_ens_primary_name_for_address(address)
            short_address = ens_name or short_address
        except Exception:
            logger.exception("Problems fetching ENS primary domain. [address=%s]", address)

    return short_address


async def _replace_with_cloudflare_gateway(token_image_url: str) -> str:
    ipfs_re = r"(?:ipfs:\/\/|ipfs.io\/)(?:ipfs\/)?(.+)"
    pinata_ipfs_re = r"pinata\.cloud\/(?:ipfs\/)?(.+)"
    ipfs_match = re.findall(ipfs_re, token_image_url, flags=re.IGNORECASE)
    if ipfs_match:
        image_path = ipfs_match[0]
        return f"https://cloudflare-ipfs.com/ipfs/{image_path}"

    pinata_match = re.findall(pinata_ipfs_re, token_image_url, flags=re.IGNORECASE)
    if pinata_match:
        image_path = pinata_match[0]
        return f"https://cloudflare-ipfs.com/ipfs/{image_path}"

    return token_image_url


async def get_nft(contract_address: str, token_id: str, provider: str = "alchemy") -> dict:
    if provider == "alchemy":
        return await get_alchemy_nft(contract_address, token_id)
    else:
        raise NotImplementedError("no other providers implemented")


async def get_nft_image_url(nft, provider: str = "alchemy"):
    if provider == "alchemy":
        image_url = await get_alchemy_image_url(nft)
    else:
        raise NotImplementedError("no other providers implemented")

    return await _replace_with_cloudflare_gateway(token_image_url=image_url)


async def verify_token_ownership(contract_address: str, token_id: str, wallet_address: str) -> bool:
    settings = get_settings()
    web3_client = Web3(Web3.WebsocketProvider(settings.web3_provider_url_ws))
    contract_address = checksum_address(contract_address)
    wallet_address = checksum_address(wallet_address)
    token_id_int = int(token_id)

    try:
        contract = web3_client.eth.contract(address=contract_address, abi=erc721_abi)
        current_owner = contract.functions.ownerOf(token_id_int).call()
        return current_owner == wallet_address
    except ContractLogicError:
        contract = web3_client.eth.contract(address=contract_address, abi=erc1155_abi)
        balance = contract.functions.balanceOf(wallet_address, token_id_int).call()
        return balance > 0
    except Exception as e:
        logger.warning(f"exception verifying ownership of {contract_address}/{token_id_int} for {wallet_address} | {e}")
        return False
