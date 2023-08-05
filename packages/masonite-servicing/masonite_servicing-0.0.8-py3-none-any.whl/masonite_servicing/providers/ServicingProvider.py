"""A ServicingProvider Service Provider."""

from masonite.packages import PackageProvider
from masonite.controllers import Controller

class ServicingProvider(PackageProvider):
    def configure(self):
        """Register objects into the Service Container."""
        (
            self
                .root("masonite_servicing")
                .name("servicing")
        )

    def register(self):
        super().register()

    def boot(self):
        """Boots services required by the container."""
        pass
