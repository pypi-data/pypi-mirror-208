import bpkio_api.models as m
from bpkio_api.api import BroadpeakIoApi


def model_to_endpoint(api: BroadpeakIoApi, model: type):
    match model:
        case m.SourceSparse:
            return api.sources
        case m.AssetSource | m.AssetSourceIn:
            return api.sources.asset
        case m.LiveSource | m.LiveSourceIn:
            return api.sources.live
        case m.AssetCatalogSource | m.AssetCatalogSourceIn:
            return api.sources.asset_catalog
        case m.AdServerSource | m.AdServerSourceIn:
            return api.sources.ad_server
        case m.SlateSource | m.SlateSourceIn:
            return api.sources.slate
        case m.AdInsertionService | m.AdInsertionServiceIn:
            return api.services.ad_insertion
        case m.ContentReplacementService | m.ContentReplacementServiceIn:
            return api.services.content_replacement
        case m.VirtualChannelService, m.VirtualChannelServiceIn:
            return api.services.virtual_channel
        case m.Category, m.CategoryIn:
            return api.categories
        case m.ContentReplacementSlot:
            return api.services.content_replacement.slots
        case m.VirtualChannelSlot:
            return api.services.virtual_channel.slots
        case m.Tenant:
            return api.tenants
        case m.TranscodingProfile | m.TranscodingProfileIn | m.TranscodingProfileId:
            return api.transcoding_profiles
        case m.ConsumptionData:
            return api.consumption
        case m.User:
            return api.users
        case _:
            raise Exception(f"No endpoint found for model {model.__name__}")


MODELS_OUT_IN = [
    (m.AssetSource, m.AssetSourceIn),
    (m.LiveSource, m.LiveSourceIn),
    (m.AdServerSource, m.AdServerSourceIn),
    (m.AssetCatalogSource, m.AssetCatalogSourceIn),
    (m.SlateSource, m.SlateSourceIn),
    (m.ContentReplacementService, m.ContentReplacementServiceIn),
    (m.VirtualChannelService, m.VirtualChannelServiceIn),
    (m.AdInsertionService, m.AdInsertionServiceIn),
    (m.Category, m.CategoryIn),
    (m.TranscodingProfile, m.TranscodingProfileIn),
    (m.ServiceSparse, m.ServiceIn),
    (m.SourceSparse, m.SourceIn),
]


def model_to_model_in(model: type):
    return next(i for (o, i) in MODELS_OUT_IN if o == model)
