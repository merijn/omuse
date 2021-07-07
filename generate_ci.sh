#!/usr/bin/env bash
BASEPATH="$( cd "$(dirname "$0")/" ; pwd -P)"

if [ "$#" -eq 0 ]; then
    OUTFILE="$BASEPATH/.github/workflows/omuse-ci.yml"
elif [ "$#" -eq 1 ]; then
    OUTFILE="$1"
else
    printf "Too many arguments!\n"
    printf "Usage:\n"
    printf "$(basename "$0") <output-file>\n"
    exit 1
fi

cat "$BASEPATH/.github/workflows/templates/preamble" >"$OUTFILE"
for pkg in `cd "$BASEPATH/packages" && ls -d omuse-*`; do
    printf "  $pkg:\n"
    cat "$BASEPATH/.github/workflows/templates/matrix"
    printf "    name: $pkg - (\${{ join(matrix.*, ', ') }})\n"
    cat "$BASEPATH/.github/workflows/templates/pkg-preamble"
    if [ -f "$BASEPATH/.github/workflows/templates/deps-$pkg" ]; then
        cat "$BASEPATH/.github/workflows/templates/deps-$pkg"
    fi
    printf "    - name: \"Install OMUSE package: $pkg\"\n"
    printf "      run: |\n"
    printf "        pip install --no-clean --pre --find-links dist/ $pkg\n"
    printf "        rm -rf "\${TEMP_DIR}"/pip-*/\n"
    printf "      env:\n"
    printf "        TEMP_DIR: \${{ steps.get_temp.outputs.TMPDIR }}\n\n"
    cat "$BASEPATH/.github/workflows/templates/pkg-cleanup"
    printf "\n"
done >>"$OUTFILE"
