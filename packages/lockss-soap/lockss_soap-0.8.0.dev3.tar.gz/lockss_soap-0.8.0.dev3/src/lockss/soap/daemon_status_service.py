#!/usr/bin/env python3

# Copyright (c) 2000-2023, Board of Trustees of Leland Stanford Jr. University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import zeep.exceptions
import zeep.helpers

from lockss.soap.util import _construct_query, _make_client

SERVICE = 'DaemonStatusService'


def get_au_article_urls(node_object, auid):
    """
    Retrieves the given AU's article URLs on the given node.

    Performs a `query_aus` operation selecting for ``articleUrls`` where
    ``auId`` is the given AUID.

    :param node_object: A node object returned by `lockss.soap.node`.
    :param auid: An AUID.
    :return: A list of article URLs, or ``None`` if there is no matching AUID.
    """
    res = query_aus(node_object, ['articleUrls'], where=f'auId = "{auid}"')
    return res[0].get('articleUrls', []) if len(res) > 0 else None


def get_au_status(node_object, auid):
    """
    Retrieves the given AU's status data from the given node, in the form of
    a record with these attributes:

    *  ``accessType`` (string)
    *  ``availableFromPublisher`` (boolean)
    *  ``contentSize`` (numeric)
    *  ``crawlPool`` (string)
    *  ``crawlProxy`` (string)
    *  ``crawlWindow`` (string)
    *  ``creationTime`` (numeric)
    *  ``currentlyCrawling`` (boolean)
    *  ``currentlyPolling`` (boolean)
    *  ``diskUsage`` (numeric)
    *  ``journalTitle`` (string)
    *  ``lastCompletedCrawl`` (numeric)
    *  ``lastCompletedDeepCrawl`` (numeric)
    *  ``lastCompletedDeepCrawlDepth`` (numeric)
    *  ``lastCompletedPoll`` (numeric)
    *  ``lastCrawl`` (numeric)
    *  ``lastCrawlResult`` (string)
    *  ``lastDeepCrawl`` (numeric)
    *  ``lastDeepCrawlResult`` (string)
    *  ``lastMetadataIndex`` (numeric)
    *  ``lastPoll`` (numeric)
    *  ``lastPollResult`` (string)
    *  ``pluginName`` (string)
    *  ``provider`` (string)
    *  ``publisher`` (string)
    *  ``publishingPlatform`` (string)
    *  ``recentPollAgreement`` (floating point)
    *  ``repository`` (string)
    *  ``status`` (string)
    *  ``subscriptionStatus`` (string)
    *  ``substanceState`` (string)
    *  ``volume`` (string) (the AU name)
    *  ``year`` (string)

    Performs a ``getAuStatus`` SOAP operation.

    :param node_object: A node object returned by `lockss.soap.node`.
    :param auid: An AUID.
    :return: An object (with attributes described above), or ``None`` if
        `zeep.exceptions.Fault` with ``No Archival Unit with provided
        identifier`` was raised).
    :raises zeep.exceptions.Fault: If a `zeep.exceptions.Fault` was raised
        other than one with ``No Archival Unit with provided identifier``.
    """
    try:
        client = _make_client(node_object, SERVICE)
        ret = client.service.getAuStatus(auId=auid)
        return zeep.helpers.serialize_object(ret)
    except zeep.exceptions.Fault as exc:
        if exc.message == 'No Archival Unit with provided identifier':
            return None
        else:
            raise


def get_au_substance_urls(node_object, auid):
    """
    Retrieves the given AU's substance URLs on the given node.

    Performs a `query_aus` operation selecting for ``substanceUrls`` where
    ``auId`` is the given AUID.

    :param node_object: A node object returned by `lockss.soap.node`.
    :param auid: An AUID.
    :return: A list of substance URLs, or ``None`` if there is no matching
        AUID.
    """
    res = query_aus(node_object, ['substanceUrls'], where=f'auId = "{auid}"')
    return res[0].get('substanceUrls', []) if len(res) > 0 else None


def get_au_type_urls(node_object, auid, typ):
    """
    Retrieves the given AU's article or substance URLs on the given node,
    depending on whether the ``typ`` parameter is ``articleUrls`` or
    ``substanceUrls`` respectively.

    .. warning::

       This method will become deprecated in a future release. Use
       `get_au_article_urls` or `get_au_substance_urls` instead.

    :param node_object: A node object returned by `lockss.soap.node`.
    :param auid: An AUID.
    :param typ: Either ``articleUrls`` for article URLs or ``substanceUrls``
       for substance URLs.
    :return: The result of `get_au_article_urls` for ``articleUrls`` or of
        `get_au_substance_urls` for ``substanceUrls``.
    :raises Exception: If ``typ`` is not ``articleUrls`` or ``substanceUrls``.
    """
    if typ == 'articleUrls':
        return get_au_article_urls(node_object, auid)
    elif typ == 'substanceUrls':
        return get_au_substance_urls(node_object, auid)
    else:
        raise Exception(f'invalid URL type: {typ}')


def get_au_urls(node_object, auid, prefix=None):
    """
    Retrieves the given AU's list of URLs on the given node.

    Performs a ``getAuUrls`` SOAP operation.

    :param node_object: A node object returned by `lockss.soap.node`.
    :param auid: An AUID.
    :param prefix: An optional prefix.
    :return: The AU's list of URLs (only those beginning with ``prefix`` if
        given), or ``None`` if `zeep.exceptions.Fault` with ``No Archival Unit
        with provided identifier`` was raised.
    :raises zeep.exceptions.Fault: If a `zeep.exceptions.Fault` was raised
        other than one with ``No Archival Unit with provided identifier``.
    """
    try:
        client = _make_client(node_object, SERVICE)
        ret = client.service.getAuUrls(auId=auid, url=prefix)
        return ret
    except zeep.exceptions.Fault as exc:
        if exc.message == 'No Archival Unit with provided identifier':
            return None
        else:
            raise


def get_auids(node_object):
    """
    Retrieves the given node's list of AUIDs.

    Performs a ``getAuIds`` SOAP operation.

    :param node_object: A node object returned by `lockss.soap.node`.
    :return: A list of AUIDs.
    """
    client = _make_client(node_object, SERVICE)
    ret = client.service.getAuIds()
    return zeep.helpers.serialize_object(ret)


def get_peer_agreements(node_object, auid):
    """
    Retrieves the given AU's peer agreements data on the given node, in the
    form of a record with these attributes:

    *  ``agreements``, a record with these attributes:
       *  ``entry``, a list of records with these attributes:
          *  ``key``, a string among:
             *  ``POR``
             *  ``POP``
             *  ``SYMMETRIC_POR``
             *  ``SYMMETRIC_POP``
             *  ``POR_HINT``
             *  ``POP_HINT``
             *  ``SYMMETRIC_POR_HINT``
             *  ``SYMMETRIC_POP_HINT``
             *  ``W_POR``
             *  ``W_POP``
             *  ``W_SYMMETRIC_POR``
             *  ``W_SYMMETRIC_POP``
             *  ``W_POR_HINT``
             *  ``W_POP_HINT``
             *  ``W_SYMMETRIC_POR_HINT``
             *  ``W_SYMMETRIC_POP_HINT``
          *  ``value``, a record with these attributes:
             *  ``highestPercentAgreement`` (floating point)
             *  ``highestPercentAgreementTimestamp`` (numeric)
             *  ``percentAgreement`` (floating point)
             *  ``percentAgreementTimestamp`` (numeric)
    *  ``peerId`` (string)

    Performs a `query_aus` operation selecting for ``peerAgreements`` where
    `auId`` is the given AUID.

    :param node_object: A node object returned by `lockss.soap.node`.
    :param auid: An AUID.
    :return: An object (with attributes described above), or ``None`` if no
        data is returned.
    """
    res = query_aus(node_object, ['peerAgreements'], where=f'auId = "{auid}"')
    return zeep.helpers.serialize_object(res[0]).get('peerAgreements') if len(res) > 0 else None


def get_platform_configuration(node_object):
    """
    Retrieves the given node's platform configuration data, in the form of a
    record with these attributes:

    *  ``adminEmail`` (string)
    *  ``buildHost`` (string)
    *  ``buildTimestamp`` (numeric)
    *  ``currentTime`` (numeric)
    *  ``currentWorkingDirectory`` (string)
    *  ``daemonVersion``, a record with these attributes:
       *  ``buildVersion`` (numeric)
       *  ``fullVersion`` (string)
       *  ``majorVersion`` (numeric)
       *  ``minorVersion`` (numeric)
    *  ``disks`` (list of strings)
    *  ``groups`` (list of strings)
    *  ``hostName`` (string)
    *  ``ipAddress`` (string)
    *  ``javaVersion``, a record with these attributes:
       *  ``runtimeName`` (string)
       *  ``runtimeVersion`` (string)
       *  ``specificationVersion`` (string)
       *  ``version`` (string)
    *  ``mailRelay`` (string)
    *  ``platform``, a record with these attributes:
       *  ``name`` (string)
       *  ``suffix`` (string)
       *  ``version`` (string)
    *  ``project`` (string)
    *  ``properties`` (list of strings)
    *  ``uptime`` (numeric)
    *  ``v3Identity`` (string)

    Performs a ``getPlatformConfiguration`` SOAP operation.

    :param node_object: A node object returned by `lockss.soap.node`.
    :return: An object (with attributes described above).
    """
    client = _make_client(node_object, SERVICE)
    ret = client.service.getPlatformConfiguration()
    return zeep.helpers.serialize_object(ret)


def is_daemon_ready(node_object):
    """
    Returns the given node's ready flag.

    Performs a ``isDaemonReady`` SOAP operation.

    :param node_object: A node object returned by `lockss.soap.node`.
    :return: The node's boolean ready flag.
    :rtype: bool
    """
    client = _make_client(node_object, SERVICE)
    ret = client.service.isDaemonReady()
    return ret


def query_aus(node_object, select, where=None):
    """
    Performs a query against the AUs of a given node, and returns a record with
    attributes among these:

    *  ``accessType`` (string)
    *  ``articleUrls`` (list of strings)
    *  ``auConfiguration``, a record with these attributes:
       *  ``defParams``, a list of records with these attributes:
          *  ``key`` (string)
          *  ``value`` (string)
       *  ``nonDefParams``, a list of records with these attributes:
          *  ``key`` (string)
          *  ``value`` (string)
    *  ``auId`` (string)
    *  ``availableFromPublisher`` (boolean)
    *  ``contentSize`` (numeric)
    *  ``crawlPool`` (string)
    *  ``crawlProxy`` (string)
    *  ``crawlWindow`` (string)
    *  ``creationTime`` (numeric)
    *  ``currentlyCrawling`` (boolean)
    *  ``currentlyPolling`` (boolean)
    *  ``diskUsage`` (numeric)
    *  ``highestPollAgreement`` (numeric)
    *  ``isBulkContent`` (boolean)
    *  ``journalTitle`` (string)
    *  ``lastCompletedCrawl`` (numeric)
    *  ``lastCompletedDeepCrawl`` (numeric)
    *  ``lastCompletedDeepCrawlDepth`` (numeric)
    *  ``lastCompletedPoll`` (numeric)
    *  ``lastCrawl`` (numeric)
    *  ``lastCrawlResult`` (string)
    *  ``lastDeepCrawl`` (numeric)
    *  ``lastDeepCrawlResult`` (string)
    *  ``lastMetadataIndex`` (numeric)
    *  ``lastPoll`` (numeric)
    *  ``lastPollResult`` (string)
    *  ``name`` (string)
    *  ``newContentCrawlUrls`` (list of strings)
    *  ``peerAgreements``, a list of records with these attributes:
       *  ``agreements``, a record with these attributes:
          *  ``entry``, a list of records with these attributes:
             *  ``key``, a string among:
                *  ``POR``
                *  ``POP``
                *  ``SYMMETRIC_POR``
                *  ``SYMMETRIC_POP``
                *  ``POR_HINT``
                *  ``POP_HINT``
                *  ``SYMMETRIC_POR_HINT``
                *  ``SYMMETRIC_POP_HINT``
                *  ``W_POR``
                *  ``W_POP``
                *  ``W_SYMMETRIC_POR``
                *  ``W_SYMMETRIC_POP``
                *  ``W_POR_HINT``
                *  ``W_POP_HINT``
                *  ``W_SYMMETRIC_POR_HINT``
                *  ``W_SYMMETRIC_POP_HINT``
             *  ``value``, a record with these attributes:
                *  ``highestPercentAgreement`` (floating point)
                *  ``highestPercentAgreementTimestamp`` (numeric)
                *  ``percentAgreement`` (floating point)
                *  ``percentAgreementTimestamp`` (numeric)
       *  ``peerId`` (string)
    *  ``pluginName`` (string)
    *  ``publishingPlatform`` (string)
    *  ``recentPollAgreement`` (numeric)
    *  ``repositoryPath`` (string)
    *  ``status`` (string)
    *  ``subscriptionStatus`` (string)
    *  ``substanceState`` (string)
    *  ``tdbProvider`` (string)
    *  ``tdbPublisher`` (string)
    *  ``tdbYear`` (string)
    *  ``urlStems`` (list of strings)
    *  ``urls``, a list of records with these attributes:
       *  ``currentVersionSize`` (numeric)
       *  ``pollWeight`` (floating point)
       *  ``url`` (string)
       *  ``versionCount`` (numeric)
    *  ``volume`` (string)

    Performs a ``queryAus`` SOAP operation.

    :param node_object: A node object returned by `lockss.soap.node`.
    :param select: A list of attribute names, chosen among the ones above.
    :param where: An optional query string expressed over the attribute names
        above.
    :return: A list of objects for AUs matching the ``where`` query, each
        populated with only the attributes requested in the ``select`` list.
    """
    client = _make_client(node_object, SERVICE)
    query = _construct_query(select, where)
    ret = client.service.queryAus(auQuery=query)
    return zeep.helpers.serialize_object(ret)


def query_crawls(node_object, select, where=None):
    """
    Performs a query against the crawls of a given node, and returns a record
    with attributes among these:

    *  ``auId`` (string)
    *  ``auName`` (string)
    *  ``bytesFetched`` (numeric)
    *  ``crawlKey`` (string)
    *  ``crawlStatus`` (string)
    *  ``crawlType`` (string)
    *  ``duration`` (numeric)
    *  ``linkDepth`` (numeric)
    *  ``mimeTypeCount`` (numeric)
    *  ``mimeTypes`` (list of strings)
    *  ``offSiteUrlsExcludedCount`` (numeric)
    *  ``pagesExcluded`` (list of strings)
    *  ``pagesExcludedCount`` (numeric)
    *  ``pagesFetched`` (list of strings)
    *  ``pagesFetchedCount`` (numeric)
    *  ``pagesNotModified`` (list of strings)
    *  ``pagesNotModifiedCount`` (numeric)
    *  ``pagesParsed`` (list of strings)
    *  ``pagesParsedCount`` (numeric)
    *  ``pagesPending`` (list of strings)
    *  ``pagesPendingCount`` (numeric)
    *  ``pagesWithErrors`` (list of strings)
    *  ``pagesWithErrorsCount`` (numeric)
    *  ``priority`` (numeric)
    *  ``refetchDepth`` (numeric)
    *  ``sources`` (list of strings)
    *  ``startTime`` (numeric)
    *  ``startingUrls`` (list of strings)

    Performs a ``queryCrawls`` SOAP operation.

    :param node_object: A node object returned by `lockss.soap.node`.
    :param select: A list of attribute names, chosen among the ones above.
    :param where: An optional query string expressed over the attribute names
        above.
    :return: A list of objects for crawls matching the ``where`` query, each
        populated with only the attributes requested in the ``select`` list.
    """
    client = _make_client(node_object, SERVICE)
    query = _construct_query(select, where)
    ret = client.service.queryCrawls(crawlQuery=query)
    return zeep.helpers.serialize_object(ret)


def query_polls(node_object, select, where=None):
    """
    Performs a query against the crawls of a given node, and returns a record
    with attributes among these:

    *  ``activeRepairCount`` (numeric)
    *  ``activeRepairs``, a list of records with these attributes:
       *  ``peerId`` (string)
       *  ``url`` (string)
    *  ``additionalInfo`` (string)

<xs:element maxOccurs="unbounded" minOccurs="0" name="activeRepairs" nillable="true" type="tns:repairWsResult"/>
<xs:element minOccurs="0" name="additionalInfo" type="xs:string"/>
<xs:element minOccurs="0" name="agreedUrlCount" type="xs:int"/>
<xs:element maxOccurs="unbounded" minOccurs="0" name="agreedUrls" nillable="true" type="xs:string"/>
<xs:element minOccurs="0" name="auId" type="xs:string"/>
<xs:element minOccurs="0" name="auName" type="xs:string"/>
<xs:element minOccurs="0" name="bytesHashedCount" type="xs:long"/>
<xs:element minOccurs="0" name="bytesReadCount" type="xs:long"/>
<xs:element minOccurs="0" name="completedRepairCount" type="xs:int"/>
<xs:element maxOccurs="unbounded" minOccurs="0" name="completedRepairs" nillable="true" type="tns:repairWsResult"/>
<xs:element minOccurs="0" name="deadline" type="xs:long"/>
<xs:element minOccurs="0" name="disagreedUrlCount" type="xs:int"/>
<xs:element maxOccurs="unbounded" minOccurs="0" name="disagreedUrls" nillable="true" type="xs:string"/>
<xs:element minOccurs="0" name="duration" type="xs:long"/>
<xs:element minOccurs="0" name="endTime" type="xs:long"/>
<xs:element minOccurs="0" name="errorDetail" type="xs:string"/>
<xs:element name="errorUrls">
<xs:complexType>
<xs:sequence>
<xs:element maxOccurs="unbounded" minOccurs="0" name="entry">
<xs:complexType>
<xs:sequence>
<xs:element minOccurs="0" name="key" type="xs:string"/>
<xs:element minOccurs="0" name="value" type="xs:string"/>
</xs:sequence>
</xs:complexType>
</xs:element>
</xs:sequence>
</xs:complexType>
</xs:element>
<xs:element minOccurs="0" name="hashErrorCount" type="xs:int"/>
<xs:element minOccurs="0" name="noQuorumUrlCount" type="xs:int"/>
<xs:element maxOccurs="unbounded" minOccurs="0" name="noQuorumUrls" nillable="true" type="xs:string"/>
<xs:element minOccurs="0" name="participantCount" type="xs:int"/>
<xs:element maxOccurs="unbounded" minOccurs="0" name="participants" nillable="true" type="tns:participantWsResult"/>
<xs:element minOccurs="0" name="percentAgreement" type="xs:float"/>
<xs:element minOccurs="0" name="pollKey" type="xs:string"/>
<xs:element minOccurs="0" name="pollStatus" type="xs:string"/>
<xs:element minOccurs="0" name="pollVariant" type="xs:string"/>
<xs:element minOccurs="0" name="quorum" type="xs:int"/>
<xs:element minOccurs="0" name="remainingTime" type="xs:long"/>
<xs:element minOccurs="0" name="startTime" type="xs:long"/>
<xs:element minOccurs="0" name="talliedUrlCount" type="xs:int"/>
<xs:element maxOccurs="unbounded" minOccurs="0" name="talliedUrls" nillable="true" type="xs:string"/>
<xs:element minOccurs="0" name="tooCloseUrlCount" type="xs:int"/>
<xs:element maxOccurs="unbounded" minOccurs="0" name="tooCloseUrls" nillable="true" type="xs:string"/>
<xs:element minOccurs="0" name="voteDeadline" type="xs:long"/>




    Performs a ``queryPolls`` SOAP operation.

    :param node_object: A node object returned by `lockss.soap.node`.
    :param select: A list of attribute names, chosen among the ones above.
    :param where: An optional query string expressed over the attribute names
        above.
    :return: A list of objects for polls matching the ``where`` query, each
        populated with only the attributes requested in the ``select`` list.
    """
    client = _make_client(node_object, SERVICE)
    query = _construct_query(select, where)
    ret = client.service.queryPolls(pollQuery=query)
    return zeep.helpers.serialize_object(ret)


def query_tdb_titles(*args, **kwargs):
    """
    .. warning::

       This function is deprecated and will simply raise `NotImplementedError`.

    :param args: Ignored positional arguments.
    :param kwargs: Ignored keyword arguments.
    :return: Always raises`NotImplementedError`.
    :raises NotImplementedError: Always raises`NotImplementedError`.
    """
    raise NotImplementedError('query_tdb_titles()')
