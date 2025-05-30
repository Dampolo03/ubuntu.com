from typing import List, Dict, Optional

from webapp.shop.api.ua_contracts.primitives import (
    Contract,
    ContractItem,
    Entitlement,
    Renewal,
    Subscription,
    SubscriptionItem,
    User,
)
from webapp.shop.api.ua_contracts.models import (
    Metadata,
    ExternalID,
    Listing,
    ChannelListing,
    Product,
    OfferItem,
    Offer,
)


def parse_product(raw_product: Dict) -> Product:
    return Product(
        id=raw_product.get("id"),
        name=raw_product.get("name"),
    )


def parse_product_listing(
    raw_product_listing: Dict, raw_products: List[Dict] = None
) -> Listing:
    product = None
    raw_products = raw_products or []
    for raw_product in raw_products:
        if raw_product.get("id") == raw_product_listing.get("productID"):
            product = parse_product(raw_product)
            break

    return Listing(
        id=raw_product_listing.get("id"),
        name=raw_product_listing.get("name"),
        marketplace=raw_product_listing.get("marketplace"),
        product=product,
        price=raw_product_listing.get("price").get("value"),
        currency=raw_product_listing.get("price").get("currency"),
        status=raw_product_listing.get("status"),
        trial_days=raw_product_listing.get("trialDays"),
        period=raw_product_listing.get("period"),
    )


def parse_channel_product_listing(
    raw_product_listing: Dict, raw_products: List[Dict] = None
) -> ChannelListing:
    product = None
    raw_products = raw_products or []
    for raw_product in raw_products:
        if raw_product.get("id") == raw_product_listing.get("productID"):
            product = parse_product(raw_product)
            break

    return ChannelListing(
        id=raw_product_listing.get("id"),
        name=raw_product_listing.get("name"),
        marketplace=raw_product_listing.get("marketplace"),
        product=product,
        price=raw_product_listing.get("price").get("value"),
        currency=raw_product_listing.get("price").get("currency"),
        status=raw_product_listing.get("status"),
        metadata=raw_product_listing.get("metadata"),
        exclusion_group=raw_product_listing.get("exclusionGroup", ""),
        effective_days=raw_product_listing.get("effectiveDays"),
    )


def parse_product_listings(
    raw_product_listings: List[Dict] = None,
    raw_products: List[Dict] = None,
) -> Dict[str, Listing]:
    raw_product_listings = raw_product_listings or {}

    return {
        product_listing.get("id"): parse_product_listing(
            product_listing, raw_products
        )
        for product_listing in raw_product_listings
    }


def parse_channel_product_listings(
    raw_product_listings: List[Dict] = None,
    raw_products: List[Dict] = None,
) -> Dict[str, ChannelListing]:
    raw_product_listings = raw_product_listings or {}

    return {
        product_listing.get("id"): parse_channel_product_listing(
            product_listing, raw_products
        )
        for product_listing in raw_product_listings
    }


def parse_entitlements(
    raw_entitlements: List[Dict] = None,
) -> List[Entitlement]:
    entitlements = []
    raw_entitlements = raw_entitlements or []
    for raw_entitlement in raw_entitlements:
        affordances = raw_entitlement.get("affordances")
        obligations = raw_entitlement.get("obligations")
        is_available = raw_entitlement.get("entitled")

        support_level = None
        if affordances:
            support_level = affordances.get("supportLevel")
            is_in_beta = affordances.get("inBeta", False)

        enabled_by_default = (
            obligations.get("enableByDefault") if obligations else False
        )

        entitlement = Entitlement(
            type=raw_entitlement.get("type"),
            support_level=support_level,
            enabled_by_default=enabled_by_default,
            is_available=is_available,
            is_in_beta=is_in_beta,
        )

        entitlements.append(entitlement)

    return entitlements


def parse_renewal(raw_renewal: Dict = None) -> Renewal:
    renewal_items = raw_renewal.get("renewalItems")
    price = 0
    currency = "usd"
    number_of_machines = 0
    for item in renewal_items:
        price = price + item.get("priceTotal").get("value")
        currency = item.get("priceTotal").get("currency")
        number_of_machines = item.get("allowance").get("value")

    return Renewal(
        id=raw_renewal.get("id"),
        contract_id=raw_renewal.get("contractID"),
        actionable=raw_renewal.get("actionable"),
        status=raw_renewal.get("status"),
        start_date=raw_renewal.get("start"),
        end_date=raw_renewal.get("end"),
        new_contract_start=raw_renewal.get("newContractStart"),
        price=price,
        currency=currency,
        number_of_machines=number_of_machines,
    )


def parse_contract_items(raw_items: List[Dict] = None) -> List[ContractItem]:
    items = []
    raw_items = raw_items or []
    for raw_item in raw_items:
        raw_renewal = raw_item.get("renewal")

        item = ContractItem(
            id=raw_item.get("id"),
            contract_id=raw_item.get("contractID"),
            created_at=raw_item.get("created"),
            start_date=raw_item.get("effectiveFrom"),
            end_date=raw_item.get("effectiveTo"),
            reason=raw_item.get("reason"),
            value=raw_item.get("value"),
            product_listing_id=raw_item.get("productListingID"),
            purchase_id=raw_item.get("purchaseID"),
            subscription_id=raw_item.get("subscriptionID"),
            trial_id=raw_item.get("trialID"),
            renewal=parse_renewal(raw_renewal) if raw_renewal else None,
        )

        items.append(item)

    return items


def parse_contract(raw_contract: Dict) -> Contract:
    account_info = raw_contract.get("accountInfo")
    contract_info = raw_contract.get("contractInfo")
    raw_entitlements = contract_info.get("resourceEntitlements")
    entitlements = parse_entitlements(raw_entitlements)
    raw_items = contract_info.get("items")
    items = parse_contract_items(raw_items)

    number_of_active_machines = 0
    max_tracking_reached = False
    if "activeMachines" in contract_info:
        active_machines = contract_info["activeMachines"]
        number_of_active_machines = active_machines["activeMachines"]
        max_tracking_reached = (
            active_machines["maximumTrackingReached"]
            if "maximumTrackingReached" in active_machines
            else False
        )

    return Contract(
        id=contract_info.get("id"),
        account_id=account_info.get("id"),
        name=contract_info.get("name"),
        product_id=contract_info.get("products")[0],
        entitlements=entitlements,
        number_of_active_machines=number_of_active_machines,
        items=items,
        max_tracking_reached=max_tracking_reached,
    )


def parse_contracts(raw_contracts: Dict) -> List[Contract]:
    return [parse_contract(raw_contract) for raw_contract in raw_contracts]


def parse_subscription_items(
    subscription_id: str,
    raw_items: List[Dict] = None,
) -> List[SubscriptionItem]:
    subscription_items = []
    raw_items = raw_items or []
    for raw_item in raw_items:
        subscription_item = SubscriptionItem(
            subscription_id=subscription_id,
            product_listing_id=raw_item.get("productListing").get("id"),
            value=raw_item.get("value"),
        )

        subscription_items.append(subscription_item)

    return subscription_items


def parse_subscription(raw_subscription: Dict) -> Subscription:
    subscription_id = raw_subscription.get("subscription").get("id")
    raw_items = raw_subscription.get("purchasedProductListings")
    subscription = raw_subscription.get("subscription")

    return Subscription(
        id=subscription_id,
        account_id=subscription.get("accountID"),
        marketplace=subscription.get("marketplace"),
        period=subscription.get("period"),
        status=subscription.get("status"),
        last_purchase_id=raw_subscription.get("lastPurchaseID"),
        pending_purchases=raw_subscription.get("pendingPurchases"),
        is_auto_renewing=subscription.get("autoRenew"),
        started_with_trial=subscription.get("startedWithTrial"),
        in_trial=subscription.get("inTrial"),
        items=parse_subscription_items(subscription_id, raw_items),
    )


def parse_subscriptions(raw_subscriptions: Dict) -> List[Subscription]:
    return [
        parse_subscription(raw_subscription)
        for raw_subscription in raw_subscriptions
    ]


def parse_user(raw_user: Dict) -> User:
    user = User(
        display_name=raw_user.get("displayName"),
        name=raw_user.get("name"),
        email=raw_user.get("email"),
        id=raw_user.get("id"),
        last_login_at=raw_user.get("lastLogin"),
        first_login_at=raw_user.get("firstLogin"),
        verified=raw_user.get("verified"),
    )

    user_role_on_account = raw_user.get("userRoleOnAccount")
    if user_role_on_account:
        user.set_user_role_on_account(user_role_on_account)

    return user


def parse_users(raw_users: List) -> List[User]:
    return [parse_user(raw_user) for raw_user in raw_users]


def parse_metadata(metadata: List[Dict[str, str]]) -> List[Metadata]:
    return [Metadata(item["key"], item["value"]) for item in metadata]


def parse_external_ids(raw_external_ids: List[Dict]) -> List[ExternalID]:
    external_ids: List[ExternalID] = []
    for raw_external_id in raw_external_ids:
        external_ids.append(
            ExternalID(
                origin=raw_external_id["origin"],
                ids=raw_external_id["IDs"],
            )
        )
    return external_ids


def parse_offer_items(
    raw_offer_items: List, raw_product_listings: List
) -> List[OfferItem]:
    offer_items = []

    for raw_offer_item in raw_offer_items:
        item_listing = raw_offer_item["productListingID"]
        product_listing = [
            product_listing
            for product_listing in raw_product_listings
            if product_listing.get("id") == item_listing
        ]
        allowance = raw_offer_item.get("value")
        # total price ( price * quantity )
        price = product_listing[0].get("price").get("value") * allowance

        is_channel_offer = (
            product_listing[0].get("marketplace") == "canonical-pro-channel"
        )

        channel_item_fields = {}

        if is_channel_offer:
            channel_item_fields = {
                "currency": product_listing[0]
                .get("price", {})
                .get("currency"),
                "effectiveDays": product_listing[0].get("effectiveDays"),
                "productID": product_listing[0].get("productID"),
                "productName": product_listing[0].get("productName"),
            }

        offer_items.append(
            OfferItem(
                id=product_listing[0].get("id"),
                name=product_listing[0].get("name"),
                price=price,
                allowance=allowance,
                **channel_item_fields,
            )
        )

    return offer_items


def parse_offer(raw_offer: Dict) -> Offer:
    items = parse_offer_items(
        raw_offer.get("items", []), raw_offer.get("productListings", [])
    )
    external_ids = (
        parse_external_ids(raw_offer["externalIDs"])
        if raw_offer.get("activationAccountID") is not None
        and raw_offer["externalIDs"] is not None
        else None
    )

    metadata = (
        parse_metadata(raw_offer.get("metadata", []))
        if raw_offer.get("activationAccountID")
        else None
    )
    exclusion_group = raw_offer.get("exclusionGroup", "")

    purchase = "purchase" in raw_offer

    # Always included fields
    offer_data = {
        "id": raw_offer["id"],
        "account_id": raw_offer["accountID"],
        "marketplace": raw_offer["marketplace"],
        "created_at": raw_offer["createdAt"],
        "actionable": raw_offer["actionable"],
        "purchase": purchase,
        "total": sum(item.price for item in items),
        "items": items,
        "discount": raw_offer.get("discount"),
    }

    # Conditionally include fields related to activation_account_id
    if raw_offer.get("activationAccountID"):
        if metadata:
            channel_deal_creator_name = get_metadata_value(
                metadata, "channelDealCreatorName"
            )
            distributor_account_name = get_metadata_value(
                metadata, "distributorAccountName"
            )
            end_user_account_name = get_metadata_value(
                metadata, "endUserAccountName"
            )
            reseller_account_name = get_metadata_value(
                metadata, "resellerAccountName"
            )
            technical_contact_email = get_metadata_value(
                metadata, "technicalContactEmail"
            )
            technical_contact_name = get_metadata_value(
                metadata, "technicalContactName"
            )
            opportunity_number = get_metadata_value(
                metadata, "opportunityNumber"
            )

        offer_data.update(
            {
                "activation_account_id": raw_offer.get("activationAccountID"),
                "can_change_items": raw_offer.get("canChangeItems"),
                "external_ids": external_ids,
                "channel_deal_creator_name": channel_deal_creator_name,
                "distributor_account_name": distributor_account_name,
                "reseller_account_name": reseller_account_name,
                "end_user_account_name": end_user_account_name,
                "technical_contact_email": technical_contact_email,
                "technical_contact_name": technical_contact_name,
                "opportunity_number": opportunity_number,
                "exclusion_group": exclusion_group,
            }
        )

    return Offer(**offer_data)


def parse_offers(raw_offers: List) -> List[Offer]:
    return [parse_offer(raw_offer) for raw_offer in raw_offers]


def get_metadata_value(
    metadata: Optional[List[Metadata]], key: str
) -> Optional[str]:
    if metadata is not None:
        for metadata in metadata:
            if metadata.key == key:
                return metadata.value
    return None
