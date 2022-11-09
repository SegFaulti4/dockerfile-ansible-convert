match_config = {
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
        "patterns": {
            "apt-get update": [
                "apt-get update"
            ],
            "apt-get upgrade": [
                "apt-get upgrade"
            ],
            "apt-get dist-upgrade": [
                "apt-get dist-upgrade"
            ],
            "apt-get dselect-upgrade": [
                "apt-get dselect-upgrade"
            ],
            "apt-get install": [
                "apt-get install [packages...]"
            ],
            "apt-get reinstall": [
                "apt-get reinstall [packages...]"
            ],
            "apt-get remove": [
                "apt-get remove [packages...]"
            ],
            "apt-get purge": [
                "apt-get purge [packages...]"
            ],
            "apt-get build-dep": [
                "apt-get build-dep [packages...]"
            ],
            "apt-get satisfy": [
                "apt-get satisfy [packages...]"
            ],
            "apt-get download": [
                "apt-get download [packages...]"
            ],
            "apt-get changelog": [
                "apt-get changelog [packages...]"
            ],
            "apt-get indextargets": [
                "apt-get indextargets"
            ],
            "apt-get check": [
                "apt-get check"
            ],
            "apt-get clean": [
                "apt-get clean"
            ],
            "apt-get autoclean": [
                "apt-get autoclean", "apt-get auto-clean"
            ],
            "apt-get autoremove": [
                "apt-get autoremove", "apt-get auto-remove"
            ],
        },
        "opts_postprocess_map": {
            "--force-yes --allow-unauthenticated --allow-downgrades --allow-remove-essential --allow-change-held-packages": {
                "apt": {
                    "force": "yes"
                }
            },
            "--allow-unauthenticated": {
                "apt": {
                    "allow_unauthenticated": "yes"
                }
            },
            "--only-upgrade": {
                "apt": {
                    "only_upgrade": "yes"
                }
            },
            "--autoremove": {
                "apt": {
                    "autoremove": "yes"
                }
            },
            "--purge": {
                "apt": {
                    "purge": "yes"
                }
            },
            "--no-install-recommends": {
                "apt": {
                    "install_recommends": "no"
                }
            },
            "--default-release <val>": {
                "apt": {
                    "default_release": "<val>"
                }
            },
            "-o Dpkg::Options::=<val>": {
                "apt": {
                    "option": "<val>"
                }
            },
            "--assume-yes": {},
            "--no-show-upgraded": {},
            "--verbose-versions": {},
            "--print-uris": {},
            "--list-cleanup": {},
            "--no-list-cleanup": {},
            "--quiet": {}
        },
        "examples": {
            "apt-get install [packages...]": {
                "apt": {
                    "name": "[packages...]",
                }
            },
            "apt-get update": {
                "apt": {
                    "update_cache": "yes"
                }
            },
            "apt-get upgrade": {
                "apt": {
                    "upgrade": "yes"
                }
            },
            "apt-get dist-upgrade": {
                "apt": {
                    "upgrade": "dist"
                }
            },
            "apt-get remove": {
                "apt": {
                    "state": "absent"
                }
            },
            "apt-get build-dep [packages...]": {
                "apt": {
                    "state": "build-dep",
                    "name": "[packages...]"
                }
            },
            "apt-get autoclean": {
                "apt": {
                    "autoclean": "yes"
                }
            },
            "apt-get autoremove": {
                "apt": {
                    "autoremove": "yes"
                }
            },
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
            "interactive once": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-I"
                ]
            },
            "interactive always": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-i"
                ]
            },
            "recursive": {
                "arg_required": False,
                "many_args": False,
                "aliases": [
                    "-r", "-R", "--recursive"
                ]
            },
            "directive": {
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
            }
        },
        "patterns": {
            "rm": [
                "rm [files...]"
            ],
        },
        "opts_postprocess_map": {
            "-f": {},
            "-I": {},
            "-i": {},
            "-d": {},
            "-v": {}
        },
        "examples": {
            # weak
            "rm [files...]": {
                "file": {
                    "state": "absent",
                    "path": "[files...]"
                }
            },
            "rm -r [files...]": {
                "file": {
                    "state": "absent",
                    "path": "[files...]"
                }
            }
        }
    },
    "mkdir": {
        "opts": {
            "mode": {
                "arg_required": False,
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
            }
        },
        "patterns": {
            "mkdir ": {
                "mkdir [directories...]"
            }
        },
        "opts_postprocess_map": {
            "-m <mode>": {
                "file": {
                    "mode": "<mode>"
                }
            },
            "-v": {}
        },
        "examples": {
            # weak
            "mkdir [directories...]": {
                "file": {
                    "path": "[directories...]",
                    "state": "directory"
                }
            },
            "mkdir -p [directories...]": {
                "file": {
                    "path": "[directories...]",
                    "state": "directory"
                }
            }
        }
    }
}
