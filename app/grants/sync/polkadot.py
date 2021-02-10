import json
import logging
from datetime import datetime

from django.conf import settings
from django.utils import timezone

import requests
from grants.sync.helpers import record_contribution_activity

logger = logging.getLogger(__name__)


def get_polkadot_txn_status(contribution, network='mainnet'):
    txnid = contribution.tx_id
    if not txnid or txnid == "0x0":
        return None

    subscription = contribution.subscription
    token_symbol = subscription.token_symbol

    if subscription.tenant not in ['POLKADOT', 'KUSAMA'] :
        return None

    if token_symbol not in ['DOT', 'KSM']:
        return None

    response = {
        'status': 'pending'
    }

    try:
        if token_symbol in ['DOT', 'KSM']:
            response = fetch_from_polkascan(token_symbol, txnid)
        elif token_symbol in ['EDG']:
            response = fetch_from_subscan(token_symbol, txnid)
    except Exception as e:
        logger.error(f'error: get_polkadot_txn_status - {e}')
    finally:
        return response


def fetch_from_polkascan(token_symbol, txnid):

    response = { 'status': 'pending' }

    if token_symbol == 'DOT':
        polkascan_url = f'https://explorer-31.polkascan.io/polkadot/api/v1/extrinsic/{txnid}'
    elif token_symbol == 'KSM':
        polkascan_url = f'https://explorer-31.polkascan.io/kusama/api/v1/extrinsic/{txnid}'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0. 2272.118 Safari/537.36.'}
    polkascan_response = requests.get(polkascan_url, headers=headers).json()

    if polkascan_response:
        status = polkascan_response.get('data').get('attributes')

        if status.get('success') == 1:
            response = { 'status': 'done'}
        elif status.get('error') == 1:
            response = { 'status': 'expired' }
        return response


def fetch_from_subscan(token_symbol, txnid):

    response = { 'status': 'pending' }

    if token_symbol == 'EDG':
        subscan_url = f'https://edgeware.subscan.io/api/open/extrinsic'

    payload = {
	    'hash': txnid
    }

    subscan_response = requests.post(subscan_url, data=json.dumps(payload)).json()

    if subscan_response:
        status = subscan_response.get('data').get('attributes')

        if status.get('success') == 'true':
            response = { 'status': 'done'}
        elif status.get('success') == 'false':
            response = { 'status': 'expired' }
        return response


def sync_polkadot_payout(contribution):
    if contribution.tx_id and contribution.tx_id != '0x0':
        txn_status = get_polkadot_txn_status(contribution)

        if txn_status:
            if txn_status.get('status') == 'done':
                contribution.success = True
                contribution.tx_cleared = True
                contribution.checkout_type = 'polkadot_std'
                record_contribution_activity(contribution)
                contribution.save()
            elif txn_status.get('status') == 'expired':
                contribution.tx_cleared = True
                contribution.success = False
                contribution.save()
