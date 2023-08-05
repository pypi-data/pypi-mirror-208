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

import argparse
import itertools
import sys
import traceback

import rich_argparse
import tabulate

import lockss.soap
import lockss.soap.daemon_status_service
from lockss.soap.util import _BaseCli, _csvtype, datetime_ms, _do, duration_ms, _file_lines


AU_STATUS = {
    'accessType': ('Access Type', lambda r: r.get('accessType')),
    'availableFromPublisher': ('Available from Publisher', lambda r: r.get('availableFromPublisher')),
    'contentSize': ('Content Size', lambda r: r.get('contentSize')),
    'crawlPool': ('Crawl Pool', lambda r: r.get('crawlPool')),
    'crawlProxy': ('Crawl Proxy', lambda r: r.get('crawlProxy')),
    'crawlWindow': ('Crawl Window', lambda r: r.get('crawlWindow')),
    'creationTime': ('Creation Time', lambda r: datetime_ms(r.get('creationTime'))),
    'currentlyCrawling': ('Currently Crawling', lambda r: r.get('currentlyCrawling')),
    'currentlyPolling': ('Currently Polling', lambda r: r.get('currentlyPolling')),
    'diskUsage': ('Disk Usage', lambda r: r.get('diskUsage')),
    'journalTitle': ('Journal Title', lambda r: r.get('journalTitle')),
    'lastCompletedCrawl': ('Last Completed Crawl', lambda r: datetime_ms(r.get('lastCompletedCrawl'))),
    'lastCompletedDeepCrawl': ('Last Completed Deep Crawl', lambda r: datetime_ms(r.get('lastCompletedDeepCrawl'))),
    'lastCompletedDeepCrawlDepth': ('Last Completed Deep Crawl Depth', lambda r: r.get('lastCompletedDeepCrawlDepth')),
    'lastCompletedPoll': ('Last Completed Poll', lambda r: datetime_ms(r.get('lastCompletedPoll'))),
    'lastCrawl': ('Last Crawl', lambda r: datetime_ms(r.get('lastCrawl'))),
    'lastCrawlResult': ('Last Crawl Result', lambda r: r.get('lastCrawlResult')),
    'lastDeepCrawl': ('Last Deep Crawl', lambda r: datetime_ms(r.get('lastDeepCrawl'))),
    'lastDeepCrawlResult': ('Last Deep Crawl Result', lambda r: r.get('lastDeepCrawlResult')),
    'lastMetadataIndex': ('Last Metadata Index', lambda r: datetime_ms(r.get('lastMetadataIndex'))),
    'lastPoll': ('Last Poll', lambda r: datetime_ms(r.get('lastPoll'))),
    'lastPollResult': ('Last Poll Result', lambda r: r.get('lastPollResult')),
    'pluginName': ('Plugin Name', lambda r: r.get('pluginName')),
    'provider': ('Provider', lambda r: r.get('provider')),
    'publisher': ('Publisher', lambda r: r.get('publisher')),
    'publishingPlatform': ('Publishing Platform', lambda r: r.get('publishingPlatform')),
    'recentPollAgreement': ('Recent Poll Agreement', lambda r: r.get('recentPollAgreement')),
    'repository': ('Repository', lambda r: r.get('repository')),
    'status': ('Status', lambda r: r.get('status')),
    'subscriptionStatus': ('Subscription Status', lambda r: r.get('subscriptionStatus')),
    'substanceState': ('Substance State', lambda r: r.get('substanceState')),
    'volume': ('Volume Name', lambda r: r.get('volume')),
    'year': ('Year', lambda r: r.get('year'))
}


PLATFORM_CONFIGURATION = {
    'adminEmail': ('Admin E-mail', lambda r: r.get('adminEmail')),
    'buildHost':  ('Build Host', lambda r: r.get('buildHost')),
    'buildTimestamp': ('Build Timestamp', lambda r: datetime_ms(r.get('buildTimestamp'))),
    'currentTime': ('Current Time', lambda r: datetime_ms(r.get('currentTime'))),
    'currentWorkingDirectory': ('Current Working Directory', lambda r: r.get('currentWorkingDirectory')),
    'daemonBuildVersion': ('Daemon Build Version', lambda r: r.get('daemonVersion', {}).get('buildVersion')),
    'daemonFullVersion': ('Daemon Full Version', lambda r: r.get('daemonVersion', {}).get('fullVersion')),
    'daemonMajorVersion': ('Daemon Major Version', lambda r: r.get('daemonVersion', {}).get('majorVersion')),
    'daemonMinorVersion': ('Daemon Minor Version', lambda r: r.get('daemonVersion', {}).get('minorVersion')),
    'disks': ('Disks', lambda r: '\n'.join(r.get('disks', []))),
    'groups': ('Groups', lambda r: '\n'.join(r.get('groups', []))),
    'hostName': ('Host Name', lambda r: r.get('hostName')),
    'ipAddress': ('IP Address', lambda r: r.get('ipAddress')),
    'javaRuntimeName': ('Java Runtime Name', lambda r: r.get('javaVersion', {}).get('runtimeName')),
    'javaRuntimeVersion': ('Java Runtime Version', lambda r: r.get('javaVersion', {}).get('runtimeVersion')),
    'javaSpecificationVersion': ('Java Specification Version', lambda r: r.get('javaVersion', {}).get('specificationVersion')),
    'javaVersion': ('Java Version', lambda r: r.get('javaVersion', {}).get('version')),
    'mailRelay': ('Mail Relay', lambda r: r.get('mailRelay')),
    'platformName': ('Platform Name', lambda r: r.get('platform', {}).get('name')),
    'platformSuffix': ('Platform Suffix', lambda r: r.get('platform', {}).get('suffix')),
    'platformVersion': ('Platform Version', lambda r: r.get('platform', {}).get('version')),
    'project': ('Project', lambda r: r.get('project')),
    'properties': ('Properties', lambda r: '\n'.join(r.get('properties', []))),
    'uptime': ('Uptime', lambda r: duration_ms(r.get('uptime'))),
    'v3Identity': ('V3 Identity', lambda r: r.get('v3Identity'))
}


QUERY_AUS = {
    'accessType': ('Access Type', lambda r: r.get('accessType')),
    'articleUrls': ('Article URLs', lambda r: '\n'.join(r.get('articleUrls', list()))),
    'auConfiguration': ('AU Configuration', lambda r: '<AuConfiguration>'),  # FIXME
    'auId': ('AUID', lambda r: r.get('auId')),
    'availableFromPublisher': ('Available from Publisher', lambda r: r.get('availableFromPublisher')),
    'contentSize': ('Content Size', lambda r: r.get('contentSize')),
    'crawlPool': ('Crawl Pool', lambda r: r.get('crawlPool')),
    'crawlProxy': ('Crawl Proxy', lambda r: r.get('crawlProxy')),
    'crawlWindow': ('Crawl Window', lambda r: r.get('crawlWindow')),
    'creationTime': ('Creation Time', lambda r: datetime_ms(r.get('creationTime'))),
    'currentlyCrawling': ('Currently Crawling', lambda r: r.get('currentlyCrawling')),
    'currentlyPolling': ('Currently Polling', lambda r: r.get('currentlyPolling')),
    'diskUsage': ('Disk Usage', lambda r: r.get('diskUsage')),
    'highestPollAgreement': ('Highest Poll Agreement', lambda r: r.get('highestPollAgreement')),
    'isBulkContent': ('Is Bulk Content', lambda r: r.get('isBulkContent')),
    'journalTitle': ('Title', lambda r: r.get('journalTitle')),
    'lastCompletedCrawl': ('Last Completed Crawl', lambda r: datetime_ms(r.get('lastCompletedCrawl'))),
    'lastCompletedDeepCrawl': ('Last Completed Deep Crawl', lambda r: datetime_ms(r.get('lastCompletedDeepCrawl'))),
    'lastCompletedDeepCrawlDepth': ('Last Completed Deep Crawl Depth', lambda r: r.get('lastCompletedDeepCrawlDepth')),
    'lastCompletedPoll': ('Last Completed Poll', lambda r: datetime_ms(r.get('lastCompletedPoll'))),
    'lastCrawl': ('Last Crawl', lambda r: datetime_ms(r.get('lastCrawl'))),
    'lastCrawlResult': ('Last Crawl Result', lambda r: r.get('lastCrawlResult')),
    'lastDeepCrawl': ('Last Deep Crawl', lambda r: datetime_ms(r.get('lastDeepCrawl'))),
    'lastDeepCrawlResult': ('Last Deep Crawl Result', lambda r: r.get('lastDeepCrawlResult')),
    'lastMetadataIndex': ('Last Metadata Index', lambda r: datetime_ms(r.get('lastMetadataIndex'))),
    'lastPoll': ('Last Poll', lambda r: datetime_ms(r.get('lastPoll'))),
    'lastPollResult': ('Last Poll Result', lambda r: r.get('lastPollResult')),
    'name': ('Name', lambda r: r.get('name')),
    'newContentCrawlUrls': ('New Content Crawl URLs', lambda r: '\n'.join(r.get('newContentCrawlUrls', []))),
    'peerAgreements': ('Peer Agreements', lambda r: '<PeerAgreements>'),  # FIXME
    'pluginName': ('Plugin Name', lambda r: r.get('pluginName')),
    'publishingPlatform': ('Publishing Platform', lambda r: r.get('publishingPlatform')),
    'recentPollAgreement': ('Recent Poll Agreement', lambda r: r.get('recentPollAgreement')),
    'repositoryPath': ('Repository Path', lambda r: r.get('repositoryPath')),
    'subscriptionStatus': ('Subscription Status', lambda r: r.get('subscriptionStatus')),
    'substanceState': ('Substance State', lambda r: r.get('substanceState')),
    'substanceUrls': ('Substance URLs', lambda r: '\n'.join(r.get('substanceUrls', []))),
    'tdbProvider': ('TDB Provider', lambda r: r.get('tdbProvider')),
    'tdbPublisher': ('TDB Publisher', lambda r: r.get('tdbPublisher')),
    'tdbYear': ('TDB Year', lambda r: r.get('tdbYear')),
    'urlStems': ('URL Stems', lambda r: '\n'.join(r.get('urlStems', []))),
    'urls': ('URLs', lambda r: '\n'.join(r.get('urls', []))),
    'volume': ('Volume', lambda r: r.get('volume'))
}


QUERY_CRAWLS = {
    'auId': ('AUID', lambda r: r.get('auId')),
    'auName': ('AU Name', lambda r: r.get('auName')),
    'bytesFetchedCount': ('Bytes Fetched', lambda r: r.get('bytesFetchedCount')),
    'crawlKey': ('Crawl Key', lambda r: r.get('crawlKey')),
    'crawlStatus': ('Crawl Status', lambda r: r.get('crawlStatus')),
    'crawlType': ('Crawl Type', lambda r: r.get('crawlType')),
    'duration': ('Duration', lambda r: duration_ms(r.get('duration'))),
    'linkDepth': ('Link Depth', lambda r: duration_ms(r.get('linkDepth'))),
    'mimeTypeCount': ('MIME Type Count', lambda r: duration_ms(r.get('mimeTypeCount'))),
    'mimeTypes': ('MIME Types', lambda r: '\n'.join(r.get('mimeTypes', []))),
    'offSiteUrlsExcludedCount': ('Offsite URLs Excluded', lambda r: r.get('offSiteUrlsExcludedCount')),
    'pagesExcluded': ('Excluded Pages', lambda r: '\n'.join(r.get('pagesExcluded', []))),
    'pagesExcludedCount': ('Excluded Page Count', lambda r: r.get('pagesExcludedCount')),
    'pagesFetched': ('Fetched Pages', lambda r: '\n'.join(r.get('pagesFetched', []))),
    'pagesFetchedCount': ('Fetched Page Count', lambda r: r.get('pagesFetchedCount')),
    'pagesNotModified': ('Not-Modified Pages', lambda r: '\n'.join(r.get('pagesNotModified', []))),
    'pagesNotModifiedCount': ('Not-Modified Page Count', lambda r: r.get('pagesNotModifiedCount')),
    'pagesParsed': ('Parsed Pages', lambda r: '\n'.join(r.get('pagesParsed', []))),
    'pagesParsedCount': ('Parsed Page Count', lambda r: r.get('pagesParsedCount')),
    'pagesPending': ('Pending Pages', lambda r: '\n'.join(r.get('pagesPending', []))),
    'pagesPendingCount': ('Pending Page Count', lambda r: r.get('pagesPendingCount')),
    'pagesWithErrors': ('Error Pages', lambda r: '\n'.join(x.get('url') for x in r.get('pagesWithErrors', []))),
    'pagesWithErrors:message': ('Error Page Message', lambda r: '\n'.join(x.get('message') for x in r.get('pagesWithErrors', []))),
    'pagesWithErrors:severity': ('Error Page Severity', lambda r: '\n'.join(x.get('severity') for x in r.get('pagesWithErrors', []))),
    'pagesWithErrorsCount': ('Error Page Count', lambda r: r.get('pagesWithErrorsCount')),
    'priority': ('Priority', lambda r: r.get('priority')),
    'refetchDepth': ('Refetch Depth', lambda r: r.get('refetchDepth')),
    'sources': ('Sources', lambda r: '\n'.join(r.get('sources', []))),
    'startTime': ('Start Time', lambda r: datetime_ms(r.get('startTime'))),
    'startingUrls': ('Starting URLs', lambda r: '\n'.join(r.get('startingUrls', [])))
}


QUERY_POLLS = {
    'activeRepairCount': ('Active Repair Count', lambda r: r.get('activeRepairCount')),
    'activeRepairs': ('Active Repairs', lambda r: '\n'.join(x.get('url') for x in r.get('activeRepairs', []))),
    'activeRepairs:peerId': ('Active Repair Peer ID', lambda r: '\n'.join(x.get('peerId') for x in r.get('activeRepairs', []))),
    'additionalInfo': ('Additional Info', lambda r: r.get('additionalInfo')),
    'agreedUrlCount': ('Agreed URL Count', lambda r: r.get('agreedUrlCount')),
    'agreedUrls': ('Agreed URLs', lambda r: '\n'.join(r.get('agreedUrls', []))),
    'auId': ('AUID', lambda r: r.get('auId')),
    'auName': ('AU Name', lambda r: r.get('auName')),
    'bytesHashedCount': ('Bytes Hashed', lambda r: r.get('bytesHashedCount')),
    'bytesReadCount': ('Bytes Read', lambda r: r.get('bytesReadCount')),
    'completedRepairCount': ('Completed Repair Count', lambda r: r.get('completedRepairCount')),
    'completedRepairs': ('Completed Repairs', lambda r: '\n'.join(x.get('url') for x in r.get('completedRepairs', []))),
    'completedRepairs:peerId': ('Completed Repair Peer ID', lambda r: '\n'.join(x.get('peerId') for x in r.get('completedRepairs', []))),
    'deadline': ('Deadline', lambda r: datetime_ms(r.get('deadline'))),
    'disagreedUrlCount': ('Disagreed URL Count', lambda r: r.get('disagreedUrlCount')),
    'disagreedUrls': ('Disagreed URLs', lambda r: '\n'.join(r.get('disagreedUrls', []))),
    'duration': ('Duration', lambda r: duration_ms(r.get('duration'))),
    'endTime': ('End Time', lambda r: datetime_ms(r.get('endTime'))),
    'errorDetail': ('Error Detail', lambda r: '<ErrorDetail>'), # FIXME
    'errorUrls': ('Error URLs', lambda r: '\n'.join(x.get('key') for x in r.get('errorUrls', []))),
    'errorUrls:detail': ('Error URL Detail', lambda r: '\n'.join(x.get('value') for x in r.get('errorUrls', []))), # FIXME
    'hashErrorCount': ('Hash Error Count', lambda r: r.get('hashErrorCount')),
    'noQuorumUrlCount': ('No Quorum URL Count', lambda r: r.get('noQuorumUrlCount')),
    'noQuorumUrls': ('No Quorum URLs', lambda r: '\n'.join(r.get('noQuorumUrls', []))),
    'participantCount': ('Participant Count', lambda r: r.get('participantCount')),
    'participants': ('Participants', lambda r: '\n'.join(x.get('peerId') for x in r.get('participants', []))), # FIXME
    'percentAgreement': ('Agreement', lambda r: f'{r.get("percentAgreement"):.2%}'),
    'pollKey': ('Poll Key', lambda r: r.get('pollKey')),
    'pollStatus': ('Poll Status', lambda r: r.get('pollStatus')),
    'pollVariant': ('Poll Variant', lambda r: r.get('pollVariant')),
    'quorum': ('Quorum', lambda r: r.get('quorum')),
    'remainingTime': ('Remaining Time', lambda r: duration_ms(r.get('remainingTime'))),
    'startTime': ('Start Time', lambda r: datetime_ms(r.get('startTime'))),
    'talliedUrlCount': ('Tallied URL Count', lambda r: r.get('talliedUrlCount')),
    'talliedUrls': ('Tallied URLs', lambda r: '\n'.join(r.get('talliedUrls', []))),
    'tooCloseUrlCount': ('Too Close URL Count', lambda r: r.get('tooCloseUrlCount')),
    'tooCloseUrls': ('Too Close URLs', lambda r: '\n'.join(r.get('tooCloseUrls', []))),
    'voteDeadline': ('Vote Deadline', lambda r: datetime_ms(r.get('voteDeadline')))
}


class DaemonStatusServiceCli(_BaseCli):

    PROG = 'daemonstatusservice'

    def __init__(self):
        super().__init__()
        self._auids = None

    def _get_au_status(self):
        node_objects = [lockss.soap.node(node_ref, self._get_username(), self._get_password()) for node_ref in self._get_nodes()]
        auids = self._get_auids()
        fields = self._args.select if self._args.select and len(self._args.select) > 0 else AU_STATUS.keys()
        data = dict()
        def __result_func(t, r):
            for field in fields:
                data[(*t, field)] = AU_STATUS[field][1](r)
        _do(lockss.soap.daemon_status_service.get_au_status,
            [(node_object, auid) for auid in auids for node_object in node_objects],
            __result_func,
            self._handle_exception,
            not self._args.process_pool,
            self._args.pool_size)
        print(tabulate.tabulate([[auid, *[data.get((node_object, auid, field)) for node_object, field in itertools.product(node_objects, fields)]] for auid in sorted(auids)],
                                headers=['AUID', *[f'{node_object}\n{AU_STATUS[field][0]}' for node_object, field in itertools.product(node_objects, fields)]],
                                tablefmt=self._args.output_format))

    def _get_au_urls(self):
        node_objects = [lockss.soap.node(node_ref, self._get_username(), self._get_password()) for node_ref in self._get_nodes()]
        auids = self._get_auids()
        data = dict()
        def __result_func(t, r):
            data[t] = r
        _do(lockss.soap.daemon_status_service.get_au_urls,
            [(node_object, auid) for auid in auids for node_object in node_objects],
            __result_func,
            self._handle_exception,
            not self._args.process_pool,
            self._args.pool_size)
        print(tabulate.tabulate([[auid, *['\n'.join(data.get((node_object, auid), [])) for node_object in node_objects]] for auid in sorted(auids)],
                                headers=['AUID', *[node_object for node_object in node_objects]],
                                tablefmt=self._args.output_format))

    def _get_auids(self):
        if self._auids is None:
            self._auids = list()
            self._auids.extend(self._args.auid)
            for path in self._args.auids:
                self._auids.extend(_file_lines(path))
            if len(self._auids) == 0:
                self._parser.error('list of AUIDs to process is empty')
        return self._auids

    def _get_auids_cmd(self):
        node_objects = [lockss.soap.node(node_ref, self._get_username(), self._get_password()) for node_ref in self._get_nodes()]
        data, all_auids = dict(), dict()
        def __result_func(t, r):
            for row in r:
                auid = row['id']
                all_auids.setdefault(auid, row['name'])
                data[(*t, auid)] = True
        _do(lockss.soap.daemon_status_service.get_auids,
            itertools.product(node_objects),
            __result_func,
            self._handle_exception,
            not self._args.process_pool,
            self._args.pool_size)
        names = self._args.names
        print(tabulate.tabulate([[*([auid, name] if names else [auid]), *[data.get((node_object, auid), False) for node_object in node_objects]] for auid, name in sorted(all_auids.items())],
                                headers=[*(['AUID', 'AU Name'] if names else ['AUID']), *[node_object for node_object in node_objects]],
                                tablefmt=self._args.output_format))

    def _get_platform_configuration(self):
        node_objects = [lockss.soap.node(node_ref, self._get_username(), self._get_password()) for node_ref in self._get_nodes()]
        fields = self._args.select if self._args.select and len(self._args.select) > 0 else PLATFORM_CONFIGURATION.keys()
        data = dict()
        def __result_func(t, r):
            for field in fields:
                data[(*t, field)] = PLATFORM_CONFIGURATION[field][1](r)
        _do(lockss.soap.daemon_status_service.get_platform_configuration,
            itertools.product(node_objects),
            __result_func,
            self._handle_exception,
            not self._args.process_pool,
            self._args.pool_size)
        print(tabulate.tabulate([[PLATFORM_CONFIGURATION[field][0], *[data.get((node_object, field)) for node_object in node_objects]] for field in fields],
                                headers=['Field', *[node_object.get_url() for node_object in node_objects]],
                                tablefmt=self._args.output_format))

    def _handle_exception(self, tup, exc):
        if self._args.verbose:
            traceback.print_exception(exc)
        else:
            print(f'error on {tup}: {exc}', file=sys.stderr)
        self._errors += 1

    def _is_daemon_ready(self):
        node_objects = [lockss.soap.node(node_ref, self._get_username(), self._get_password()) for node_ref in self._get_nodes()]
        data = dict()
        def __result_func(t, r):
            data[t[0]] = r
        _do(lockss.soap.daemon_status_service.is_daemon_ready,
            itertools.product(node_objects),
            __result_func,
            self._handle_exception,
            not self._args.process_pool,
            self._args.pool_size)
        print(tabulate.tabulate([[node_object, data.get(node_object)] for node_object in node_objects],
                                headers=['Node', 'Ready'],
                                tablefmt=self._args.output_format))

    def _make_option_names(self, container):
        container.add_argument('--names',
                               action='store_true',
                               help='also output AU names')

    def _make_options_auids(self, container):
        group = container.add_argument_group(title='AUID options')
        group.add_argument('--auid', '-a',
                           metavar='AUID',
                           action='append',
                           default=list(),
                           help='add %(metavar)s to the list of AUIDs to process')
        group.add_argument('--auids', '-A',
                           metavar='FILE',
                           action='append',
                           default=list(),
                           help='add the AUIDs in %(metavar)s to the list of AUIDs to process')

    def _make_options_query(self, container, choices, where=True):
        group = container.add_argument_group(title='query options')
        group.add_argument('--select', '-s',
                           metavar='CSFIELDS',
                           type=_csvtype(choices),
                           help=f'add %(metavar)s to the list of fields to output (default: output all fields; choices: {", ".join(choices)}')
        if where:
            group.add_argument('--where', '-w',
                               metavar='CLAUSE',
                               help='use the where clause %(metavar)s')

    def _make_parser(self):
        super()._make_parser()
        self._parser = argparse.ArgumentParser(prog=DaemonStatusServiceCli.PROG,
                                               formatter_class=rich_argparse.RichHelpFormatter)
        self._subparsers = self._parser.add_subparsers(title='commands',
                                                       description="Add --help to see the command's own help message.",
                                                       dest='command',
                                                       required=True,
                                                       # With subparsers, metavar is also used as the heading of the column of subcommand names
                                                       metavar='COMMAND',
                                                       # With subparsers, help is used as the heading of the column of subcommand descriptions
                                                       help='DESCRIPTION')
        self._make_option_debug_cli(self._parser)
        self._make_option_verbose(self._parser)
        self._make_parser_copyright(self._subparsers)
        self._make_parser_get_au_status(self._subparsers)
        self._make_parser_get_au_urls(self._subparsers)
        self._make_parser_get_auids(self._subparsers)
        self._make_parser_get_platform_configuration(self._subparsers)
        self._make_parser_is_daemon_ready(self._subparsers)
        self._make_parser_license(self._subparsers)
        self._make_parser_query_aus(self._subparsers)
        self._make_parser_query_crawls(self._subparsers)
        self._make_parser_query_polls(self._subparsers)
        self._make_parser_usage(self._subparsers)
        self._make_parser_version(self._subparsers)

    def _make_parser_get_au_status(self, container):
        parser = container.add_parser('get-au-status', aliases=['gas'],
                                      description='Output status information about target AUIDs.',
                                      help='output status information about target AUIDs',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._get_au_status)
        self._make_option_output_format(parser)
        self._make_options_nodes(parser)
        self._make_options_auids(parser)
        self._make_options_query(parser, AU_STATUS.keys(), where=False)
        self._make_options_job_pool(parser)

    def _make_parser_get_au_urls(self, container):
        parser = container.add_parser('get-au-urls', aliases=['gau'],
                                      description='Output URL list from target AUIDs.',
                                      help='output URL list from target AUIDs',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._get_au_urls)
        self._make_option_output_format(parser)
        self._make_options_nodes(parser)
        self._make_options_auids(parser)
        self._make_options_job_pool(parser)

    def _make_parser_get_auids(self, container):
        parser = container.add_parser('get-auids', aliases=['ga'],
                                      description='Output AUID list from nodes.',
                                      help='output AUID list from nodes',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._get_auids_cmd)
        self._make_option_names(parser)
        self._make_option_output_format(parser)
        self._make_options_nodes(parser)
        self._make_options_job_pool(parser)

    def _make_parser_get_platform_configuration(self, container):
        parser = container.add_parser('get-platform-configuration', aliases=['gpc'],
                                      description='Get the platform configuration from nodes.',
                                      help='get the platform configuration from nodes',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._get_platform_configuration)
        self._make_option_output_format(parser)
        self._make_options_nodes(parser)
        self._make_options_query(parser, PLATFORM_CONFIGURATION.keys(), where=False)
        self._make_options_job_pool(parser)

    def _make_parser_is_daemon_ready(self, container):
        parser = container.add_parser('is-daemon-ready', aliases=['idr'],
                                      description='Check if nodes are up and ready.',
                                      help='check if nodes are up and ready',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._is_daemon_ready)
        self._make_option_output_format(parser)
        self._make_options_nodes(parser)
        self._make_options_job_pool(parser)

    def _make_parser_query(self, container, option, aliases, description, help, target, query_mapping):
        parser = container.add_parser(option, aliases=aliases,
                                      description=description,
                                      help=help,
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._do_query)
        parser.set_defaults(target=target)
        parser.set_defaults(query_mapping=query_mapping)
        self._make_option_output_format(parser)
        self._make_options_nodes(parser)
        self._make_options_query(parser, query_mapping.keys())
        self._make_options_job_pool(parser)
        return parser

    def _make_parser_query_aus(self, container):
        parser = self._make_parser_query(container,
                                         'query-aus', aliases=['qa'],
                                         description='Perform a query on AUs.',
                                         help='perform a query on AUs',
                                         target=lockss.soap.daemon_status_service.query_aus,
                                         query_mapping=QUERY_AUS)

    def _make_parser_query_crawls(self, container):
        parser = self._make_parser_query(container,
                                         'query-crawls', aliases=['qc'],
                                         description='Perform a query on crawls.',
                                         help='perform a query on crawls',
                                         target=lockss.soap.daemon_status_service.query_crawls,
                                         query_mapping=QUERY_CRAWLS)

    def _make_parser_query_polls(self, container):
        parser = self._make_parser_query(container,
                                         'query-polls', aliases=['qp'],
                                         description='Perform a query on polls.',
                                         help='perform a query on polls',
                                         target=lockss.soap.daemon_status_service.query_polls,
                                         query_mapping=QUERY_POLLS)

    def _do_query(self):
        target = self._args.target
        query_mapping = self._args.query_mapping
        node_objects = [lockss.soap.node(node_ref, self._get_username(), self._get_password()) for node_ref in self._get_nodes()]
        requested_fields = self._args.select if self._args.select and len(self._args.select) > 0 else query_mapping.keys()
        select_minus_auid = list(dict.fromkeys(k.partition(':')[0] for k in requested_fields if k != 'auId'))
        select_auid_first = ['auId', *select_minus_auid]
        where = self._args.where
        data, all_auids = dict(), set()
        def __result_func(t, r):
            for row in r:
                auid = row['auId']
                all_auids.add(auid)
                for field in requested_fields:
                    data[(t[0], auid, field)] = query_mapping[field][1](row)
        _do(target,
            [(node_object, select_auid_first, where) for node_object in node_objects],
            __result_func,
            self._handle_exception,
            not self._args.process_pool,
            self._args.pool_size)
        print(tabulate.tabulate([[auid, *[data.get((node_object, auid, field)) for node_object, field in itertools.product(node_objects, requested_fields)]] for auid in sorted(all_auids)],
                                headers=['AUID', *[f'{node_object}\n{query_mapping[field][0]}' for node_object, field in itertools.product(node_objects, requested_fields)]],
                                tablefmt=self._args.output_format))


def daemon_status_service():
    DaemonStatusServiceCli().run()
