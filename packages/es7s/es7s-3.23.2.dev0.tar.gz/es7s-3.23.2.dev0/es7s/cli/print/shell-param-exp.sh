#!/usr/bin/bash
# ------------------------------------------------------------------------------
# es7s/core (Gen. I/legacy)
# (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
# shellcheck source=../es7s/data/es7s-shell-commons.sh
__ecl(){ local cur="$(dirname "$(readlink -f "$0")")" lcpath="core/_commons.sh"
local p=("$ES7S_SHELL_COMMONS" "$cur/../$lcpath" "$cur/../../$lcpath") ; while \
[[ ! $(type -t __es7s_com) =~ ^fu ]]; do [[ -f "${p[0]}" ]] && source "${p[0]}"
p=("${p[@]:1}"); [[ "${#p[@]}" -gt 0 ]] && continue; echo "ERROR: es7s/commons\
 not found. Reinstall es7s / set ES7S_SHELL_COMMONS env"; exit 7; done; }; __ecl
# ------------------------------------------------------------- loader v0922 --

function pvalue() {
    local v="$*"
    [[ -z $v ]] && echo "$nullstr" || echo "$v"
}
function try_1() {
    if (pvalue "${!1?$2}") 2> /dev/null ; then return ; fi
    pvalue "$2"
 }
function try_2() {
    if (pvalue "${!1:?$2}") 2> /dev/null ; then return ; fi
    pvalue "$2"
 }
# -----------------------------------------------------------------------------
C_RST=$_f
C_BOLD=$(_cs $I_BOLD)
C_ULINE=$(_cs $I_UNDERL)
function _mr() { echo     "$(_m "$IH_RED" ${*})" ; }
function _my() { echo  "$(_m "$IH_YELLOW" ${*})" ; }
function _mg() { echo   "$(_m "$IH_GREEN" ${*})" ; }
function _mb() { echo    "$(_m "$IH_BLUE" ${*})" ; }
function _mm() { echo "$(_m "$IH_MAGNETA" ${*})" ; }
function  _m() { echo          "$(_cs ${1})${*:2}${C_RST}" ; }
function  _i() { echo  "$(_cs ${1}  $I_INV)${*:2}${C_RST}" ; }
function  _b() { echo  "$(_cs ${1} $I_BOLD)${*:2}${C_RST}" ; }
function  _c() { echo "$(alignc ${1} "${*:2}")" ; }
function  _l() { echo "$(alignl ${1} "${*:2}")" ; }
function  _r() { echo "$(alignr ${1} "${*:2}")" ; }
C_TABLE=$(_cs $IH_GRAY )
pl_sc=$(_i "$IH_BLUE" ':')
mn_sc=$(_i "$IH_YELLOW" ':')
eq_sc=$(_i "$IH_GREEN" ':')
qs_sc=$(_i "$IH_RED" ':')
pl_op=$(_b "$IH_BLUE" '+')
mn_op=$(_b "$IH_YELLOW" '-')
eq_op=$(_b "$IH_GREEN" '=')
qs_op=$(_b "$IH_RED" '?')
pl_param=$(_mb "alt_v")
mn_param=$(_my "def_v")
eq_param=$(_mg "def_v")
qs_param=$(_mr "err_v")
nullstr=$(_m "37 3" "null")
pl_p=$(_mb "A")
mn_p=$(_my "D")
eq_p=$(_mg "D")
qs_p=$(_mr "E")
v=$(_mm 1486)
vnull=$(_m "3 95" "(null)")
vunset=$(_m "3 95" "(unset)")
p_v=param=
p_e=param=
expct=$(_mr "err_v")
p_ns=$'\u2205'
# -----------------------------------------------------------------------------
a=$(_mm 1486)
b=
unset c
# -----------------------------------------------------------------------------
printf "$C_TABLE"'╔ %---------58s ╤ %-7s ╤ %-7s ╤ %-7s ╗' '' '' '' '' | sed "s/ /═/g"

printf "\n$C_TABLE"'║ %---------58s │ %-7s │ %-7s │ %-7s ║' "$(_c 58 "${C_RST}${_b} Bash parameter${_f}$C_TABLE")" "$(_l 7 "param=")"\
                                                               "$(_l 7 "$p_e")"\
                                                               "$(_l 7 "$p_ns")"

printf "\n$C_TABLE"'║ %---------58s │ %-7s │ %-7s │ %-7s ║' "$(_c 58 "${C_RST}${_b} substitution${_f}$C_TABLE")" "$C_RST$(_r 7 "$v")$C_TABLE"\
                                                               "$C_RST$(_r 7 "$vnull")$C_TABLE"\
                                                               "$C_RST$(_r 7 "$vunset")$C_TABLE"

printf "\n$C_TABLE"'╠ %--36s   %-20s╪ %-7s ╪ %-7s ╪ %-7s ╣' '' '' '' '' '' | sed "s/ /═/g"

printf "\n$C_TABLE"'║ %--36s     %-20s%-7s │ %-7s │ %-7s ║'  "$C_RST$(_l 36 "${C_ULINE}${C_BOLD}Use Default:${C_RST} If param $(_b "$IH_YELLOW" 'n')ot $(_b "$IH_YELLOW" 's')et")"\
                                                             "$(_r 20 "\${${C_TABLE}param${C_RST}$mn_op$mn_param}${C_TABLE}=>${C_RST}")"\
                                                             "$C_RST$(_r 7 "$(pvalue ${a-$mn_param})")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(pvalue ${b-$mn_param})")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(pvalue ${c-$mn_param})")$C_TABLE"

printf "\n$C_TABLE"'║ %--36s     %-20s%-7s │ %-7s │ %-7s ║'  "$C_RST$(_l 36 "or $(_i $IH_YELLOW "e")mpty, use $(_my "def_v")")"\
                                                             "$(_r 20 "\${${C_TABLE}param${C_RST}$mn_sc$mn_op$mn_param}${C_TABLE}=>${C_RST}")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(pvalue "${a:-$mn_param}")")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(pvalue "${b:-$mn_param}")")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(pvalue "${c:-$mn_param}")")$C_TABLE"

printf "\n$C_TABLE"'╟ %--36s   %-20s┼ %-7s ┼ %-7s ┼ %-7s ╢' '' | sed "s/ /─/g"

printf "\n$C_TABLE"'║ %--36s     %-20s%-7s │ %-7s │ %-7s ║'  "$C_RST$(_l 36 "${C_ULINE}${C_BOLD}Assign Default:${C_RST} If param $(_b "$IH_GREEN" 'n')ot $(_b "$IH_GREEN" 's')et")"\
                                                             "$(_r 20 "\${${C_TABLE}param${C_RST}$eq_op$eq_param}${C_TABLE}=>${C_RST}")"\
                                                             "$C_RST$(_r 7 "$(pvalue "${a=$eq_param}")")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(pvalue "${b=$eq_param}")")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(pvalue "${c=$eq_param}")")$C_TABLE"

printf "\n$C_TABLE"'║ %--36s     %--20s%-7s │ %-7s │ %-7s ║'  "$C_RST$(_l 36 "or $(_i $IH_GREEN "e")mpty, set it to $(_mg "def_v") and use")"\
                                                              "$(_r 20 "\${${C_TABLE}param${C_RST}$eq_sc$eq_op$eq_param}${C_TABLE}=>${C_RST}")"\
                                                              "$C_RST$(_r 7 "$(pvalue "${a:=$eq_param}")")$C_TABLE"\
                                                              "$C_RST$(_r 7 "$(pvalue "${b:=$eq_param}")")$C_TABLE"\
                                                              "$C_RST$(_r 7 "$(pvalue "${c:=$eq_param}")")$C_TABLE"

printf "\n$C_TABLE"'╟ %---------58s ┼ %-7s ┼ %-7s ┼ %-7s ╢' '' | sed "s/ /─/g"

printf "\n$C_TABLE"'║ %--36s     %-20s%-7s │ %-7s │ %-7s ║'  "$C_RST$(_l 36 "${C_ULINE}${C_BOLD}Throw Error:${C_RST} If param $(_b "$IH_RED" 'n')ot $(_b "$IH_RED" 's')et")"\
                                                             "$(_r 20 "\${${C_TABLE}param${C_RST}$qs_op$qs_param}${C_TABLE}=>${C_RST}")"\
                                                             "$C_RST$(_r 7 "$(try_1 "a" "$qs_param")")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(try_1 "b" "$qs_param")")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(try_1 "c" "$qs_param")")$C_TABLE"

printf "\n$C_TABLE"'║ %--36s     %-20s%-7s │ %-7s │ %-7s ║'  "$C_RST$(_l 36 "or $(_i $IH_RED "e")mpty, print $(_m "$IH_RED" 'err_v') and $(_m "$IH_RED" 'exit')")"\
                                                             "$(_r 20 "\${${C_TABLE}param${C_RST}$qs_sc$qs_op$qs_param}${C_TABLE}=>${C_RST}")"\
                                                             "$C_RST$(_r 7 "$(try_2 "a" $qs_param)")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(try_2 "b" $qs_param)")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(try_2 "c" $qs_param)")$C_TABLE"

printf "\n$C_TABLE"'╟ %------ --58s ┼ %-7s ┼ %-7s ┼ %-7s ╢' '' | sed "s/ /─/g"

printf "\n$C_TABLE"'║ %--36s     %-20s%-7s │ %-7s │ %-7s ║'  "$C_RST$(_l 36 "${C_ULINE}${C_BOLD}Use Alternative:${C_RST} If param $(_b "$IH_BLUE" 'n')ot $(_b "$IH_BLUE" 's')et")"\
                                                             "$(_r 20 "\${${C_TABLE}param${C_RST}$pl_op$pl_param}${C_TABLE}=>${C_RST}")"\
                                                             "$C_RST$(_r 7 "$(pvalue "${a+$pl_param}")")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(pvalue "${b+$pl_param}")")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(pvalue "${c+$pl_param}")")$C_TABLE"

printf "\n$C_TABLE"'║ %--36s     %-20s%-7s │ %-7s │ %-7s ║'  "$C_RST$(_l 36 "or $(_i $IH_BLUE "e")mpty, use $nullstr; else - use $(_mb alt_v)")"\
                                                             "$(_r 20 "\${${C_TABLE}param${C_RST}$pl_sc$pl_op$pl_param}${C_TABLE}=>${C_RST}")"\
                                                             "$C_RST$(_r 7 "$(pvalue "${a:+$pl_param}")")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(pvalue "${b:+$pl_param}")")$C_TABLE"\
                                                             "$C_RST$(_r 7 "$(pvalue "${c:+$pl_param}")")$C_TABLE"

printf "\n$C_TABLE"'╚ %---------58s ╧ %-7s ╧ %-7s ╧ %-7s ╝\n' '' | sed "s/ /═/g"
printn
