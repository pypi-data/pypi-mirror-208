from eossr import api


def test_get_ossr_records():
    ossr_records = api.get_ossr_records(all_versions=True)
    assert len(ossr_records) >= 12  # number of records October 01, 2021
    all_ids = [rec.data['id'] for rec in ossr_records]
    assert 5524913 in all_ids  # id of the version v0.2 of the eossr
