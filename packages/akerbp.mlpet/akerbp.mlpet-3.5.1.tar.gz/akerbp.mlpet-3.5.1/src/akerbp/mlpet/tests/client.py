import os

from akerbp.mlpet.utilities import get_cognite_client

CLIENT_READ = get_cognite_client(
    client_id=os.environ["COGNITE_CLIENT_ID_READ"],
    client_secret=os.environ["COGNITE_CLIENT_SECRET_READ"],
)
CLIENT_WRITE = get_cognite_client(
    client_id=os.environ["COGNITE_CLIENT_ID_WRITE"],
    client_secret=os.environ["COGNITE_CLIENT_SECRET_WRITE"],
)
