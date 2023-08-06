"ssb api"

import logging
from datetime import datetime
import requests # type: ignore
from dwh_oppfolging.apis.ssb_api_v1_types import Version, VersionHeader, Correspondence, CorrespondenceHeader, Classification

API_VERSION = 1
API_NAME = "SSB"
SEKTOR_ID = 39
NAERING_ID = 6
YRKESKATALOG_ID = 145
YRKESKLASSIFISERING_ID = 7
ORGANISASJONSFORM_ID = 35

_BASE_URL = (
    f"https://data.ssb.no/api/klass/v{API_VERSION}"  # classifications/{0}/changes"
)
_HEADERS = {"Accept": "application/json;charset=UTF-8"}
#_VALID_DATE_FMT = "%Y-%m-%d"
#_MODIFIED_DATE_FMT = "%Y-%m-%dT%H:%M:%S.%f%z"


#def _convert_ssb_date(date: str | None, fmt: str, force_):
#    """converts ssb date string to datetime"""
#    if date is None:
#        return None
#    converted_date = string_to_naive_norwegian_datetime(datetime.strptime(date, fmt).isoformat())
#    return converted_date


#def _build_version_struct(data: dict):
#    """returns version struct"""
#    url = data["_links"]["self"]["href"]
#    version_id = int(url[url.rindex("/") + 1 :])
#    version = Version(
#        url,
#        version_id,
#        _convert_ssb_date(data["validFrom"], _VALID_DATE_FMT),
#        _convert_ssb_date(data.get("validTo"), _VALID_DATE_FMT),
#        _convert_ssb_date(data["lastModified"], _MODIFIED_DATE_FMT),
#    )
#    return version


#def _build_correspondence_struct(data: dict):
#    """returns correspondence struct"""
#    url = data["_links"]["self"]["href"]
#    correspondence_id = int(url[url.rindex("/") + 1 :])
#    corr = Correspondence(
#        url,
#        correspondence_id,
#        int(data["sourceId"]),
#        int(data["targetId"]),
#        _convert_ssb_date(data["lastModified"], _MODIFIED_DATE_FMT),
#    )
#    return corr


#def _build_versioned_classification_code_record(
#    classification_id: int,
#    version: Version,
#    classification_item: dict,
#    download_date: datetime,
#):
#    """returns row dict form that can be inserted into table"""
#    record: dict = {}
#    record["klassifikasjon_id"] = classification_id
#    record["versjon_id"] = version.version_id
#    record["gyldig_fom_tid_kilde"] = version.valid_from
#    record["gyldig_til_tid_kilde"] = version.valid_to
#    record["oppdatert_tid_kilde"] = version.last_modified
#    record["api_versjon"] = API_VERSION
#    record["data"] = json_to_string(classification_item)
#    record["sha256_hash"] = string_to_sha256_hash(record["data"])
#    record["lastet_dato"] = download_date
#    record["kildesystem"] = API_NAME
#    return record


#def _build_correspondence_code_record(
#    source_classification_id: int,
#    target_classification_id: int,
#    corr: Correspondence,
#    correspondence_map: dict,
#    download_date: datetime,
#):
#    """returns row dict form that can be inserted into table"""
#    record: dict = {}
#    record["fra_klassifikasjon_id"] = source_classification_id
#    record["fra_versjon_id"] = corr.source_version_id
#    record["til_klassifikasjon_id"] = target_classification_id
#    record["til_versjon_id"] = corr.target_version_id
#    record["oppdatert_tid_kilde"] = corr.last_modified
#    record["api_versjon"] = API_VERSION
#    record["data"] = json_to_string(correspondence_map)
#    record["sha256_hash"] = string_to_sha256_hash(record["data"])
#    record["lastet_dato"] = download_date
#    record["kildesystem"] = API_NAME
#    return record


def _get_all_versions_for_classification(classification_id: int):
    """returns list of classification version metadata"""
    url = _BASE_URL + "/classifications/" + str(classification_id)
    resp = requests.get(url, headers=_HEADERS, proxies={}, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    versions = [VersionHeader.from_json(entry) for entry in data["versions"]]

    if len(versions) == 0:
        logging.info(f"found no versions for classification {classification_id}")
    else:
        logging.info(f"found versions {[v.version_id for v in versions]} for classification {classification_id}")

    return versions


def _get_all_correspondences_for_classification_version(version_header: VersionHeader):
    """gets corrspondance tables, a bit heavy since the api doesnt support
    listing the correspondence tables in the ../classification/<id> response
    instead they are only available in the /version/ endpoint,
    which means we are forced to download version with all its classification codes
    even when we will not need them...
    """
    resp = requests.get(version_header.url, headers=_HEADERS, proxies={}, timeout=10)
    data = resp.json()
    corrs = [
        CorrespondenceHeader.from_json(entry) for entry in data["correspondenceTables"]
    ]

    if len(corrs) == 0:
        logging.info(f"found no correspondences for version {version_header.version_id}")
    else:
        logging.info(f"found correspondence {[c.target_version_id for c in corrs]} for version {version_header.version_id}")

    return corrs


def _get_all_records_in_classification_version(
    classification_id: int, version_header: VersionHeader, download_date: datetime
):
    """returns list of codes as records for given version of classification"""
    resp = requests.get(version_header.url, headers=_HEADERS, proxies={}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    version = Version.from_json(data, classification_id)
    records = version.to_records(API_VERSION, API_NAME, download_date)
    logging.info(f"found {len(records)} records for version {version.version_id}")
    return records


def _get_all_records_in_correspondence(
    source_classification_id: int,
    target_classification_id: int,
    corr_header: CorrespondenceHeader,
    download_date: datetime,
):
    """returns list of correspondence-codes as records for given correspondence"""
    resp = requests.get(corr_header.self_url, headers=_HEADERS, proxies={}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    corr = Correspondence.from_json(data, source_classification_id, target_classification_id)
    records = corr.to_records(API_VERSION, API_NAME, download_date)
    return records


def get_latest_records_for_classification(
    download_date: datetime,
    last_modified_date: datetime,
    classification_id: int,
):
    """
    Yields codes for each classification version in row-dict form newer than `last_modified_date`.
    Note: the SSB api exposes only modified dates at version -level, not for each code.
    """
    for version in _get_all_versions_for_classification(classification_id):
        if not version.last_modified > last_modified_date:
            logging.info(f"skipping too old version last modified on {version.last_modified}")
            continue
        yield _get_all_records_in_classification_version(classification_id, version, download_date)


def get_latest_records_for_correspondance(
    download_date: datetime,
    last_modified_date: datetime,
    source_classification_id: int,
    target_classification_id: int,
):
    """
    Yields codes for each correspondance between source and target, for all versions.
    Note: the SSB api exposes only modified dates at correspondance-level, not for each code.
    """

    logging.info(f"looking for versions implementing source classification {source_classification_id}")
    source_versions = _get_all_versions_for_classification(source_classification_id)

    logging.info(f"looking for versions implementing target classification {target_classification_id}")
    target_versions = _get_all_versions_for_classification(target_classification_id)
    target_version_ids = set(targ.version_id for targ in target_versions)

    for src in source_versions:
        logging.info(f"looking for correspondence tables in version {src.version_id} of source classification {source_classification_id}")
        for corr in _get_all_correspondences_for_classification_version(src):
            if not corr.target_version_id in target_version_ids:
                logging.info("skipping correspondence to unknown target classification")
                continue
            if not corr.last_modified > last_modified_date:
                logging.info(
                    f"skipping too old correspondence last modified on {corr.last_modified}",
                )
                continue
            yield _get_all_records_in_correspondence(
                source_classification_id,
                target_classification_id,
                corr,
                download_date
                )


def get_latest_records_for_classification_metadata(download_date: datetime, last_modified_date: datetime, classification_id: int):
    """returns information about the SSB classification"""
    url = _BASE_URL + "/classifications/" + str(classification_id)
    resp = requests.get(url, headers=_HEADERS, proxies={}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    classification = Classification.from_json(data)
    records = []
    for version_header in classification.versions:
        resp = requests.get(version_header.url, headers=_HEADERS, proxies={}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        version = Version.from_json(data, classification_id)
        if version.last_modified > last_modified_date:
            records.append(version.to_metadata_record(API_VERSION, API_NAME, download_date))
    yield records
