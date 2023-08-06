# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
from typing import Any
from typing import AsyncGenerator

from canonical import EmailAddress
from google.cloud.datastore import Query
from headless.ext.oauth2.models import SubjectIdentifier

from cbra.types import IModelRepository
from cbra.core.iam import ISubjectRepository
from cbra.core.iam.principalhasher import PrincipalHasher
from cbra.core.iam.models import Principal
from cbra.core.iam.models import Subject
from .datastorerepository import DatastoreRepository
from .types import IDatastoreKey


class DatastoreSubjectRepository(
    DatastoreRepository,
    ISubjectRepository,
    IModelRepository[Subject]
):
    __module__: str = 'cbra.ext.google'
    hasher: PrincipalHasher = PrincipalHasher()

    @functools.singledispatchmethod # type: ignore
    async def get(self, principal: Any) -> Subject | None:
        if principal is None: return None
        raise NotImplementedError(f'{principal.__module__}.{type(principal).__name__}')

    @get.register
    async def get_by_email(self, principal: EmailAddress) -> Subject | None:
        query = self.query('Principal')
        query.add_filter('spec.kind', '=', 'EmailAddress') # type: ignore
        query.add_filter('spec.email', '=', str(principal)) # type: ignore
        dao = await self.one(Principal, query)
        if dao is None:
            return None
        return await self.get(dao.subject)

    @get.register
    async def get_by_identifier(self, principal: SubjectIdentifier) -> Subject | None:
        query = self.query('Principal')
        query.add_filter('spec.kind', '=', 'SubjectIdentifier') # type: ignore
        query.add_filter('spec.iss', '=', principal.iss) # type: ignore
        query.add_filter('spec.sub', '=', principal.sub) # type: ignore
        dao = await self.one(Principal, query)
        if dao is None:
            return None
        return await self.get(dao.subject)

    @get.register
    async def get_by_uid(self, uid: int) -> Subject | None:
        assert isinstance(uid, int), repr(uid)
        obj = await self.get_model_by_key(Subject, uid)
        if obj is None:
            return None
        assert obj.uid is not None
        await obj.decrypt(self.keychain)
        async for principal in self.get_principals(obj.uid):
            obj.principals.add(principal)
        return obj

    async def get_principals(self, subject_id: int) -> AsyncGenerator[Principal, None]:
        query = self.query(Principal)
        query.add_filter('subject', '=', subject_id) # type: ignore
        for entity in await self.run_in_executor(query.fetch): # type: ignore
            yield Principal.parse_obj({
                **entity,
                'key': entity.key.name
            })

    async def resolve(self, identity: int | str) -> Subject | None:
        """Resolve a principal to a global subject identifier."""
        return await self.get(int(identity))

    async def find_by_principals(
        self,
        principals: list[Any]
    ) -> set[int]:
        keys = [
            self.client.key('Principal', self.hasher.hash(x)) for x in principals # type: ignore
        ]
        #for principal in principals:
        #    query = self.query(Principal)
        #    self.filter_principal(principal, query)
        #    subjects.update([
        #        int(x['subject']) async for x in self.execute(query, dict[str, int])
        #    ])
        #return subjects
        return {
            entity['subject'] # type: ignore
            for entity in await self.run_in_executor(self.client.get_multi, keys) # type: ignore
        }

    async def destroy(self, subject_id: int) -> None:
        keys = [self.client.key('Subject', subject_id)] # type: ignore
        query = self.query(Principal)
        query.add_filter('subject', '=', subject_id) # type: ignore
        query.keys_only()
        for entity in await self.run_in_executor(query.fetch): # type: ignore
            keys.append(entity.key)
        await self.run_in_executor(self.client.delete_multi, keys) # type: ignore

    async def persist(self, instance: Subject) -> Subject:
        claims = instance.claims
        if not instance.is_encypted():
            await instance.encrypt(self.keychain)
        key = await self.put(instance, exclude={'principals', 'uid'})
        assert instance.uid is not None
        await self.delete([self.model_key(x) for x in instance._removed_principals]) # type: ignore
        for principal in instance.principals:
            await self.put_principal(key, principal) # type: ignore
        
        # TODO: Code assumes no changes to this attribute.
        instance.claims = claims
        return instance

    async def put_principal(self, parent: IDatastoreKey, principal: Principal) -> None:
        key = self.client.key('Principal', principal.key) # type: ignore
        entity = self.client.entity(key) # type: ignore
        entity.update(principal.dict(exclude={'key'})) # type: ignore
        await self.run_in_executor(self.client.put, entity) # type: ignore

    @functools.singledispatchmethod
    def filter_principal(
        self,
        principal: EmailAddress | SubjectIdentifier,
        query: Query
    ) -> None:
        raise NotImplementedError(type(principal).__name__)

    @filter_principal.register
    def filter_emailaddress(
        self,
        principal: EmailAddress,
        query: Query
    ) -> None:
        query.add_filter('spec.kind', '=', 'EmailAddress') # type: ignore
        query.add_filter('spec.email', '=', str(principal)) # type: ignore

    @filter_principal.register
    def filter_subjectidentifier(
        self,
        principal: SubjectIdentifier,
        query: Query
    ) -> None:
        query.add_filter('spec.kind', '=', 'SubjectIdentifier') # type: ignore
        query.add_filter('spec.iss', '=', principal.iss) # type: ignore
        query.add_filter('spec.sub', '=', principal.sub) # type: ignore