import os
import boto3
import json
import pymysql
from fastapi import Depends, Header, HTTPException, APIRouter
from gaiaframework.base.server.cache.cache import Cache
from gaiaframework.base.server.cache.cache_utils import CacheProvider, CacheFacade

class DS_Server():
    router = APIRouter()

    debug = False
    mysql_db = None
    mysql_creds = None
    company = None
    baseDependencies = []
    x_token = ""

    ## Initialize caching - turned off by default
    ## To enable caching change cache_type to Cache.Type.REDIS
    cache_type = Cache.Type.NONE
    cache = CacheProvider.get_cache(cache_type)
    cache_facade = CacheFacade(cache, cache_type)

    def __init__(self, x_token="fake-super-secret-token", verify_x_token=False, verify_company_token=False, debug=False):
        self.x_token = x_token
        self.debug = debug
        if verify_x_token:
            self.baseDependencies.append(Depends(self.get_token_header))

        if verify_company_token:
            self.baseDependencies.append(Depends(self.get_gaia_company))

        self.router.add_api_route("/livenessprobe", self.liveness_probe, methods=["GET"], dependencies=self.baseDependencies)
        self.router.add_api_route("/readinessprobe", self.readiness_probe, methods=["GET"], dependencies=self.baseDependencies)
        pass

    async def get_gaia_company(self, Authorization: str = Header(None), GAIA_AI_TOKEN: str = Header(None, alias="GAIA-AI-TOKEN")):
        self.company = None
        gaia_ai_token = None
        if GAIA_AI_TOKEN:
            gaia_ai_token = GAIA_AI_TOKEN
        elif Authorization:
            try:
                scheme, token = Authorization.split()
                if scheme.lower() == "bearer":
                    gaia_ai_token = token
            except:
                pass
        if not gaia_ai_token:
            raise HTTPException(status_code=401, detail="Unauthorized")
        else:
            self.get_company_by_token(gaia_ai_token)
            if not self.company:
                raise HTTPException(status_code=401, detail="Unauthorized")

    async def get_token_header(self, x_token: str = Header(...)):
        if x_token != self.x_token:
            raise HTTPException(status_code=400, detail="X-Token header invalid")

    async def verify_env(self):
        # Don't allow usage of an endpoint on production environment
        if os.environ.get('SPRING_PROFILES_ACTIVE') == 'production':
            raise HTTPException(status_code=404, detail="Endpoint not available")

    def extract_host_and_service_account(self, request):
        x_forwarded_for = request.headers.get('x-forwarded-for')
        x_goog_authenticated_user_email = request.headers.get('x-goog-authenticated-user-email')
        service_account = ''
        host = ''
        try:
            if x_goog_authenticated_user_email:
                service_account = x_goog_authenticated_user_email.replace('accounts.google.com:', '')
            if x_forwarded_for:
                host = x_forwarded_for
        except Exception as e:
            print(f'Attempt to get headers from: {request.headers} failed. Error: {e}')
            pass
        return host, service_account

    def liveness_probe(self):
        return {"alive": True}

    def readiness_probe(self):
        return {"ready": True}

    def get_from_secret_manager(self, profile_name, secret):

        # Create a Secrets Manager client
        if self.debug:
            print(f'getting creds from secretsmanager for {profile_name} with {secret}')
        session = boto3.Session(profile_name=profile_name)
        # region = session.region_name
        client = session.client(service_name='secretsmanager')

        # Get the secret value
        response = client.get_secret_value(SecretId=secret)

        # Parse the secret value as JSON and extract the credentials
        secret_dict = json.loads(response['SecretString'])
        if self.debug:
            print(f'got creds from secretsmanager for {profile_name} with {secret}', secret_dict)
        return secret_dict

    def get_mysql_creds(self, profile_name, secret):
        self.mysql_creds = self.get_from_secret_manager(profile_name, secret)
    def mysql_connect(self, host, user, password, database):
        try:
            self.mysql_db = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if self.debug:
                print(f'mysql_connect SUCCESS to db {database} on host {host}')
        except Exception as e:
            if self.debug:
                print('ERROR mysql connect', str(e))

    def run_mysql_query(self, query):
        results = None
        cursor = None
        try:
            cursor = self.mysql_db.cursor()
            cursor.execute(query)
            # Fetch the results and convert to list of JSON objects
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            # json_results = json.dumps(results)
            if self.debug:
                print('results', results)
        except Exception as e:
            if self.debug:
                print('ERROR run_mysql_query', e)
        if cursor:
            cursor.close()
        return results

    def get_company_by_token(self, api_token=''):
        res = self.run_mysql_query(f"SELECT * FROM new_app_company where api_token='{api_token}'")
        if res and len(res):
            self.company = res[0]
        if self.debug:
            print('self.company', self.company)
