"""
DETAILED IMPLEMENTATION PLAN
==========================

Following the instructions.md multi-stage action plan, this document outlines 
the systematic approach to fix all three critical issues identified.

## ISSUE SUMMARY

### Issue 1: ErrorHandler Method Name Mismatch
**Problem**: Plot generation callbacks call `self.error_handler.handle_error()` 
but ErrorHandler class only provides `handle_callback_error()` method.
**Impact**: AttributeError causing callback failures
**Root Cause**: Method naming inconsistency between caller and implementation

### Issue 2: Plot Generation Type Error  
**Problem**: `plot_section_from_ags_content()` returns base64 string by default,
but callback expects matplotlib Figure object for `.savefig()` calls.
**Impact**: "'str' object has no attribute 'savefig'" error
**Root Cause**: Default `return_base64=True` parameter in plotting function

### Issue 3: "No borehole log data available"
**Problem**: Reported by user but function exists and is importable
**Impact**: Users cannot generate borehole logs
**Root Cause**: Likely data flow or parameter passing issue (needs investigation)

## IMPLEMENTATION STRATEGY

### Phase 1: Quick Critical Fixes (Immediate)
1. Fix ErrorHandler method name mismatch in plot_generation.py
2. Fix plot function return type in plot_generation.py
3. Test fixes with comprehensive validation

### Phase 2: Data Flow Investigation (Secondary) 
1. Investigate borehole log data availability issue
2. Test borehole log generation with sample data
3. Fix any data flow or parameter issues found

### Phase 3: Validation & Testing (Final)
1. Run comprehensive tests on all fixes
2. Validate that all three issues are resolved
3. Perform integration testing
4. Document changes and create test coverage

## DETAILED IMPLEMENTATION STEPS

### Step 1: Fix ErrorHandler Method Names
**File**: callbacks/plot_generation.py
**Lines**: 85, 126
**Change**: 
- FROM: `self.error_handler.handle_error(`
- TO: `self.error_handler.handle_callback_error(`

**Rationale**: Use existing API method with correct name

### Step 2: Fix Plot Function Return Type
**File**: callbacks/plot_generation.py  
**Line**: 112-116
**Change**: Add `return_base64=False` parameter to plot_section_from_ags_content call
**Rationale**: Ensures matplotlib Figure object is returned for processing

### Step 3: Investigate Borehole Log Data Issue
**Approach**: 
1. Check callback registration for borehole log generation
2. Verify data parameter passing
3. Test with actual data samples
4. Fix any data flow issues discovered

### Step 4: Comprehensive Testing
**Tests to Run**:
1. Error handling method calls work correctly
2. Plot generation returns proper figure objects  
3. Borehole log generation works with sample data
4. Integration test of full workflow
5. Memory management (figure cleanup) still works

## RISK ASSESSMENT

### Low Risk Changes
- ErrorHandler method name fix: Direct API method substitution
- Plot return type fix: Simple parameter addition

### Medium Risk Areas  
- Borehole log investigation: May uncover deeper data flow issues
- Integration testing: Need to verify all workflows still work

### Mitigation Strategies
1. Make changes incrementally with testing after each step
2. Keep backup of original files
3. Test with multiple data scenarios
4. Verify memory management still works (figure cleanup)

## SUCCESS CRITERIA

### Primary Success Metrics
1. ✅ No more AttributeError: 'ErrorHandler' object has no attribute 'handle_error'
2. ✅ No more "'str' object has no attribute 'savefig'" errors  
3. ✅ Borehole log generation works for users
4. ✅ All existing functionality continues to work

### Secondary Success Metrics
1. ✅ Error handling provides meaningful user feedback
2. ✅ Plot generation maintains memory efficiency
3. ✅ Config system (both monolithic and modular) continues working
4. ✅ Integration tests pass for all workflows

## TESTING APPROACH

### Unit Tests
- Test ErrorHandler method calls work
- Test plot function return types
- Test borehole log function calls

### Integration Tests  
- Test complete plot generation workflow
- Test error handling in callback failures
- Test borehole log generation end-to-end

### Regression Tests
- Verify existing functionality unchanged
- Test memory management still works
- Test config system accessibility

## DEPENDENCIES & CONSTRAINTS

### Dependencies
- matplotlib (for figure handling)
- dash (for callback system)
- Existing AGS data parsing functions
- Error handling system architecture

### Constraints
- Must maintain backward compatibility
- Cannot break existing config system
- Must preserve memory management (figure cleanup)
- Should maintain consistent error reporting

## ROLLBACK PLAN

If issues arise:
1. Restore original callbacks/plot_generation.py
2. Verify original functionality works
3. Re-analyze root causes with additional debugging
4. Implement more conservative fixes

Created: July 2025
Author: Debug Assistant following instructions.md multi-stage action plan
"""
