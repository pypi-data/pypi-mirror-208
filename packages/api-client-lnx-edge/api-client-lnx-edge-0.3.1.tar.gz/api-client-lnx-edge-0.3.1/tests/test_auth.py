from src.edge_api_client import EdgeAPI


def test_valid_api_key():
    edge = EdgeAPI()
    resp = edge.get_affiliates()

    assert resp.status_code == 200


def test_invalid_api_key():
    edge = EdgeAPI()
    resp = edge.get_affiliates(headers={'X-Edge-Key': 'not_a_real_api_key'})

    assert resp.status_code == 403
