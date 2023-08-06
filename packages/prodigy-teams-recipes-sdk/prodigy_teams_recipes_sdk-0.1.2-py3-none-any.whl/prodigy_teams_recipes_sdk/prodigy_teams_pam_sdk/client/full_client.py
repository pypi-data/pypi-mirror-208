from datetime import datetime, timedelta

import httpx
import jwt

from .. import ty
from .action import Action
from .asset import Asset
from .base import BaseClient
from .broker import Broker
from .broker_path import BrokerPath
from .dataset import Dataset
from .for_cluster import ForCluster
from .group import Group
from .invitation import Invitation
from .notification import Notification
from .org import Org
from .package import Package
from .person import Person
from .project import Project
from .recipe import Recipe
from .recipeplan import RecipePlan
from .secret import Secret
from .session import Session
from .task import Task
from .user import User


class ClientCredentialsAuthRequest(ty.NamedTuple):
    token_url: str
    auth: httpx.BasicAuth
    data: ty.Dict[str, str]


class AccessTokenCredential(ty.BaseModel):
    access_token: str

    @property
    def header(self) -> ty.Dict[str, ty.Any]:
        """
        Return the JWT header dict of the `self.access_token`.
        The signature is not verified, but this allows inspection of e.g. expiration
        """
        return jwt.decode(
            self.access_token,
            algorithms=["HS256"],
            options={"verify_signature": False},
        )

    @property
    def expires_at(self) -> datetime:
        return datetime.utcfromtimestamp(self.header["exp"])

    def expires_within(self, delta: timedelta) -> bool:
        """Return True if the access token expires within `seconds` seconds."""
        return datetime.utcnow() + delta > self.expires_at

    @property
    def expired(self) -> bool:
        """Returns True if the access token has expired."""
        return self.expires_within(timedelta(seconds=5))


class Client:
    action: Action
    asset: Asset
    broker: Broker
    broker_path: BrokerPath
    dataset: Dataset
    group: Group
    invitation: Invitation
    for_cluster: ForCluster
    recipeplan: RecipePlan
    notification: Notification
    org: Org
    package: Package
    person: Person
    project: Project
    recipe: Recipe
    session: Session
    task: Task
    user: User
    secret: Secret

    def __init__(
        self,
        base_url: str,
        token: AccessTokenCredential,
        client_id: ty.Optional[str] = None,
        client_secret: ty.Optional[str] = None,
        app: ty.Optional[ty.Callable[..., ty.Any]] = None,
    ):
        self._base_url = base_url
        self._token = token
        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_headers = {"Authorization": f"Bearer {token.access_token}"}

        self._app = app
        self._sync_client = httpx.Client(
            app=app, base_url=base_url, headers=self._auth_headers
        )
        self._async_client = httpx.AsyncClient(
            app=app, base_url=base_url, headers=self._auth_headers
        )
        self._base_client = BaseClient(self._sync_client, self._async_client, "")
        self.request = self._base_client.request
        self.request_async = self._base_client.request_async
        self.action = Action(self._sync_client, self._async_client, "/api/v1/action")
        self.asset = Asset(self._sync_client, self._async_client, "/api/v1/asset")
        self.broker = Broker(self._sync_client, self._async_client, "/api/v1/broker")
        self.broker_path = BrokerPath(
            self._sync_client, self._async_client, "/api/v1/broker-path"
        )
        self.dataset = Dataset(self._sync_client, self._async_client, "/api/v1/dataset")
        self.for_cluster = ForCluster(
            self._sync_client, self._async_client, "/api/v1/for-cluster"
        )
        self.group = Group(self._sync_client, self._async_client, "/api/v1/group")
        self.invitation = Invitation(
            self._sync_client, self._async_client, "/api/v1/invitation"
        )
        self.recipeplan = RecipePlan(
            self._sync_client, self._async_client, "/api/v1/recipeplan"
        )
        self.notification = Notification(
            self._sync_client, self._async_client, "/api/v1/notification"
        )
        self.org = Org(self._sync_client, self._async_client, "/api/v1/org")
        self.package = Package(self._sync_client, self._async_client, "/api/v1/package")
        self.person = Person(self._sync_client, self._async_client, "/api/v1/person")
        self.project = Project(self._sync_client, self._async_client, "/api/v1/project")
        self.recipe = Recipe(self._sync_client, self._async_client, "/api/v1/recipe")
        self.session = Session(self._sync_client, self._async_client, "/api/v1/session")
        self.task = Task(self._sync_client, self._async_client, "/api/v1/task")
        self.user = User(self._sync_client, self._async_client, "/api/v1/user")
        self.secret = Secret(self._sync_client, self._async_client, "/api/v1/secret")

    def close(self) -> None:
        self._sync_client.close()

    async def aclose(self) -> None:
        self._sync_client.close()
        await self._async_client.aclose()

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def access_token(self) -> str:
        return self._token.access_token

    @classmethod
    def from_client_creds(
        cls, base_url: str, client_id: str, client_secret: str
    ) -> "Client":
        cred = cls._make_authorization_request(base_url, client_id, client_secret)
        return cls(
            base_url=base_url,
            token=cred,
            client_id=client_id,
            client_secret=client_secret,
        )

    @classmethod
    async def from_client_creds_async(
        cls, base_url: str, client_id: str, client_secret: str
    ) -> "Client":
        cred = await cls._make_authorization_request_async(
            base_url, client_id, client_secret
        )
        return cls(
            base_url=base_url,
            token=cred,
            client_id=client_id,
            client_secret=client_secret,
        )

    def ensure_auth(self) -> None:
        if self._token.expired and self._client_id and self._client_secret:
            cred = self._make_authorization_request(
                self._base_url, self._client_id, self._client_secret
            )
            self._update_auth(cred)

    async def ensure_auth_async(self) -> None:
        if self._token.expired and self._client_id and self._client_secret:
            cred = await self._make_authorization_request_async(
                self._base_url, self._client_id, self._client_secret
            )
            self._update_auth(cred)

    def _update_auth(self, token: AccessTokenCredential) -> None:
        self._token = token
        self._auth_headers = {"Authorization": f"Bearer {token.access_token}"}
        self._async_client.headers.update(self._auth_headers)
        self._sync_client.headers.update(self._auth_headers)

    @staticmethod
    def _make_authorization_request(
        base_url: str, client_id: str, client_secret: str
    ) -> AccessTokenCredential:
        """Send a Client Credentials Auth request to Prodigy Teams to
        receive an authorized Access Token."""
        req = Client._create_auth_req(base_url, client_id, client_secret)
        res = httpx.post(req.token_url, auth=req.auth, data=req.data)
        return Client._handle_auth_res(res)

    @staticmethod
    async def _make_authorization_request_async(
        base_url: str, client_id: str, client_secret: str
    ) -> AccessTokenCredential:
        """Send a Client Credentials Auth request to Prodigy Teams to
        receive an authorized Access Token."""
        req = Client._create_auth_req(base_url, client_id, client_secret)
        async with httpx.AsyncClient(auth=req.auth) as http_client:
            res = await http_client.post(req.token_url, data=req.data)
        return Client._handle_auth_res(res)

    @staticmethod
    def _create_auth_req(
        base_url: str, client_id: str, client_secret: str
    ) -> ClientCredentialsAuthRequest:
        token_url = f"{base_url}/api/v1/oauth/token"
        auth = httpx.BasicAuth(username=client_id, password=client_secret)
        data = {"grant_type": "client_credentials"}
        return ClientCredentialsAuthRequest(token_url=token_url, auth=auth, data=data)

    @staticmethod
    def _handle_auth_res(res: httpx.Response) -> AccessTokenCredential:
        """Send a Client Credentials Auth request to Prodigy Teams to
        receive an authorized Access Token."""
        res.raise_for_status()
        data = res.json()
        return AccessTokenCredential(access_token=data["access_token"])
