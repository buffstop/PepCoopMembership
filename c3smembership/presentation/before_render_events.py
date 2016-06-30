# -*- coding: utf-8 -*-

from c3smembership.git_tools import GitTools
import os
from pyramid.events import (
    subscriber,
    BeforeRender
)


# TODO: Version and message information must not be attached to all dictionary
# returning routes. Routes which only return json for auto completion must not
# contain this information. Find a proper mechanism to attach messages and
# versioning information to all necessary routes but not to all.


excluded_routes = [
    'autocomplete_input_values',
    'autocomplete_people_search',
    'get_member',
]


@subscriber(BeforeRender)
def message_before_render(event):
    if type(event.rendering_val) == dict:
        request = event.get('request')
        if request.matched_route is not None \
                and request.matched_route.name not in excluded_routes:
            message = ''
            if 'message' in event['request'].GET:
                message = event['request'].GET['message']
            event.rendering_val['message'] = message


@subscriber(BeforeRender)
def version_before_render(event):
    if type(event.rendering_val) == dict:
        request = event.get('request')
        if request.matched_route is not None \
                and request.matched_route.name not in excluded_routes:
            version_number = open(os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                '../../',
                'VERSION')).read()
            version_location_url = None
            version_location_name = None
            # retrieving git information is expensive and therefore only displayed in
            # development mode
            if 'c3smembership.runmode' in event['request'].registry.settings and \
                    event['request'].registry.settings['c3smembership.runmode'] == 'dev':
                git_tag = GitTools.get_tag()
                branch_name = GitTools.get_branch()
                version_metadata = [u'Version {0}'.format(version_number)]
                if git_tag is not None:
                    version_metadata.append(u'Tag {0}'.format(git_tag))
                if branch_name is not None:
                    version_metadata.append(u'Branch {0}'.format(branch_name))
                version_information = ', '.join(version_metadata)
                version_location_name = GitTools.get_commit_hash()
                version_location_url = GitTools.get_github_commit_url()
            else:
                version_information = u'Version {0}'.format(version_number)
            event.rendering_val['version_information'] = version_information
            event.rendering_val['version_location_name'] = version_location_name
            event.rendering_val['version_location_url'] = version_location_url
