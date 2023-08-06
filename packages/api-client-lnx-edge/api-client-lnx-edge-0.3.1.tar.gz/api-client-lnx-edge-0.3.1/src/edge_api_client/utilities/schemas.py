import enum

import marshmallow


class StatusEnum(enum.Enum):
    Active = 'Active'
    Inactive = 'Inactive'
    SubOfferOnly = 'SubOfferOnly'


class ViewabilityEnum(enum.Enum):
    ApplyToRun = 'ApplyToRun'
    Testing = 'Testing'
    Private = 'Private'
    Public = 'Public'
    Archived = 'Archived'


class PixelBehaviorEnum(enum.Enum):
    dedupe = 'dedupe'
    replace = 'replace'
    incrementConvAndRev = 'incrementConvAndRev'
    incrementRevOnly = 'incrementRevOnly'


class TrafficTypesEnum(enum.Enum):
    Email = 'Email'
    Contextual = 'Contextual'
    Display = 'Display'
    Search = 'Search'
    Social = 'Social'
    Native = 'Native'
    MobileAds = 'MobileAds'


class CreateOfferSchema(marshmallow.Schema):
    friendlyName = marshmallow.fields.Str(required=True)
    category = marshmallow.fields.Int(required=True)
    description = marshmallow.fields.Str()
    domain = marshmallow.fields.Int(required=True)
    customFallbackUrl = marshmallow.fields.Str(required=True)
    filterFallbackUrl = marshmallow.fields.Str(required=True)
    filterFallbackProduct = marshmallow.fields.Int(required=True)
    dayparting = marshmallow.fields.Dict()
    filters = marshmallow.fields.Dict()
    destination = marshmallow.fields.Dict(required=True)
    status = marshmallow.fields.Enum(enum=StatusEnum, required=True)
    viewability = marshmallow.fields.Enum(enum=ViewabilityEnum, required=True)
    scrub = marshmallow.fields.Int()
    defaultAffiliateConvCap = marshmallow.fields.Int(allow_none=True)
    lifetimeAffiliateClickCap = marshmallow.fields.Int(allow_none=True)
    trafficTypes = marshmallow.fields.List(marshmallow.fields.Enum(enum=TrafficTypesEnum))
    pixelBehavior = marshmallow.fields.Enum(enum=PixelBehaviorEnum, dump_default=PixelBehaviorEnum.dedupe)
    allowQueryPassthrough = marshmallow.fields.Bool(dump_default=False)
    allowPageviewPixel = marshmallow.fields.Bool(dump_default=False)
    allowForcedClickConversion = marshmallow.fields.Bool(dump_default=False)
    creatives = marshmallow.fields.List(marshmallow.fields.Int())
    unsubscribe_link = marshmallow.fields.Str()
    suppression_list = marshmallow.fields.Str()
    from_lines = marshmallow.fields.Str()
    subject_lines = marshmallow.fields.Str()
    redirectOffer = marshmallow.fields.Int(allow_none=True)
    redirectPercent = marshmallow.fields.Float(allow_none=True)
    capRedirectOffer = marshmallow.fields.Int(allow_none=True)
