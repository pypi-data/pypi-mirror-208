"""Schema definitions."""
# Standard Modules
from enum import Enum
from typing import Callable, Dict

# Local Modules
from cofactr.helpers import identity
from cofactr.schema.flagship.offer import Offer as FlagshipOffer
from cofactr.schema.logistics.offer import Offer as LogisticsOffer
from cofactr.schema.flagship.part import Part as FlagshipPart
from cofactr.schema.flagship_v2.offer import Offer as FlagshipV2Offer
from cofactr.schema.flagship_v2.part import Part as FlagshipV2Part
from cofactr.schema.flagship_v3.part import Part as FlagshipV3Part
from cofactr.schema.flagship_v4.part import Part as FlagshipV4Part
from cofactr.schema.flagship_v5.part import Part as FlagshipV5Part
from cofactr.schema.flagship_v6.part import Part as FlagshipV6Part
from cofactr.schema.flagship_cache_v0.part import Part as FlagshipCacheV0Part
from cofactr.schema.flagship_cache_v1.part import Part as FlagshipCacheV1Part
from cofactr.schema.flagship_cache_v2.part import Part as FlagshipCacheV2Part
from cofactr.schema.flagship_cache_v3.part import Part as FlagshipCacheV3Part
from cofactr.schema.logistics.part import Part as LogisticsPart
from cofactr.schema.logistics_v2.part import Part as LogisticsV2Part
from cofactr.schema.logistics_v2.offer import Offer as LogisticsV2Offer
from cofactr.schema.logistics_v2.seller import Seller as LogisticsV2Seller
from cofactr.schema.logistics_v3.part import Part as LogisticsV3Part
from cofactr.schema.logistics_v4.part import Part as LogisticsV4Part
from cofactr.schema.flagship.seller import Seller as FlagshipSeller
from cofactr.schema.price_solver_v0.part import Part as PriceSolverV0Part
from cofactr.schema.price_solver_v1.part import Part as PriceSolverV1Part
from cofactr.schema.price_solver_v2.part import Part as PriceSolverV2Part
from cofactr.schema.price_solver_v3.part import Part as PriceSolverV3Part


class ProductSchemaName(str, Enum):
    """Product schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    FLAGSHIP_V2 = "flagship-v2"
    FLAGSHIP_V3 = "flagship-v3"
    FLAGSHIP_V4 = "flagship-v4"
    FLAGSHIP_V5 = "flagship-v5"
    FLAGSHIP_V6 = "flagship-v6"
    FLAGSHIP_CACHE_V0 = "flagship-cache-v0"
    FLAGSHIP_CACHE_V1 = "flagship-cache-v1"
    FLAGSHIP_CACHE_V2 = "flagship-cache-v2"
    FLAGSHIP_CACHE_V3 = "flagship-cache-v3"
    LOGISTICS = "logistics"
    LOGISTICS_V2 = "logistics-v2"
    LOGISTICS_V3 = "logistics-v3"
    LOGISTICS_V4 = "logistics-v4"
    PRICE_SOLVER_V0 = "price-solver-v0"
    PRICE_SOLVER_V1 = "price-solver-v1"
    PRICE_SOLVER_V2 = "price-solver-v2"
    PRICE_SOLVER_V3 = "price-solver-v3"


schema_to_product: Dict[ProductSchemaName, Callable] = {
    ProductSchemaName.FLAGSHIP: FlagshipPart,
    ProductSchemaName.FLAGSHIP_V2: FlagshipV2Part,
    ProductSchemaName.FLAGSHIP_V3: FlagshipV3Part,
    ProductSchemaName.FLAGSHIP_V4: FlagshipV4Part,
    ProductSchemaName.FLAGSHIP_V5: FlagshipV5Part,
    ProductSchemaName.FLAGSHIP_V6: FlagshipV6Part,
    ProductSchemaName.FLAGSHIP_CACHE_V0: FlagshipCacheV0Part,
    ProductSchemaName.FLAGSHIP_CACHE_V1: FlagshipCacheV1Part,
    ProductSchemaName.FLAGSHIP_CACHE_V2: FlagshipCacheV2Part,
    ProductSchemaName.FLAGSHIP_CACHE_V3: FlagshipCacheV3Part,
    ProductSchemaName.LOGISTICS: LogisticsPart,
    ProductSchemaName.LOGISTICS_V2: LogisticsV2Part,
    ProductSchemaName.LOGISTICS_V3: LogisticsV3Part,
    ProductSchemaName.LOGISTICS_V4: LogisticsV4Part,
    ProductSchemaName.PRICE_SOLVER_V0: PriceSolverV0Part,
    ProductSchemaName.PRICE_SOLVER_V1: PriceSolverV1Part,
    ProductSchemaName.PRICE_SOLVER_V2: PriceSolverV2Part,
    ProductSchemaName.PRICE_SOLVER_V3: PriceSolverV3Part,
}


class OfferSchemaName(str, Enum):
    """Offer schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    FLAGSHIP_V2 = "flagship-v2"
    LOGISTICS = "logistics"
    LOGISTICS_V2 = "logistics-v2"


schema_to_offer: Dict[OfferSchemaName, Callable] = {
    OfferSchemaName.INTERNAL: identity,
    OfferSchemaName.FLAGSHIP: FlagshipOffer,
    OfferSchemaName.FLAGSHIP_V2: FlagshipV2Offer,
    OfferSchemaName.LOGISTICS: LogisticsOffer,
    OfferSchemaName.LOGISTICS_V2: LogisticsV2Offer,
}


class OrgSchemaName(str, Enum):
    """Organization schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    LOGISTICS = "logistics"
    LOGISTICS_V2 = "logistics-v2"


schema_to_org: Dict[OrgSchemaName, Callable] = {
    OrgSchemaName.INTERNAL: identity,
    OrgSchemaName.FLAGSHIP: FlagshipSeller,
    OrgSchemaName.LOGISTICS: FlagshipSeller,
    OrgSchemaName.LOGISTICS_V2: LogisticsV2Seller,
}


class SupplierSchemaName(str, Enum):
    """Supplier schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    LOGISTICS = "logistics"
    LOGISTICS_V2 = "logistics-v2"


schema_to_supplier: Dict[SupplierSchemaName, Callable] = {
    SupplierSchemaName.INTERNAL: identity,
    SupplierSchemaName.FLAGSHIP: FlagshipSeller,
    SupplierSchemaName.LOGISTICS: FlagshipSeller,
    SupplierSchemaName.LOGISTICS_V2: LogisticsV2Seller,
}
