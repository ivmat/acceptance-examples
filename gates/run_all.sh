#!/bin/sh
# Full gate suite. Run: bash gates/run_all.sh
# Runs every selftest first, then every real check. Exits 1 if any step fails.
here=$(cd "$(dirname "$0")" && pwd)
checks="lists links leaks secrets licence packages"
status=0
notes=""

run_step() {
    label=$1
    shift
    if out=$("$@" 2>&1); then
        echo "PASS $label"
        if [ -n "$out" ]; then
            echo "$out" | sed 's/^/     /'
        fi
        case "$out" in
            *"nothing to run"*)
                echo "     NOTE: $label ran nothing. This pass is not a real run."
                notes="$notes $label"
                ;;
        esac
    else
        echo "FAIL $label"
        echo "$out" | sed 's/^/     /'
        status=1
    fi
}

for c in $checks; do
    run_step "selftest $c" python3 -B "$here/check_$c.py" --selftest
done
for c in $checks; do
    run_step "check $c" python3 -B "$here/check_$c.py"
done

if [ "$status" -eq 0 ]; then
    echo "ALL GATES PASS"
    if [ -n "$notes" ]; then
        echo "NOTE: these steps ran nothing:$notes"
    fi
else
    echo "GATES FAILED"
fi
exit "$status"
