# Memory System Validation Report
Generated: 2025-08-22T03:41:07.879377

## Contract Requirements Validation

- **persistence**: ❌ FAILED
- **user_actions**: ❌ FAILED
- **cli_querying**: ✅ PASSED
- **json_export**: ✅ PASSED
- **performance**: ✅ PASSED

## Errors
- ❌ Feed item persistence test failed: Instance <FeedItem at 0x10b4987d0> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)
- ❌ User action recording test failed: Instance <UserAction at 0x10b43e060> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)

## Summary
⚠️ **VALIDATION FAILED** - 3/5 requirements passed