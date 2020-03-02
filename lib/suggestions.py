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

        return True