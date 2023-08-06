#!/usr/bin/env python
# coding: utf-8

import pytest

from testing_config import BaseTestConfig
from tests.fixtures import xumm_api as test_fixtures
from unittest.mock import Mock, patch

import xumm


class TestPayloadCancel(BaseTestConfig):

    @classmethod
    def setUp(cls):
        cls.sdk = xumm.XummSdk(
            cls.json_fixtures['api']['key'],
            cls.json_fixtures['api']['secret']
        )

    @patch('xumm.client.requests.delete')
    def test_payload_cancel(cls, mock_delete):
        print('should cancel a payload by UUID')
        payloadId = '00000000-0000-4839-af2f-f794874a80b0'

        mock_delete.return_value = Mock(status_code=200)
        mock_delete.return_value.json.return_value = cls.json_fixtures['payload']['cancelled']
        
        cls.assertEqual(cls.sdk.payload.cancel(payloadId).to_dict(), cls.json_fixtures['payload']['cancelled'])

    @patch('xumm.client.requests.delete')
    def test_payload_not_found_errors(cls, mock_delete):
        print('should throw if payload not found with `returnErrors`')
        payloadId = '00000000-0000-4839-af2f-f794874a80b0'

        mock_delete.return_value = Mock(status_code=404)
        mock_delete.return_value.json.return_value = cls.json_fixtures['payload']['notfound']

        with pytest.raises(xumm.error.InvalidRequestError, match=r"Error code 404, see XUMM Dev Console, reference: a61ba59a-0304-44ae-a86e-d74808bd5190"):
            cls.sdk.payload.cancel(payloadId)
            cls.fail("payload_cancel() raised Exception unexpectedly!")

    @patch('xumm.client.requests.delete')
    @patch('xumm.client.requests.post')
    def test_payload_create_cancel(cls, mock_post, mock_delete):
        print('should cancel a payload by Created Payload')

        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = cls.json_fixtures['payload']['created']

        created_payload = cls.sdk.payload.create(test_fixtures.valid_payload())
        if created_payload:
            mock_delete.return_value = Mock(status_code=200)
            mock_delete.return_value.json.return_value = cls.json_fixtures['payload']['cancelled']
            cls.assertEqual(cls.sdk.payload.cancel(created_payload.uuid).to_dict(), cls.json_fixtures['payload']['cancelled'])

    @patch('xumm.client.requests.delete')
    @patch('xumm.client.requests.get')
    def test_payload_get_cancel(cls, mock_get, mock_delete):
        print('should cancel a payload by Fetched Payload')
        payloadId = '00000000-0000-4839-af2f-f794874a80b0'
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = cls.json_fixtures['payload']['get']

        get_payload = cls.sdk.payload.get(payloadId)
        if get_payload:
            mock_delete.return_value = Mock(status_code=200)
            mock_delete.return_value.json.return_value = cls.json_fixtures['payload']['cancelled']
            cls.assertEqual(cls.sdk.payload.cancel(get_payload.meta.uuid).to_dict(), cls.json_fixtures['payload']['cancelled'])
