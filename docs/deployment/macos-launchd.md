# macOS with launchd

Use a tracked plist with absolute executable paths and a wrapper only when environment preparation
is required. Validate the plist, bootstrap or kickstart the correct user/system domain, inspect
service state, and verify application behavior. Keep credentials outside the plist and source
repository. Document bootout and rollback procedures.

