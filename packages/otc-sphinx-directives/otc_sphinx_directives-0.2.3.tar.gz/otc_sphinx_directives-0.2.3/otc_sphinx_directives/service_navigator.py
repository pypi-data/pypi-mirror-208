# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from docutils import nodes

from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from sphinx.util import logging

import otc_metadata.services

LOG = logging.getLogger(__name__)

METADATA = otc_metadata.services.Services()


class service_navigator(nodes.General, nodes.Element):
    pass


class ServiceNavigator(Directive):
    node_class = service_navigator
    option_spec = {
        'class': directives.unchanged,
        'environment': directives.unchanged_required
    }

    has_content = False

    def run(self):
        node = self.node_class()
        node['environment'] = self.options.get('environment', 'public')
        node['class'] = self.options.get('class', 'navigator-container')
        return [node]


def service_navigator_html(self, node):
    # This method renders containers of service groups with links to the
    # document of the specified type
    data = f'<div class="{node["class"]} container-docsportal">'

    for cat in METADATA.service_categories:
        category = cat["name"]
        category_title = cat["title"]
        data += (
            f'<div class="card item-docsportal">'
            f'<div class="card-body">'
            f'<h5 class="card-title">{category_title}</h5></div>'
            f'<ul class="list-group list-group-flush">'
        )

        for service in METADATA.services_by_category(category=category):
            title = service['service_title']
            link = service['service_uri']
            if link:
                if (link[:-1] != '/'):
                    link = link + '/index.html'
                else:
                    link = link + 'index.html'
            img = service['service_type']
            environment = service['environment']
            if environment == "hidden":
                continue
            if environment == "internal" and node['environment'] != "internal":
                continue
            data += (
                f'<li class="list-group-item"><a href="{link}">'
                f'<div class="row">'
                f'<div class="col-2">'
                f'<img src="_static/images/services/{img}.svg">'
                f'</div>'
                f'<div class="col-10">{title}</div>'
                f'</div></a></li>'
            )

        data += '</ul></div>'

    data += '</div>'

    self.body.append(data)
    raise nodes.SkipNode
