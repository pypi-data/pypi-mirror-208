from django.utils.translation import gettext_lazy
from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_mpesamz"
    verbose_name = "MPesaMZ"

    class PretixPluginMeta:
        name = gettext_lazy("MPesaMZ")
        author = "Ivan Ruby"
        description = gettext_lazy("A plugin to allow payments through the M-Pesa mobile payment platform")
        visible = True
        version = __version__
        category = "PAYMENT"
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA


