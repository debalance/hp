import logging
import re
import requests
import subprocess

from xmpp_backends.base import EjabberdBackendBase
from xmpp_backends.base import BackendError
from xmpp_backends.ejabberd_rest import EjabberdRestBackend

log = logging.getLogger(__name__)

class EjabberdRestBackendRWTH(EjabberdRestBackend):
    def srg_create(self, groupname, domain, text, displayed):
        response = self.post('srg_create', group=groupname, host=domain, name=groupname, description=text, display=displayed)
        result = response.json()
        # result is 0
        return result

    def srg_delete(self, groupname, domain):
        response = self.post('srg_delete', group=groupname, host=domain)
        result = response.json()
        # result is 0
        return result

    def srg_get_info(self, groupname, domain):
        try:
            result = {}
            response = self.post('srg_get_info', group=groupname, host=domain)
            # result = response.json()
            # result is a JSON dict (emtpy dict if group is non-existent)
            
            # Because of a bug in the REST API we cannot use response.json()
            # workaround: call "ejabberdctl" instead!
            # Put the following in your sudoers:
            #  django ALL=(ALL) NOPASSWD: /usr/sbin/ejabberdctl srg_get_info *
            command = 'sudo ejabberdctl srg_get_info "' + groupname + '" ' + domain
            response = subprocess.getoutput(command)
            for line in response.split("\n"):
                result[(line.split("\t")[0])] = line.split("\t")[1]
            display = result['displayed_groups']
            display = re.sub('\["', '', display)
            display = re.sub('"\]', '', display)
            display = re.sub('","', "\\\\n", display)
            result['displayed_groups'] = display
        except BackendError:
            result['name'] = groupname
            result['displayed_groups'] = "Failed to fetch data."
            result['description'] = "Failed to fetch data."

        return result

    def srg_get_members(self, groupname, domain):
        response = self.post('srg_get_members', group=groupname, host=domain)
        result = response.json()
        # result is a JSON list (empty list if group is non-existent)
        return result

    def srg_list(self, domain):
        response = self.post('srg_list', host=domain)
        result = response.json()
        # result is a JSON list
        return result

    def srg_user_add(self, username, domain, groupname):
        response = self.post('srg_user_add', user=username, host=domain, group=groupname, grouphost=domain)
        result = response.json()
        # result is 0
        return result

    def srg_user_del(self, username, domain, groupname):
        response = self.post('srg_user_del', user=username, host=domain, group=groupname, grouphost=domain)
        result = response.json()
        # result is 0
        return result
