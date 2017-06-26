import glob
import os
import shutil

from dogen.plugin import Plugin

class Artifact(Plugin):
    @staticmethod
    def info():
        return "artifact", "Support overriding the sources from an artifact directory"

    @staticmethod
    def inject_args(parser):
        parser.add_argument('--artifact-local-enable', action='store_true', help='Uses local artifacts from the provided artifacts directory')
        parser.add_argument('--artifact-local-dir', default='artifacts', help='Provides path to local artifacts directory')

        return parser

    def __init__(self, dogen, args):
        super(Artifact, self).__init__(dogen, args)
        self.artifact_files = []

    def before_sources(self):

        if not self.artifact_files:
            return
        
        if not os.path.exists(self.output):
            self.log.warn("build directory does not exist")
            return
        self.log.info("Copying local artifact files from '%s'" % self.args.artifact_local_dir)

        for item in sorted(self.artifact_files):
            src = os.path.join(self.args.artifact_local_dir, item)
            dest = os.path.join(self.output, item)
            self.log.debug("Copying local artifact %s" % os.path.basename(src))
            if os.path.isdir(src):
                if os.path.exists(dest):
                    shutil.rmtree(dest) 
                shutil.copytree(src, dest)
            else:
                if os.path.exists(dest):
                    os.remove(dest)
                shutil.copy2(src, dest)

        self.log.debug("Done.")

    def prepare(self, cfg):

        if not self.args.artifact_local_enable:
            return

        if not self.args.artifact_local_dir:
            self.log.debug("No directory with local artifact files specified, skipping artifact plugin")
            return

        if not os.path.isdir(self.args.artifact_local_dir):
            self.log.debug("Provided path to directory with local artifact files does not exists or is not a directory")
            return
            
        self.artifact_files = os.listdir(self.args.artifact_local_dir)

        if not self.artifact_files:
            self.log.debug("No local artifacts found")
            return
