# compose_flask/app.py
from flask import Flask
from flask import request

from slackclient import SlackClient
from lib.vault import Vault
from lib.github import Github

import os

addr = os.environ['VAULT_ADDR']
token = os.environ['VAULT_TOKEN']

class Suggestions:
    def __init__(self):
        self.vault = Vault(addr, token)
        self.github = Github()

        self.arr_token = ("xoxb", "918589458594", "931400580288", "9LrOqSiT1GEKFftbqrfRXhD4")
        self.sl_token = "-".join(self.arr_token)
        self.slack_client = SlackClient(self.sl_token)
    
    def suggest_version(self):
        versions = self.github.get_latest_releases()
        current = self.vault.get_version()
        latest = versions[0].lstrip('v')

        if not latest == current:
            # Suggestion
            self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Suggestion: Update Vault.")

            # Reason
            because = "Because: You currently have a {}, and there is an update, Version {}.".format(current, latest)
            self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text=because)
            
            # Action
            self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Action: Download")

            # Source
            text = "https://releases.hashicorp.com/vault/1.3.2/vault_1.3.2_linux_amd64.zip"
            self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text=text)

            text2 = "and install it to vaultserver1.uat.acmecorp.net, vaultserver2.uat.acmecorp.net, and vaultserver3.uat.acmecorp.net."
            self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text=text2)

            text3 = "Hashi Docs: https://www.vaultproject.io/docs/upgrading/index.html#ha-installations"
            self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text=text3)
            
            # Internal docs
            internal = "Internal docs for this: confluence.acmecorp.net/vault-upgrade-manualconfluence.acmecorp.net/vault-upgrade-ansible"
            self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text=internal)
        else:
            latest_version = 'You already have the latest version of Vault installed: {}'.format(current)
            self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text=latest_version)


        return True

    def adoption_stats(self):
        secrets_engine = len([k  for  k in self.vault.get_secrets_engine_list()])
        auth_methods = len([k  for  k in self.vault.get_auth_methods()])
        policies = len([k  for  k in self.vault.get_policies()])

        # Suggestion
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="*Adoption Stats.* :bar_chart:")
        
        # Check Logs
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Overall Adoption rate this week: Positive :arrow_up:")
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Overall Adoption rate this month: Positive :arrow_up:")
        
        # Dummy data
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Monthly BVA: $20,000 (Estimated)")
        
        # self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="New This Week:")
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="{} Auth Methods".format(auth_methods))
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="{} Policies".format(policies))
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="{} Secrets Engines".format(secrets_engine))
        
        # More Details
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="_Respond 'Adoption Details 2' for more._")
        
        return True

    def adoption_stats_detailed(self):
        
        total_entities = self.vault.get_total_entities_count().get('keys', [])

        # Suggestion
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="*Adoption Details* :bar_chart:")
        
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Total Entities: {}".format(len(total_entities)))
        # self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Change: 10%")
        
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Roles: {}".format(self.vault.get_total_roles()))
        # self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Unused: {}".format(self.vault.get_unused_roles()))
        
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Tokens: {}".format(self.vault.get_total_tokens()))
                
        return False

    def extant_leases(self):
        # Suggestion
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="*Extant Leases*")
        
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="*Tokens*")
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="{} total".format(self.vault.get_total_tokens()))
        
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="{} service tokens".format())
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="{} batch tokens".format())
        # self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="{} periodic Tokens".format(self.vault.get_auth_methods(namespace = namespace)))
        
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="*Oldest:* {}".format())
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="*Newest:* {}".format())
        
        self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="_Respond Extant Leases Detail._")

    def extant_leases_detailed(self):
        for secret_engine in secrets_engine:
            total_tokens = self.vault.get_secrets_engine_list(namespace = namespace)
            self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="{} total".format(total_tokens))

            if total_tokens > 0:
                self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Oldest: {}".format())
                self.slack_client.api_call("chat.postMessage", channel="#vaultbot", text="Newest: {}".format())
