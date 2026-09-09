# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

#============
#output style
#============
define print_r
	@printf '\033[1;31m$(1)\033[0m\n'
endef

define print_y
	@printf '\033[1;33mX-----------| $(1)\033[0m\n'
endef

define print_g
	@printf '\033[1;32mX+++++| $(1)\033[0m\n'
endef

# for help target
define help_y
	@printf '\033[1;33m$(1)\033[0m\n'
endef

define help_g
	@printf '\033[1;32m $(1)\033[0m\n'
endef