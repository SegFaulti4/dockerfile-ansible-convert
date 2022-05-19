from log import globalLog
import dockerfile_ansible_convert.apt_get_matcher as apt_get_matcher


class ModuleMatcher:

    @staticmethod
    def match(context, comm):
        try:
            name = "_match_" + comm.name
            name = name.replace("-", "_")
            print(name)
            return getattr(ModuleMatcher, name)(context, comm)
        except Exception as exc:
            globalLog.info(type(exc))
            globalLog.info(exc)
            globalLog.info("Failed to match command: " + comm.line)
            return None

    @staticmethod
    def _match_apt_get(context, comm):
        matcher = apt_get_matcher.AptGetMatcher(context)
        return matcher.match_apt_get(comm)

    @staticmethod
    def _match_rm(context, comm):
        if "force" in comm.opts and "recursive" in comm.opts:
            paths = [context.resolve_path_value(w) for w in comm.params["paths"]]
            if any(p is None for p in paths):
                return None
            return {
                "file": {
                    "path": paths,
                    "state": "absent"
                }
            }
        return None

    @staticmethod
    def _match_mkdir(context, comm):
        if "help" in comm.opts or "version" in comm.opts:
            return None
        res = {
            "file": {
                "state": "directory"
            }
        }
        paths = [context.resolve_path_value(w) for w in comm.params["paths"]]
        if any(p is None for p in paths):
            return None
        if "mode" in comm.opts:
            mode = context.resolve_value(comm.opts["mode"])
            if mode is None:
                return None
            res["file"]["mode"] = mode
        if "Z" in comm.opts:
            res["file"]["selevel"] = "_default"
            res["file"]["serole"] = "_default"
            res["file"]["setype"] = "_default"
            res["file"]["seuser"] = "_default"
        if "context" in comm.opts:
            cont = context.resolve_value(comm.opts["context"])
            if cont is None:
                return None
            cont = cont.split(':')
            if len(cont) != 4:
                return None
            res["file"]["seuser"] = cont[0]
            res["file"]["serole"] = cont[1]
            res["file"]["setype"] = cont[2]
            res["file"]["selevel"] = cont[3]
        return res

    @staticmethod
    def _match_cd(context, comm):
        if "directory" in comm.params:
            dr = context.resolve_path_value(comm.params["directory"])
            if dr is None:
                return None
            context.set_local_wd(dr)

    @staticmethod
    def _match_chmod(context, comm):
        if "help" in comm.opts or "version" in comm.opts:
            return None
        if comm.fullname == "chmod reference":
            return None
        mode = context.resolve_value(comm.params["mode"])
        file = context.resolve_value(comm.params["file"])
        if mode is None or file is None:
            return None
        res = {
            "file": {
                "state": "file",
                "mode": mode,
                "path": file
            }
        }
        if "recursive" in comm.opts:
            res["file"]["state"] = "directory"
            res["file"]["recurse"] = "yes"
        return res
