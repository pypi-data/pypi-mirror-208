# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import base64
import hashlib

from typing import Any
from .itokensigner import ITokenSigner
from .signable import Signable


class SignableOIDCToken(Signable):
    __module__: str = 'cbra.ext.oauth2.types'
    access_token: str | None = None
    authorization_code: str | None = None
    claims: dict[str, Any]

    async def sign(self, signer: ITokenSigner) -> str:
        # TODO: This must be updated in the ckms module to have a key
        # return the actual hashing algorithm, if any.
        claims = dict(self.claims)
        digestargs: list[Any] = []
        length: int
        try:
            if signer.alg != 'EdDSA':
                hasher = hashlib.new(f'sha{int(signer.alg[2:5])}')
                length = hasher.digest_size
            elif signer.crv == 'Ed25519':
                hasher = hashlib.new('sha512')
                length = hasher.digest_size
            elif signer.crv == 'Ed448':
                hasher = hashlib.new('shake_256')
                length = 114
                digestargs = [length]
            else:
                raise ValueError
        except ValueError:
            raise NotImplementedError(f"Unsupported algorithm: {signer.alg}")
        if self.access_token is not None:
            hasher.update(str.encode(self.access_token))
            digest = hasher.digest(*digestargs)
            claims['at_hash'] = base64.urlsafe_b64encode(digest[:int(length/2)])
        if self.authorization_code is not None:
            hasher.update(str.encode(self.authorization_code))
            digest = hasher.digest(*digestargs)
            claims['c_hash'] = base64.urlsafe_b64encode(digest[:int(length/2)])
        return await signer.jwt(
            claims=claims,
            typ='jwt'
        )