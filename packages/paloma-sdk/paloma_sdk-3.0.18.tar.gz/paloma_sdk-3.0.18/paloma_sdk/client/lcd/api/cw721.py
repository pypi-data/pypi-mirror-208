from typing import Optional

from paloma_sdk.core.broadcast import SyncTxBroadcastResult
from paloma_sdk.core.coins import Coins
from paloma_sdk.core.wasm import MsgExecuteContract, MsgInstantiateContract

from ..wallet import Wallet
from ._base import BaseAsyncAPI, sync_bind
from .tx import CreateTxOptions

__all__ = ["AsyncCw721API", "Cw721API"]


class AsyncCw721API(BaseAsyncAPI):
    async def instantiate(
        self, wallet: Wallet, code_id: int, name: str, symbol: str, minter: str
    ) -> SyncTxBroadcastResult:
        """instantiate the Cw721 smart contract using code id.
        Args:
            wallet (Wallet): CW721 deployer wallet
            code_id (int): Code_id of CW721 code
            name (str): CW721 token name
            symbol (str): CW721 token symbol
            minter (str): CW721 token minter
        Returns:
            SyncTxBroadcastResult: Transaction Broadcast Result
        """
        instantiate_msg = {"name": name, "symbol": symbol, "minter": minter}
        funds = Coins()
        tx = await wallet.create_and_sign_tx(
            CreateTxOptions(
                msgs=[
                    MsgInstantiateContract(
                        wallet.key.acc_address,
                        None,
                        code_id,
                        "CW721",
                        instantiate_msg,
                        funds,
                    )
                ]
            )
        )
        result = await self._c.tx.broadcast_sync(tx)
        return result

    async def mint(
        self, wallet: Wallet, token: str, token_id: str, owner: str, token_uri: str
    ) -> SyncTxBroadcastResult:
        """Mint CW721 token
        Args:
            wallet (Wallet): CW721 sender wallet
            token (str): CW721 token address
            token_id (str): CW721 token id
            owner (str): owner who will receive the CW721
            token_uri (str): URI of the minting token
        Returns:
            SyncTxBroadcastResult: Transaction Broadcast Result
        """
        execute_msg = {
            "mint": {
                "token_id": token_id,
                "owner": owner,
                "token_uri": token_uri,
                "extension": None,
            }
        }

        funds = Coins()
        tx = await wallet.create_and_sign_tx(
            CreateTxOptions(
                msgs=[
                    MsgExecuteContract(
                        wallet.key.acc_address, token, execute_msg, funds
                    )
                ]
            )
        )
        result = await self._c.tx.broadcast_sync(tx)
        return result

    async def approve(
        self,
        wallet: Wallet,
        token: str,
        spender: str,
        token_id: str,
        expires: Optional[dict] = None,
    ) -> SyncTxBroadcastResult:
        """Allows operator to transfer / send the token from the owner's account.
            If expiration is set, then this allowance has a time/height limit.
        Args:
            wallet (Wallet): CW721 owner wallet
            token (str): CW721 token address
            spender (str): the address who will get permission to the CW721 token
            token_id (str): token id of the CW721 token
            expires: (dict, optional) {"at_height": height(u64)} / {"at_time":timestamp(nanosecond, u64)}
        Returns:
            SyncTxBroadcastResult: Transaction Broadcast Result
        """
        execute_msg = {"approve": {"spender": spender, "token_id": token_id}}

        if expires is not None:
            execute_msg["approve"]["expires"] = expires

        funds = Coins()
        tx = await wallet.create_and_sign_tx(
            CreateTxOptions(
                msgs=[
                    MsgExecuteContract(
                        wallet.key.acc_address, token, execute_msg, funds
                    )
                ]
            )
        )
        result = await self._c.tx.broadcast_sync(tx)
        return result

    async def revoke(
        self, wallet: Wallet, token: str, spender: str, token_id: str
    ) -> SyncTxBroadcastResult:
        """Remove previously granted Approval
        Args:
            wallet (Wallet): CW721 sender wallet
            token (str): token address
            spender (str): token approved address
            token_id (str): CW721 token id
        Returns:
            SyncTxBroadcastResult: Transaction Broadcast Result
        """
        execute_msg = {"revoke": {"spender": spender, "token_id": token_id}}

        funds = Coins()
        tx = await wallet.create_and_sign_tx(
            CreateTxOptions(
                msgs=[
                    MsgExecuteContract(
                        wallet.key.acc_address, token, execute_msg, funds
                    )
                ]
            )
        )
        result = await self._c.tx.broadcast_sync(tx)
        return result

    async def approve_all(
        self, wallet: Wallet, token: str, operator: str, expires: Optional[dict] = None
    ) -> SyncTxBroadcastResult:
        """Allows operator to transfer / send any token from the owner's account.
            If expiration is set, then this allowance has a time/height limit
        Args:
            wallet (Wallet): CW721 sender wallet
            token (str): token address
            operator (str): token operator address
            expires: (dict, optional) {"at_height": height(u64)} / {"at_time":timestamp(nanosecond, u64)}
        Returns:
            SyncTxBroadcastResult: Transaction Broadcast Result
        """
        execute_msg = {"approve_all": {"operator": operator}}

        if expires is not None:
            execute_msg["approve_all"]["expires"] = expires

        funds = Coins()
        tx = await wallet.create_and_sign_tx(
            CreateTxOptions(
                msgs=[
                    MsgExecuteContract(
                        wallet.key.acc_address, token, execute_msg, funds
                    )
                ]
            )
        )
        result = await self._c.tx.broadcast_sync(tx)
        return result

    async def revoke_all(
        self,
        wallet: Wallet,
        token: str,
        operator: str,
    ) -> SyncTxBroadcastResult:
        """Remove previously granted ApproveAll permission
        Args:
            wallet (Wallet): CW721 sender wallet
            token (str): token address
            operator (str): token approved operator address
        Returns:
            SyncTxBroadcastResult: Transaction Broadcast Result
        """
        execute_msg = {"revoke_all": {"operator": operator}}

        funds = Coins()
        tx = await wallet.create_and_sign_tx(
            CreateTxOptions(
                msgs=[
                    MsgExecuteContract(
                        wallet.key.acc_address, token, execute_msg, funds
                    )
                ]
            )
        )
        result = await self._c.tx.broadcast_sync(tx)
        return result

    async def transfer_nft(
        self, wallet: Wallet, token: str, recipient: str, token_id: str
    ) -> SyncTxBroadcastResult:
        """Send CW721 token to the other address
        Args:
            wallet (Wallet): CW721 sender wallet
            token (str): token address
            recipient (str): token receiver address
            token_id (str): CW721 token id
        Returns:
            SyncTxBroadcastResult: Transaction Broadcast Result
        """
        execute_msg = {"transfer_nft": {"recipient": recipient, "token_id": token_id}}

        funds = Coins()
        tx = await wallet.create_and_sign_tx(
            CreateTxOptions(
                msgs=[
                    MsgExecuteContract(
                        wallet.key.acc_address, token, execute_msg, funds
                    )
                ]
            )
        )
        result = await self._c.tx.broadcast_sync(tx)
        return result

    async def send_nft(
        self, wallet: Wallet, token: str, contract: str, token_id: str, msg: str
    ) -> SyncTxBroadcastResult:
        """Send CW721 token to the other address and run msg
        Args:
            wallet (Wallet): CW721 sender wallet
            token (str): token address
            contract (str): token receiver address
            token_id (str): CW721 token id
            msg (str): Base64 encoded message string
        Returns:
            SyncTxBroadcastResult: Transaction Broadcast Result
        """
        execute_msg = {
            "send_nft": {"contract": contract, "token_id": token_id, "msg": msg}
        }

        funds = Coins()
        tx = await wallet.create_and_sign_tx(
            CreateTxOptions(
                msgs=[
                    MsgExecuteContract(
                        wallet.key.acc_address, token, execute_msg, funds
                    )
                ]
            )
        )
        result = await self._c.tx.broadcast_sync(tx)
        return result

    async def burn(
        self,
        wallet: Wallet,
        token: str,
        token_id: str,
    ) -> SyncTxBroadcastResult:
        """Burn CW721 token
        Args:
            wallet (Wallet): CW721 sender wallet
            token (str): CW721 token address
            token_id (str): CW721 token id
        Returns:
            SyncTxBroadcastResult: Transaction Broadcast Result
        """
        execute_msg = {"burn": {"token_id": token_id}}

        funds = Coins()
        tx = await wallet.create_and_sign_tx(
            CreateTxOptions(
                msgs=[
                    MsgExecuteContract(
                        wallet.key.acc_address, token, execute_msg, funds
                    )
                ]
            )
        )
        result = await self._c.tx.broadcast_sync(tx)
        return result


class Cw721API(AsyncCw721API):
    @sync_bind(AsyncCw721API.instantiate)
    def instantiate(
        self, wallet: Wallet, code_id: int, name: str, symbol: str, minter: str
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncCw721API.mint)
    def mint(
        self, wallet: Wallet, token: str, token_id: str, owner: str, token_uri: str
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncCw721API.approve)
    def approve(
        self,
        wallet: Wallet,
        token: str,
        spender: str,
        token_id: str,
        expires: Optional[str] = None,
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncCw721API.revoke)
    def revoke(
        self, wallet: Wallet, token: str, spender: str, token_id: str
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncCw721API.approve_all)
    def approve_all(
        self, wallet: Wallet, token: str, operator: str, expires: Optional[str] = None
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncCw721API.revoke_all)
    def revoke_all(
        self,
        wallet: Wallet,
        token: str,
        operator: str,
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncCw721API.transfer_nft)
    def transfer_nft(
        self, wallet: Wallet, token: str, recipient: str, token_id: str
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncCw721API.send_nft)
    def send_nft(
        self, wallet: Wallet, token: str, contract: str, token_id: str, msg: str
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncCw721API.burn)
    def burn(
        self,
        wallet: Wallet,
        token: str,
        token_id: str,
    ) -> SyncTxBroadcastResult:
        pass

    instantiate.__doc__ = AsyncCw721API.instantiate.__doc__
    mint.__doc__ = AsyncCw721API.mint.__doc__
    approve.__doc__ = AsyncCw721API.approve.__doc__
    revoke.__doc__ = AsyncCw721API.revoke.__doc__
    approve_all.__doc__ = AsyncCw721API.approve_all.__doc__
    revoke_all.__doc__ = AsyncCw721API.revoke_all.__doc__
    transfer_nft.__doc__ = AsyncCw721API.transfer_nft.__doc__
    send_nft.__doc__ = AsyncCw721API.send_nft.__doc__
    burn.__doc__ = AsyncCw721API.burn.__doc__
