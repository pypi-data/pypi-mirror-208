from contribution.models import Premium
from insuree.models import InsureePolicy
from policy.models import Policy
from product.models import Product


def create_test_policy(product, insuree, link=True, valid=True, custom_props=None):
    """
    Compatibility method that only return the Policy
    """
    return create_test_policy2(product, insuree, link, valid, custom_props)[0]


def create_test_policy2(product, insuree, link=True, valid=True, custom_props=None):
    """
    Creates a Policy and optionally an InsureePolicy
    :param product: Product on which this Policy is based (or its ID)
    :param insuree: The Policy will be linked to this Insuree's family and if link is True, the InsureePolicy will
     belong to him
    :param link: if True (default), an InsureePolicy will also be created
    :param valid: Whether the created Policy should be valid (validity_to)
    :param custom_props: dictionary of custom values for the Policy, when overriding a foreign key, override the _id
    :return: The created Policy and InsureePolicy
    """
    policy = Policy.objects.create(
        **{
            "family": insuree.family,
            "product_id": product.id if isinstance(product, Product) else product,
            "status": Policy.STATUS_ACTIVE,
            "stage": Policy.STAGE_NEW,
            "enroll_date": "2019-01-01",
            "start_date": "2019-01-02",
            "validity_from": "2019-01-01",
            "effective_date": "2019-01-01",
            "expiry_date": "2039-06-01",
            "validity_to": None if valid else "2019-01-01",
            "audit_user_id": -1,
            **(custom_props if custom_props else {})
        }
    )
    if link:
        insuree_policy = InsureePolicy.objects.create(
            insuree=insuree,
            policy=policy,
            audit_user_id=-1,
            effective_date="2019-01-01",
            expiry_date="2039-06-01",
            validity_from="2019-01-01",
            validity_to=None if valid else "2019-01-01",
        )
    else:
        insuree_policy = None
    return policy, insuree_policy


def create_test_policy_with_IPs(product, insuree, valid=True, policy_props=None, IP_props=None, premium_props=None):
    """
    Creates a Policy with its related InsureePolicys for each Family member.
    :param product: Product on which this Policy is based (or its ID)
    :param insuree: The Policy will be linked to this Insuree's family
    :param valid: Whether the created Policy should be valid (validity_to)
    :param policy_props: dictionary of custom values for the Policy, when overriding a foreign key, override the _id
    :param IP_props: dictionary of custom values for the InsureePolicy, when overriding a foreign key, override the _id
    :param premium_props: dictionary of custom values for the Premium, when overriding a foreign key, override the _id
    :return: The created Policy and InsureePolicy
    """
    value = 10000.00
    default_date = "2019-01-01"
    start_date = "2019-01-02"
    expiry_date = "2039-06-01"

    policy = Policy.objects.create(
        **{
            "family": insuree.family,
            "product_id": product.id if isinstance(product, Product) else product,
            "status": Policy.STATUS_ACTIVE,
            "stage": Policy.STAGE_NEW,
            "enroll_date": default_date,
            "start_date": start_date,
            "validity_from": default_date,
            "effective_date": default_date,
            "expiry_date": expiry_date,
            "value": value,
            "validity_to": None if valid else default_date,
            "audit_user_id": -1,
            **(policy_props if policy_props else {})
        }
    )

    for member in policy.family.members.filter(validity_to__isnull=True):
        InsureePolicy.objects.create(
            **{
                "insuree": member,
                "policy": policy,
                "audit_user_id": -1,
                "effective_date": default_date,
                "expiry_date": expiry_date,
                "start_date": start_date,
                "enrollment_date": default_date,
                "validity_from": default_date,
                "validity_to": None if valid else default_date,
                **(IP_props if IP_props else {})
            }
        )

    Premium.objects.create(
        **{
            "amount": value,
            "receipt": "TEST1234",
            "pay_date": default_date,
            "pay_type": "C",
            "validity_from": default_date,
            "policy_id": policy.id,
            "audit_user_id": -1,
            "validity_to": None if valid else default_date,
            "created_date": default_date,
            **(premium_props if premium_props else {})
        }
    )

    return policy
