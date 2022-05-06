from docker2ansible.log import globalLog


class ModuleMatcher:

    @staticmethod
    def match(resolve_func, comm):
        try:
            return getattr(ModuleMatcher, "_match_" + comm.name)(resolve_func, comm)
        except Exception as exc:
            globalLog.info(type(exc))
            globalLog.info(exc)
            globalLog.info("Failed to match command: " + comm.line)
            return None

    @staticmethod
    def _match_rm(resolve_func, comm):
        if "force" in comm.opts and "recursive" in comm.opts:
            return {
                "file": {
                    "path": [resolve_func(w) for w in comm.params["paths"]],
                    "state": "absent"
                }
            }
        return None
