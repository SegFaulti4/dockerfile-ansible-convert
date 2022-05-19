from json import dumps
from log import globalLog
from exception import MatchAnsibleModuleException


class AptGetMatcher:

    def __init__(self, context):
        self.context = context

    def _pop_bool_opt(self, opt, comm):
        if opt in comm.opts:
            comm.opts.pop(opt)
            return True
        return False

    def _apt_get_pop_last_flags(self, comm):
        no_upgrade = self._pop_bool_opt("no-upgrade", comm)
        reinstall = self._pop_bool_opt("reinstall", comm)
        fix_broken = self._pop_bool_opt("fix-broken", comm)

        return {'no_upgrade': no_upgrade, 'reinstall': reinstall, 'fix_broken': fix_broken}

    def match_apt_get_update(self, command, task):
        task['update_cache'] = 'no'

    def match_apt_get_upgrade(self, command, task):
        task['upgrade'] = 'yes'

    def match_apt_get_dist_upgrade(self, command, task):
        task['upgrade'] = 'dist'

    def match_apt_get_install(self, command, task):
        last_flags = self._apt_get_pop_last_flags(command)

        if last_flags['fix_broken'] or (last_flags['reinstall'] and last_flags['no_upgrade']):
            task['state'] = 'fixed'
        elif last_flags['reinstall']:
            task['state'] = 'latest'
        elif last_flags['no_upgrade']:
            task['state'] = 'present'

    def match_apt_get_remove(self, command, task):
        last_flags = self._apt_get_pop_last_flags(command)
        task['state'] = 'absent'

        if last_flags['fix_broken']:
            task['state'] = 'fixed'

    def match_apt_get_build_dep(self, command, task):
        task['state'] = 'build-dep'

    def match_apt_get_check(self, command, task):
        self.match_apt_get_update(command, task)

    def match_apt_get_autoclean(self, command, task):
        task['autoclean'] = 'yes'

    def match_apt_get_autoremove(self, command, task):
        task['autoremove'] = 'yes'

    def match_apt_get(self, comm):
        res = dict()

        # aliases
        if comm.fullname == 'apt-get reinstall':
            comm.fullname = 'apt-get install'
            comm.opts["reinstall"] = ""
        elif comm.fullname == 'apt-get purge':
            comm.fullname = 'apt-get remove'
            comm.opts['purge'] = ""

        # general flags match
        res['force-apt-get'] = 'yes'

        if self._pop_bool_opt("force-yes", comm) or \
                self._pop_bool_opt("allow-unauthenticated", comm) and \
                self._pop_bool_opt("allow-downgrades", comm) and \
                self._pop_bool_opt("--allow-remove-essential", comm) and \
                self._pop_bool_opt("--allow-change-held-packages", comm):
            res['force'] = 'yes'
        if self._pop_bool_opt("allow-unauthenticated", comm):
            res['allow_unauthenticated'] = 'yes'
        if self._pop_bool_opt("only-upgrade", comm):
            res['only_upgrade'] = 'yes'
        if self._pop_bool_opt("autoremove", comm):
            res['autoremove'] = 'yes'
        if self._pop_bool_opt("purge", comm):
            res['purge'] = 'yes'
        if self._pop_bool_opt("no-install-recommends", comm):
            res['install_recommends'] = 'no'

        if "default-release" in comm.opts:
            val = self.context.resolve_value(comm.opts["default-release"])
            if val is None:
                return None
            comm.opts.pop("default-release")
            res['default_release'] = val
        if "option" in comm.opts:
            o_opt = [self.context.resolve_value(o) for o in comm.opts["option"]]
            if any(o is None for o in o_opt):
                return None
            res["dpkg_options"] = [o[:16] for o in o_opt if o.startswith("Dpkg::Options::=")]
            comm.opts["option"] = [o for o in o_opt if not o.startswith("Dpkg::Options::=")]
            if not comm.opts["option"]:
                comm.opts.pop("option")

        if "packages" in comm.params:
            vals = [self.context.resolve_value(v) for v in comm.params["packages"]]
            if any(o is None for o in vals):
                return None
            res["name"] = vals

        # general flags ignore
        ignore_list = [
            "assume-yes",
            "no-show-upgraded",
            "verbose-versions",
            "print-uris",
            'list-cleanup',
            'no-list-cleanup',
            'quiet'
        ]
        for option in ignore_list:
            globalLog.debug('Ignoring apt-get option ' + option)
            comm.opts.pop(option, None)

        if comm.fullname == 'apt-get update':
            self.match_apt_get_update(comm, res)
        elif comm.fullname == 'apt-get upgrade':
            self.match_apt_get_upgrade(comm, res)
        elif comm.fullname == 'apt-get install':
            self.match_apt_get_install(comm, res)
        elif comm.fullname == 'apt-get dist-upgrade':
            self.match_apt_get_dist_upgrade(comm, res)
        elif comm.fullname == 'apt-get remove':
            self.match_apt_get_remove(comm, res)
        elif comm.fullname == 'apt-get build-dep':
            self.match_apt_get_build_dep(comm, res)
        elif comm.fullname == 'apt-get check':
            self.match_apt_get_check(comm, res)
        elif comm.fullname == 'apt-get autoclean':
            self.match_apt_get_autoclean(comm, res)
        elif comm.fullname == 'apt-get autoremove':
            self.match_apt_get_autoclean(comm, res)
        else:
            raise MatchAnsibleModuleException('Unsupported command ' + comm.fullname)

        # check for remaining flags
        if bool(comm.opts):
            raise MatchAnsibleModuleException('Unsupported ' + comm.name + ' options:\n' +
                                              dumps(comm.opts, sort_keys=True, indent=4))

        return {comm.name: res}
