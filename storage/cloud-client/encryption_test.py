# Copyright 2016 Google, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import tempfile

import encryption
from gcloud import storage
import pytest

TEST_ENCRYPTION_KEY = 'brtJUWneL92g5q0N2gyDSnlPSYAiIVZ/cWgjyZNeMy0='
TEST_ENCRYPTION_KEY_DECODED = base64.b64decode(TEST_ENCRYPTION_KEY)


def test_generate_encryption_key(capsys):
    encryption.generate_encryption_key()
    out, _ = capsys.readouterr()
    encoded_key = out.split(':', 1).pop().strip()
    key = base64.b64decode(encoded_key)
    assert len(key) == 32, 'Returned key should be 32 bytes'


def test_upload_encrypted_blob(cloud_config):
    with tempfile.NamedTemporaryFile() as source_file:
        source_file.write(b'test')

        encryption.upload_encrypted_blob(
            cloud_config.storage_bucket,
            source_file.name,
            'test_encrypted_upload_blob',
            TEST_ENCRYPTION_KEY)


@pytest.fixture
def test_blob(cloud_config):
    """Provides a pre-existing blob in the test bucket."""
    bucket = storage.Client().bucket(cloud_config.storage_bucket)
    blob = bucket.blob('encryption_test_sigil')
    content = 'Hello, is it me you\'re looking for?'
    blob.upload_from_string(
        content,
        encryption_key=TEST_ENCRYPTION_KEY_DECODED)
    return blob.name, content


def test_download_blob(test_blob, cloud_config):
    test_blob_name, test_blob_content = test_blob
    with tempfile.NamedTemporaryFile() as dest_file:
        encryption.download_encrypted_blob(
            cloud_config.storage_bucket,
            test_blob_name,
            dest_file.name,
            TEST_ENCRYPTION_KEY)

        downloaded_content = dest_file.read().decode('utf-8')
        assert downloaded_content == test_blob_content
