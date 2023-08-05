from .microsoft365defender import Microsoft365DefenderBackend
# TODO: add all backend classes that should be exposed to the user of your backend in the import statement above.

backends = {        # Mapping between backend identifiers and classes. This is used by the pySigma plugin system to recognize backends and expose them with the identifier.
    "microsoft365defender": Microsoft365DefenderBackend,
}