# Return the current git tag (if present) or the first characters of the commit hash
GIT_HASH=$(git log -n1 --pretty='%h')
DESCRIBE=$(git describe --exact-match --tags $GIT_HASH 2> /dev/null)

if [[ -n $DESCRIBE ]]; then
    # Remove 'v' from beginning of tag, if present
    RESULT=$(echo $DESCRIBE | sed 's/^v//')
else
    RESULT=$GIT_HASH
    # Check if there are uncommitted changes
    if [[ -n $(git status -s) ]]; then
        RESULT+="*"
    fi
fi

echo $RESULT
