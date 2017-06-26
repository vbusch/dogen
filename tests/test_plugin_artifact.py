import argparse
import mock
import os
import tempfile
import unittest
import shutil
import logging
import sys

from dogen.plugins.artifact import Artifact
from dogen.generator import Generator

class MockDogen():
    def __init__(self, log, cfg={}):
        self.log = log
        self.descriptor = 0
        self.output = ""
        self.cfg = cfg

class TestArtifactPlugin(unittest.TestCase):
    def setUp(self):
        self.workdir = tempfile.mkdtemp(prefix='test_artifact_plugin')
        self.descriptor = tempfile.NamedTemporaryFile(delete=False)
        self.target_dir = os.path.join(self.workdir, "target")
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
        self.artifact_dir = os.path.join(self.workdir, "artifact")
        if not os.path.exists(self.artifact_dir):
            os.makedirs(self.artifact_dir)
    
        self.log = mock.Mock()

    def teardown(self):
        shutil.rmtree(self.workdir)

    def write_config(self, config):
        with self.descriptor as f:
            f.write(config.encode())

    def prepare_dogen(self, artifact_local_dir=None, output_dir=None):
        self.write_config("version: '1'\ncmd:\nfrom: scratch\nname: someimage\n")
        args = argparse.Namespace(path=self.descriptor.name, output=output_dir, without_sources=None,
                                  template=None, scripts_path=None, additional_script=None,
                                  skip_ssl_verification=None, repo_files_dir=None, artifact_local_enable=True, artifact_local_dir=artifact_local_dir)
        self.dogen = Generator(self.log, args, [Artifact])

    def test_should_skip_plugin_if_no_path_to_local_dir_is_provided(self):            
        self.prepare_dogen(None, self.target_dir)
        self.dogen.run()

        self.log.debug.assert_any_call("No directory with local artifact files specified, skipping artifact plugin")

    def test_should_skip_plugin_if_local_dir_does_not_exist(self):            
        self.prepare_dogen("non_existing_local_artifact_dir", self.target_dir)
        self.dogen.run()

        self.log.debug.assert_any_call("Provided path to directory with local artifact files does not exists or is not a directory")

    def test_should_skip_plugin_if_path_to_local_artifact_dir_is_provided_but_there_are_no_files(self):
        self.prepare_dogen(self.artifact_dir, self.target_dir)
        self.dogen.run()
        self.log.debug.assert_any_call("No local artifacts found")

    def test_local_artifact_files_should_be_copied_to_target(self):
        open(os.path.join(self.artifact_dir, "artifact1"), 'a').close()
        open(os.path.join(self.artifact_dir, "artifact2"), 'a').close()

        self.prepare_dogen(self.artifact_dir, self.target_dir)
        self.dogen.run()

        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "artifact1")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "artifact2")))
