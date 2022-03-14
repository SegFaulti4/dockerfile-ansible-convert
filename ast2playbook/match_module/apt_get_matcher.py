from json import dumps

from log import globalLog
from exception import MatchAnsibleModuleException


class AptGetMatcher:

    def __init__(self, stack):
        self.stack = stack

    def _apt_get_pop_last_flags(self, command):
        no_upgrade = command['options'].pop('--no-upgrade', False)
        reinstall = command['options'].pop('--reinstall', False)
        fix_broken = command['options'].pop('-f', False)
        fix_broken = fix_broken or command['options'].pop('--fix-broken', False)

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


    def match_apt_get(self, command):
        res = dict()

        # aliases
        if command['full name'] == 'apt-get reinstall':
            command['full name'] = 'apt-get install'
            command['options']['--reinstall'] = True
        elif command['full name'] == 'apt-get purge':
            command['full name'] = 'apt-get remove'
            command['options']['--purge'] = True

        # general flags match
        res['force-apt-get'] = 'yes'

        if command['options'].pop('--force-yes', False) or (
            command['options'].pop('--allow-unauthenticated', False) and
            command['options'].pop('--allow-downgrades', False) and
            command['options'].pop('--allow-remove-essential', False) and
            command['options'].pop('--allow-change-held-packages', False)
        ):
            res['force'] = 'yes'
        if command['options'].pop('--allow-unauthenticated', False):
            res['allow_unauthenticated'] = 'yes'
        if command['options'].pop('--only-upgrade', False):
            res['only_upgrade'] = 'yes'
        if command['options'].pop('--auto-remove', False):
            res['autoremove'] = 'yes'
        if command['options'].pop('--autoremove', False):
            res['autoremove'] = 'yes'
        if command['options'].pop('--purge', False):
            res['purge'] = 'yes'
        if command['options'].pop('--no-install-recommends', False):
            res['install_recommends'] = 'no'

        if command['options'].get('-t', None) is not None:
            res['default_release'] = command['options'].pop('-t')
        if command['options'].get('--target-release', None) is not None:
            res['default_release'] = command['options'].pop('--target-release')

        if command['options'].get('-o', None) is not None:
            o_opt = command['options']['-o']
            command['options']['-o'], res['dpkg_options'] = list(filter(lambda x: x[0:16] != 'Dpkg::Options::=', o_opt)),\
                                                            list(map(
                                                                lambda x: x[16:],
                                                                filter(lambda x: x[0:16] == 'Dpkg::Options::=', o_opt)
                                                            ))
            if len(command['options']['-o']) == 0:
                command['options'].pop('-o')

        if command.get('packages', None) is not None:
            res['name'] = command['packages']

        # general flags ignore
        ignore_list = [
            '-y',
            '--yes',
            '--no-show-upgraded',
            '-V',
            '--verbose-versions',
            '--print-uris',
            '--list-cleanup',
            '--no-list-cleanup',
            '--show-progress',
            '-q',
            '--quiet'
        ]
        for option in ignore_list:
            globalLog.debug('Ignoring apt-get option ' + option)
            command['options'].pop(option, False)

        if command['full name'] == 'apt-get update':
            self.match_apt_get_update(command, res)
        elif command['full name'] == 'apt-get upgrade':
            self.match_apt_get_upgrade(command, res)
        elif command['full name'] == 'apt-get install':
            self.match_apt_get_install(command, res)
        elif command['full name'] == 'apt-get dist-upgrade':
            self.match_apt_get_dist_upgrade(command, res)
        elif command['full name'] == 'apt-get remove':
            self.match_apt_get_remove(command, res)
        elif command['full name'] == 'apt-get build-dep':
            self.match_apt_get_build_dep(command, res)
        elif command['full name'] == 'apt-get check':
            self.match_apt_get_check(command, res)
        elif command['full name'] == 'apt-get autoclean':
            self.match_apt_get_autoclean(command, res)
        elif command['full name'] == 'apt-get autoremove':
            self.match_apt_get_autoclean(command, res)
        else:
            raise MatchAnsibleModuleException('Unsupported command ' + command['full name'])

        # check for remaining flags
        if bool(command['options']):
            raise MatchAnsibleModuleException('Unsupported ' + command['name'] + ' options:\n' +
                                              dumps(command['options'], sort_keys=True, indent=4))

        return {command['name']: res}
