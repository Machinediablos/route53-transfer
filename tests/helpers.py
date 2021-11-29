from route53_transfer import app
from route53_transfer.app import ComparableRecord

TEST_ZONE_ID = 1
TEST_ZONE_NAME = "test.dev"
TEST_ZONE = {"id": TEST_ZONE_ID, "name": TEST_ZONE_NAME}


def diff_zone(rrset_before, rrset_after, use_upsert=False):
    return app.compute_changes(TEST_ZONE, rrset_before, rrset_after,
                               use_upsert=use_upsert)


def diff_zone_upsert(rrset_before, rrset_after):
    return diff_zone(rrset_before, rrset_after, use_upsert=True)


def to_comparable(r):
    return r if type(r) == ComparableRecord else ComparableRecord(r)


def assert_change_eq(c1: dict, c2: dict):
    assert c1["operation"] == c2["operation"], \
        f"Expected operation type to be {c2['operation']} but was {c1['operation']}"

    assert c1["zone"]["id"] == c2["zone"]["id"], \
        f"Expected zone id to be {c2['zone']['id']} but was {c1['zone']['id']}"

    assert c1["zone"]["name"] == c2["zone"]["name"], \
        f"Expected zone name to be {c2['zone']['name']} but was {c1['zone']['name']}"

    c1_record = to_comparable(c1["record"])
    c2_record = to_comparable(c2["record"])

    assert_record_eq(c1_record, c2_record)


def assert_record_eq(r1, r2):
    rd1 = r1.to_change_dict()
    rd2 = r2.to_change_dict()

    for attr in ("type", "name", "ttl", "alias_hosted_zone_id",
                 "alias_dns_name", "identifier", "weight", "region",
                 "alias_evaluate_target_health", "health_check", "failover"):
        assert rd1[attr] == rd2[attr], \
            f"Expected record {attr} to be '{rd2[attr]}' but was '{rd1[attr]}'"

    assert_resource_records_eq(r1, r2)


def assert_resource_records_eq(r1, r2):
    rr1 = r1.resource_records
    rr2 = r2.resource_records

    assert len(rr1) == len(rr2), \
        f"Expected resource_records length to be the same, but was {len(rr1)} instead of {len(rr2)}"

    for i in range(len(rr1)):
        assert rr1[i] == rr2[i], \
            "Expected resource_records element {i} to be {rr2[i]} but was {rr1[i]}"


def assert_changes_eq(cl1: list, cl2: list):
    assert len(cl1) == len(cl2), \
        f"Expected changes list length to be the same, but was {len(cl1)} instead of {len(cl2)}"

    for i in range(len(cl1)):
        assert_change_eq(cl1[i], cl2[i])

