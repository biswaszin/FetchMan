import sys
import os
import copy
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import server

initial_users_state = copy.deepcopy(server.users)
initial_products_state = copy.deepcopy(server.products)


@pytest.fixture
def client():
    server.users[:] = copy.deepcopy(initial_users_state)
    server.products[:] = copy.deepcopy(initial_products_state)
    return server.server.test_client()
