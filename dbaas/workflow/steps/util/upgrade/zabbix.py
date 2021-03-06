# -*- coding: utf-8 -*-
from dbaas_credentials.credential import Credential
from dbaas_credentials.models import CredentialType
from dbaas_zabbix import factory_for
from workflow.steps.util.base import BaseInstanceStep


class ZabbixStep(BaseInstanceStep):

    def __init__(self, instance):
        super(ZabbixStep, self).__init__(instance)

        integration = CredentialType.objects.get(type=CredentialType.ZABBIX)
        environment = self.instance.databaseinfra.environment
        credentials = Credential.get_credentials(environment, integration)

        self.zabbix_provider = factory_for(
            databaseinfra=self.instance.databaseinfra,
            credentials=credentials
        )

    def __del__(self):
        self.zabbix_provider.logout()

    def do(self):
        raise NotImplementedError

    def undo(self):
        pass


class DestroyAlarms(ZabbixStep):

    def __unicode__(self):
        return "Destroying Zabbix alarms..."

    def do(self):
        monitors = self.zabbix_provider.get_host_triggers(
            self.instance.hostname.hostname
        )
        if monitors:
            self.zabbix_provider.delete_instance_monitors(
                self.instance.hostname.hostname
            )

        monitors = self.zabbix_provider.get_host_triggers(self.instance.dns)
        if monitors:
            self.zabbix_provider.delete_instance_monitors(self.instance.dns)


class CreateAlarms(ZabbixStep):

    def __unicode__(self):
        return "Creating Zabbix alarms..."

    def do(self):
        DestroyAlarms(self.instance).do()

        self.zabbix_provider.create_instance_basic_monitors(
            self.instance.hostname
        )
        self.zabbix_provider.create_instance_monitors(self.instance)
