import time
import os, subprocess
import tempfile

from webassets.filter import Filter
from webassets.exceptions import FilterError


__all__ = ('Less2Filter',)


class Less2Filter(Filter):
    """Converts `Less <http://lesscss.org/>`_ markup to real CSS.

    Only works with versions 2.x of the less gem.

    If you want to combine it with other CSS filters, make sure this
    one runs first.

    **Note**: Currently, this needs to be the very first filter
    applied. Changes by filters that ran before will be lost.
    """
    """XXX: This currently needs to be the very first filter applied. This is
    because it uses the "source filter" mechanism to support "@includes"
    in less, i.e. it let's the less compiler work directly with the source
    file, and ignores the input stream. Filters previously already applied
    will be lost. Ways to solve this:
        - Let filters specify that they need to be first (and auto do so,
          or raise an exception).
        - Rewrite the less filter:
             - It could properly use the input stream, and just create the
               temp file in the same directory as the input path.
             - It could rewrite @includes via regex, as the cssrewrite filter
               does, before passing the tempfile on to lessc.

    XXX: Depending on how less is actually used in practice, it might actually
    be a valid use case to NOT have this be a source filter, so that one can
    split the css files into various less files, referencing variables in other
    files' - without using @include, instead having them merged together by
    django-assets. This will currently not work because we compile each
    file separately, and the compiler would fail at undefined variables.
    """

    name = 'less2'

    def setup(self):
        self.less = self.get_config('LESS2_PATH', what='less2 binary',
                                    require=False)

    def input(self, _in, out, source_path, output_path):
        proc = subprocess.Popen(
            [self.less or 'lessc'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            # shell: necessary on windows to execute
            # ruby files, but doesn't work on linux.
            shell=(os.name == 'nt'))

        with open(source_path) as src:
            stdout, stderr = proc.communicate(input=src.read())

        # less only writes to stdout, as noted in the method doc, but
        # check everything anyway.
        if stderr or proc.returncode != 0:
            raise FilterError(('less: subprocess had error: stderr=%s, '
                               'stdout=%s, returncode=%s') % (
                                            stderr, stdout, proc.returncode))

        out.write(stdout)
