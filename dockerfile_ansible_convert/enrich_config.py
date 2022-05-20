commands = {
    "apt-get": {
        "opts": {
            "no-install-recommends": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--no-install-recommends"
                ]
            },
            "install-suggests": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--install-suggests"
                ]
            },
            "download-only": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    '-d', "--download-only"
                ]
            },
            "fix-broken": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    '-f', '--fix-broken'
                ]
            },
            "fix-missing": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    '-m', "--ignore-missing", "--fix-missing"
                ]
            },
            "no-download": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--no-download"
                ]
            },
            "quiet": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-q", "--quiet"
                ]
            },
            "simulate": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    '-s', "--simulate", "--just-print", "--dry-run", "--recon", "--no-act"
                ]
            },
            "assume-yes": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    '-y', "--yes", "--assume-yes"
                ]
            },
            "assume-no": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--assume-no"
                ]
            },
            "no-show-upgraded": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--no-show-upgraded"
                ]
            },
            "verbose-versions": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-V", "--verbose-versions"
                ]
            },
            "host-architecture": {
                "arg_required": True,
                "many_args": False,
                "aliases": [
                    "-a", "--host-architecture"
                ]
            },
            "build-profiles": {
                "arg_required": True,
                "many_args": False,
                "aliases": [
                    "-P", "--build-profiles"
                ]
            },
            "build": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-b", "--compile", "--build"
                ]
            },
            "ignore-hold": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--ignore-hold"
                ]
            },
            "with-new-pkgs": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--with-new-pkgs"
                ]
            },
            "no-upgrade": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--no-upgrade"
                ]
            },
            "only-upgrade": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--only-upgrade"
                ]
            },
            "allow-downgrades": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--allow-downgrades"
                ]
            },
            "allow-remove-essential": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--allow-remove-essential"
                ]
            },
            "allow-change-held-packages": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--allow-change-held-packages"
                ]
            },
            "force-yes": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--force-yes"
                ]
            },
            "print-uris": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--print-uris"
                ]
            },
            "purge": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--purge"
                ]
            },
            "reinstall": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--reinstall"
                ]
            },
            "list-cleanup": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--list-cleanup"
                ]
            },
            "no-list-cleanup": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--no-list-cleanup"
                ]
            },
            "default-release": {
                "arg_required": True,
                "many_args": False,
                "aliases": [
                    "-t", "--target-release", "--default-release"
                ]
            },
            "trivial-only": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--trivial-only"
                ]
            },
            "no-remove": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--no-remove"
                ]
            },
            "autoremove": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--auto-remove", "--autoremove"
                ]
            },
            "only-source": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--only-source"
                ]
            },
            "diff-only": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--diff-only"
                ]
            },
            "dsc-only": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--dsc-only"
                ]
            },
            "tar-only": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--tar-only"
                ]
            },
            "arch-only": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--arch-only"
                ]
            },
            "indep-only": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--indep-only"
                ]
            },
            "allow-unauthenticated": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--allow-unauthenticated"
                ]
            },
            "no-allow-insecure-repositories": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--no-allow-insecure-repositories"
                ]
            },
            "allow-releaseinfo-change": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--allow-releaseinfo-change"
                ]
            },
            "show-progress": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--show-progress"
                ]
            },
            "with-source": {
                "arg_required": True,
                "many_args": False,
                "aliases": [
                    "--with-source"
                ]
            },
            "help": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-h", "--help"
                ]
            },
            "version": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-v", "--version"
                ]
            },
            "config-file": {
                "arg_required": True,
                "many_args": False,
                "aliases": [
                    "-c", "--config-file"
                ]
            },
            "option": {
                "arg_required": True,
                "many_args": True,
                "aliases": [
                    "-o", "--option"
                ]
            },
        },
        "scenarios": {
            "apt-get update": {
                "aliases": ["apt-get update"]
            },
            "apt-get upgrade": {
                "aliases": ["apt-get upgrade"]
            },
            "apt-get dist-upgrade": {
                "aliases": ["apt-get dist-upgrade"]
            },
            "apt-get dselect-upgrade": {
                "aliases": ["apt-get dselect-upgrade"]
            },
            "apt-get install": {
                "aliases": ["apt-get install [packages...]"]
            },
            "apt-get reinstall": {
                "aliases": ["apt-get reinstall [packages...]"]
            },
            "apt-get remove": {
                "aliases": ["apt-get remove [packages...]"]
            },
            "apt-get purge": {
                "aliases": ["apt-get purge [packages...]"]
            },
            "apt-get build-dep": {
                "aliases": ["apt-get build-dep [packages...]"]
            },
            "apt-get satisfy": {
                "aliases": ["apt-get satisfy [packages...]"]
            },
            "apt-get download": {
                "aliases": ["apt-get download [packages...]"]
            },
            "apt-get changelog": {
                "aliases": ["apt-get changelog [packages...]"]
            },
            "apt-get indextargets": {
                "aliases": ["apt-get indextargets"]
            },
            "apt-get check": {
                "aliases": ["apt-get check"]
            },
            "apt-get clean": {
                "aliases": ["apt-get clean"]
            },
            "apt-get autoclean": {
                "aliases": ["apt-get autoclean", "apt-get auto-clean"]
            },
            "apt-get autoremove": {
                "aliases": ["apt-get autoremove", "apt-get auto-remove"]
            }
        }
    },
    "echo": {
        "opts": {
            "e": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-e"
                ]
            },
            "n": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-n"
                ]
            },
            "E": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-E"
                ]
            },
            "version": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--version"
                ]
            },
            "help": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--help"
                ]
            },
        },
        "scenarios": {
            "echo": {
                "aliases": [
                    "echo [items...]"
                ]
            }
        }
    },
    "rm": {
        "opts": {
            "force": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-f", "--force"
                ]
            },
            "i": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-i"
                ]
            },
            "I": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-I"
                ]
            },
            "interactive": {
                "arg_required": True,
                "many_args": False,
                "aliases": [
                    "--interactive"
                ]
            },
            "one-file-system": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--one-file-system"
                ]
            },
            "preserve-root": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--preserve-root"
                ]
            },
            "no-preserve-root": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--no-preserve-root"
                ]
            },
            "recursive": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-r", "-R", "--recursive"
                ]
            },
            "dir": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-d", "--dir"
                ]
            },
            "verbose": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-v", "--verbose"
                ]
            },
            "help": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--help"
                ]
            },
            "version": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--version"
                ]
            },
        },
        "scenarios": {
            "rm": {
                "aliases": [
                    "rm [paths...]"
                ]
            }
        }
    },
    "mkdir": {
        "opts": {
            "mode": {
                "arg_required": True,
                "many_args": False,
                "aliases": [
                    "-m", "--mode"
                ]
            },
            "parents": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-p", "--parents"
                ]
            },
            "verbose": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-v", "--verbose"
                ]
            },
            "Z": {
               "arg_required": False,
               "many_args": False,
               "aliases": [
                    "-Z"
                ]
            },
            "context": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--context"
                ]
            },
            "help": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--help"
                ]
            },
            "version": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--version"
                ]
            }
        },
        "scenarios": {
            "mkdir": {
                "aliases": [
                    "mkdir [paths...]"
                ]
            }
        }
    },
    "cd": {
        "opts": {
            "L": {
               "arg_required": False,
               "many_args": False,
               "aliases": [
                    "-L"
                ]
            },
            "P": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-P"
                ]
            }
        },
        "scenarios": {
            "cd": {
                "aliases": [
                    "cd [directory]"
                ]
            }
        }
    },
    "chmod": {
        "opts": {
            "changes": {
               "arg_required": False,
               "many_args": False,
               "aliases": [
                    "-c", "--changes"
                ]
            },
            "quiet": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-f", "--silent", "--quiet"
                ]
            },
            "verbose": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-v", "--verbose"
                ]
            },
            "no-preserve-root": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--no-preserve-root"
                ]
            },
            "preserve-root": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--preserve-root"
                ]
            },
            "recursive": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-R", "--recursive"
                ]
            },
            "reference": {
                "arg_required": True,
                "many_args": False,
                "aliases": [
                    "--reference"
                ]
            },
            "help": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--help"
                ]
            },
            "version": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "--version"
                ]
            }
        },
        "scenarios": {
            "chmod mode": {
                "aliases": [
                    "chmod <mode> <file>",
                ]
            },
            "chmod reference": {
                "aliases": [
                    "chmod <file>"
                ]
            }
        }
    }
}
