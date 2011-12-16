"""Minify Javascript and CSS with
`YUI Compressor <http://developer.yahoo.com/yui/compressor/>`_.

YUI Compressor is an external tool written in Java, which needs to be
available. One way to get it is to install the
`yuicompressor <http://pypi.python.org/pypi/yuicompressor>`_ package::

    pip install yuicompressor

No configuration is necessary in this case.

You can also get YUI compressor a different way and define
a ``YUI_COMPRESSOR_PATH`` setting that points to the ``.jar`` file.
Otherwise, an environment variable by the same name is tried. The
filter will also look for a ``JAVA_HOME`` environment variable to
run the ``.jar`` file, or will otherwise assume that ``java`` is
on the system path.
"""

from webassets.filter import Filter, JavaMixin


__all__ = ('YUIJSFilter', 'YUICSSFilter',)


class YUIBase(Filter, JavaMixin):

    # Will cause this base class not be loaded.
    name = None

    def setup(self):
        try:
            self.jar = self.get_config('YUI_COMPRESSOR_PATH',
                                       what='YUI Compressor')
        except EnvironmentError:
            try:
                import yuicompressor
                self.jar = yuicompressor.get_jar_filename()
            except ImportError:
                raise EnvironmentError(
                    "\nYUI Compressor jar can't be found."
                    "\nPlease either install the yuicompressor package:"
                    "\n\n    pip install yuicompressor\n"
                    "\nor provide a YUI_COMPRESSOR_PATH setting or an "
                    "environment variable with the full path to the "
                    "YUI compressor jar."
                )

        self.extra_args = self.get_config('YUI_COMPRESSOR_EXTRA_ARGS',
                                          require=False)

        self.java_setup()

    def output(self, _in, out, **kw):
        args = ['--charset=utf-8', '--type=%s' % self.mode]
        if self.extra_args:
            args.extend(self.extra_args)
        self.java_run(_in, out, args)


class YUIJSFilter(YUIBase):
    name = 'yui_js'
    mode = 'js'


class YUICSSFilter(YUIBase):
    name = 'yui_css'
    mode = 'css'
