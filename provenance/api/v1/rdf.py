
# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
/PDP endpoint for Sios v1 API
"""

import copy
import eventlet
from oslo.config import cfg
from webob.exc import (HTTPError,
                       HTTPNotFound,
                       HTTPConflict,
                       HTTPBadRequest,
                       HTTPForbidden,
                       HTTPRequestEntityTooLarge,
                       HTTPInternalServerError,
                       HTTPServiceUnavailable)
from webob import Response
import provenance.api.v1
from provenance.common import exception
from provenance.common import utils
from provenance.common import wsgi
from provenance.openstack.common import strutils
import provenance.openstack.common.log as logging

import rdflib

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Controller(object):
    """
    WSGI controller for Policy Decision Point in Sios v1 API

    The PDP resource API is a RESTful web service for Policy Decisions. The API
    is as follows::

        POST /check -- check the Policy Decision
        POST /enforce -- check the Policy Decision to be enforced
    """

    def __init__(self):
        self.pool = eventlet.GreenPool(size=1024)

    """
    Performs query evaluation
    """
    def enforce_provquery(self, req):
        """Authorize an action against our policies"""
        try:
	    LOG.debug(_('Evaluating Policy decision for action [%s]') % req.context.action)
            pdp_decision =  self.policy_nova.enforce(req.context, req.context.action, req.context.target)
	    LOG.debug(_('The Policy decision for action [%s] is [%s]') % (req.context.action, pdp_decision))
	    return pdp_decision
        except:
	    LOG.debug(_('Exception Raised for action [%s]') % req.context.action)
	    LOG.debug(_('The Policy decision for action [%s] is [False]') % req.context.action)
            return False

class ProvenanceDataManager(object):
    
    def __init__(self):
        self.prov_graph = rdflib.Graph()
        self.prov_graph.parse("https://raw.github.com/dnguyenutsa/Prov-EAC/master/hws1.rdf", format="rdfa")
        for s, p, o in prov_graph:
	        LOG.debug(_('The Policy decision for action [%s] is [%s] and [%s]') % (s, p, o))

class Deserializer(wsgi.JSONRequestDeserializer):
    """Handles deserialization of specific controller method requests."""

    def _deserialize(self, request):
        result = {}
        return result

    def create(self, request):
        return self._deserialize(request)

    def update(self, request):
        return self._deserialize(request)


class Serializer(wsgi.JSONResponseSerializer):
    """Handles serialization of specific controller method responses."""

    def __init__(self):
        self.notifier = None

    def meta(self, response, result):
       return response

    def show(self, response, result):
        return response

    def update(self, response, result):
       return response

    def create(self, response, result):
       return response


def create_resource():
    """Resource factory method"""
    deserializer = Deserializer()
    serializer = Serializer()
    return wsgi.Resource(Controller(), deserializer, serializer)
