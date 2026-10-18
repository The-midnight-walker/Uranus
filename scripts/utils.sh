# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=4 sw=4 et tw=80 cc=80 fo+=t :

MISSING_PACKAGES=()
INSTALLED_PACKAGES=()
declare -A MISSING_TOOLS

RED="\033[1;31m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

OK="${GREEN}[ ok ]${NC}"
NOT="${RED}[ X  ]${NC}"

print_err() {
    local msg="$1"
    echo -e "${RED}${msg}${NC}"
}

print_success() {
    local msg="$1"
    echo -e "${GREEN}${msg}${NC}"
}

print_info() {
    local msg="$1"
    echo -e "${YELLOW}${msg}${NC}"
}

is_login_root() {
    # Verify this script is running with root privileges
    if [ "$EUID" -ne 0 ]; then
        print_err 'Permission denied: must be run as root.'
        exit 1
    fi
}

add_maps() {
    # Concatenate two associative arrays
    local -n dest="$1"
    local -n src="$2"

    for key in "${!src[@]}"; do
        dest["$key"]="${src[$key]}"
    done
}

is_installed_packages() {
    # Check package installation status:
    # - Adds uninstalled packages to MISSING_PACKAGES (if $to == "i")
    # - Adds installed packages to INSTALLED_PACKAGES (if $to == "u")
    local -n packages="$1"
    local to="$2"

    is_login_root

    for pkg in "${packages[@]}"; do
        if ! dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -q "install ok installed"; then
            echo -e "${NOT} '$pkg'"
            if [ "$to" == "i" ]; then
                MISSING_PACKAGES+=("$pkg")
            fi
        else
            echo -e "${OK} '$pkg'"
            if [ "$to" == "u" ]; then
                INSTALLED_PACKAGES+=("$pkg")
            fi
        fi
    done

    if [[ "${#MISSING_PACKAGES[@]}" -gt 0 && "$to" == "i" ]]; then
        return 1
    fi

    if [[ "${#INSTALLED_PACKAGES[@]}" -gt 0 && "$to" == "u" ]]; then
        return 1
    fi

    return 0
}

is_download_tools() {
    # Check if tools are already downloaded
    local -n tools="$1"

    for tool in "${!tools[@]}"; do
        if [ ! -f "$tool" ]; then
            echo -e "${NOT} '$tool'"
            MISSING_TOOLS["$tool"]="${tools[$tool]}"
        else
            echo -e "${OK} '$tool'"
        fi
    done
}

install_packages() {
    # Install all missing packages
    local failed_packages=()

    if [ "${#MISSING_PACKAGES[@]}" -eq 0 ]; then
        return 0
    fi

    is_login_root
    print_info '--- Installing missing packages ---'

    apt-get update >/dev/null 2>&1

    for pkg in "${MISSING_PACKAGES[@]}"; do
        echo -n "[ $pkg ]──╼ "
        if ! DEBIAN_FRONTEND=noninteractive apt-get install -y "$pkg" >/dev/null 2>&1; then
            echo -e "${RED}❌${NC}"
            failed_packages+=("$pkg")
        else
            echo -e "${GREEN}✔${NC}"
        fi
    done

    if [ "${#failed_packages[@]}" -gt 0 ]; then
        print_err "---| Failed to install the following packages:"
        for pkg in "${failed_packages[@]}"; do
            echo -n "$pkg  "
        done
        echo
        return 1
    else
        print_success "---| All packages installed successfully."
    fi

    return 0
}

remove_packages() {
    # Uninstall packages
    local failed_packages=()

    if [ "${#INSTALLED_PACKAGES[@]}" -eq 0 ]; then
        return 0
    fi

    is_login_root
    print_info '--- Removing packages ---'

    for pkg in "${INSTALLED_PACKAGES[@]}"; do
        echo -n "[ $pkg ]──╼ "
        if ! (DEBIAN_FRONTEND=noninteractive apt-get remove -y "$pkg" >/dev/null 2>&1 && apt-get purge -y "$pkg" >/dev/null 2>&1); then
            echo -e "${RED}❌${NC}"
            failed_packages+=("$pkg")
        else
            echo -e "${GREEN}✔${NC}"
        fi
    done

    apt-get clean

    if [ "${#failed_packages[@]}" -gt 0 ]; then
        print_err "---| Failed to remove the following packages:"
        for pkg in "${failed_packages[@]}"; do
            echo "$pkg  "
        done
        echo
        return 1
    else
        print_success "---| Packages removed successfully."
    fi

    return 0
}

download_tools() {
    # Download missing files specified in MISSING_TOOLS
    is_login_root

    if [ "${#MISSING_TOOLS[@]}" -eq 0 ]; then
        return 0
    fi

    print_info '--- Downloading missing tools ---'

    for tool_path in "${!MISSING_TOOLS[@]}"; do
        local url="${MISSING_TOOLS[$tool_path]}"
        local target_dir
        target_dir=$(dirname "$tool_path")

        mkdir -p "$target_dir" 2>/dev/null

        if wget -O "$tool_path" "$url" >/dev/null 2>&1; then
            print_success "Successfully downloaded '$tool_path'"
        else
            print_err "Failed to download '$tool_path' from '$url'"
        fi
    done
}

add_right_x() {
    # Add executable permissions to a file
    local obj="$1"

    if [ ! -e "$obj" ]; then
        print_err "File or directory '$obj' does not exist"
        return 1
    fi

    if [ ! -x "$obj" ]; then
        print_info "*** chmod +x '$obj' ***"
        chmod +x "$obj" 2>/dev/null || true
    fi

    return 0
}

add_dir() {
    # Create a directory with 0700 permissions
    local dir="$1"

    if [ ! -d "$dir" ]; then
        print_info "*** mkdir -m 0700 -p '$dir' ***"
        mkdir -m 0700 -p "$dir" 2>/dev/null || true
    fi

    return 0
}

add_file() {
    # Create an empty file
    local file="$1"
    local dir
    dir=$(dirname "$file")

    if [ ! -d "$dir" ]; then
        print_err "Directory '$dir' does not exist"
        return 1
    fi

    if [ ! -f "$file" ]; then
        print_info "*** touch '$file' ***"
        touch "$file"
    fi

    return 0
}