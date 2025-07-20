# Optimization Baseline Analysis

**Date:** July 20, 2025  
**Purpose:** Document current state before implementing critical optimizations

## 1. DataFrame Operation Analysis

### Current Problematic Patterns

#### Excessive DataFrame Copying
- **43 instances** of `.copy()` operations found across codebase
- Many copies are defensive but unnecessary
- Key files with copies:
  - `map_utils.py`: 5 copy operations for "view issues"
  - `callbacks_split.py`: 3 copy operations
  - `callbacks/file_upload.py`: 3 copy operations
  - `coordinate_service.py`: 1 copy operation

#### Row-by-Row Operations (Performance Critical)
- **15+ instances** of `iterrows()` found
- Highly inefficient for large datasets
- Key locations:
  - `borehole_log_professional.py`: 1 instance
  - Various archive files: Multiple instances
  - `callbacks/search_functionality.py`: 1 instance

#### Apply Operations
- Several `.apply()` operations for coordinate transformations
- Row-wise operations that could be vectorized

### Memory Usage Patterns

#### Map Marker Loading
- All markers loaded at once regardless of viewport
- No lazy loading or viewport culling implemented
- Markers created for every borehole in dataset simultaneously

#### DataFrame Storage in Dash Store
- Large DataFrames converted to dict format for browser storage
- Multiple copies maintained in different callback states
- No memory cleanup between operations

## 2. Current Performance Bottlenecks

### High-Impact Issues
1. **Map markers**: All rendered simultaneously
2. **DataFrame copies**: Defensive copying creating memory overhead
3. **Row iteration**: `iterrows()` operations
4. **Coordinate transformations**: Not vectorized

### Medium-Impact Issues
1. **Browser memory**: Large data structures in Dash stores
2. **Concatenation**: Some unnecessary concat operations
3. **Filter operations**: Could be optimized

## 3. Memory Management Issues

### Identified Problems
1. **No lazy loading** for map markers
2. **Excessive DataFrame copying** for "safety"
3. **Large objects in browser memory** via Dash stores
4. **No cleanup routines** between operations

### Browser Memory Impact
- Large datasets cause browser memory pressure
- Multiple DataFrame copies stored in different callback states
- No garbage collection hints or cleanup

## 4. Optimization Targets

### Priority 1: DataFrame Operations
- [ ] Eliminate unnecessary `.copy()` operations
- [ ] Replace `iterrows()` with vectorized operations
- [ ] Optimize coordinate transformations
- [ ] Implement views where possible

### Priority 2: Map Marker Lazy Loading
- [ ] Implement viewport-based marker rendering
- [ ] Add marker clustering for high-density areas
- [ ] Optimize marker update operations

### Priority 3: Memory Management
- [ ] Implement cleanup routines
- [ ] Optimize browser memory usage
- [ ] Add memory monitoring and alerts

## 5. Testing Strategy

### Before Changes
- [ ] Document current memory usage patterns
- [ ] Benchmark DataFrame operations
- [ ] Test with large datasets
- [ ] Measure browser memory consumption

### After Changes
- [ ] Verify all functionality still works
- [ ] Measure performance improvements
- [ ] Test memory usage reduction
- [ ] Validate no regressions

## 6. Success Metrics

### Performance Targets
- **50%+ reduction** in unnecessary DataFrame copies
- **10x+ improvement** in row operations (iterrows → vectorized)
- **Lazy loading** for map markers (only visible ones)
- **30%+ reduction** in browser memory usage

### Functionality Requirements
- All existing features must continue working
- No regression in user experience
- Improved responsiveness for large datasets
- Better scalability for multiple files

---

**Next Steps:**
1. Implement DataFrame operation optimizations
2. Add lazy loading for map markers
3. Optimize memory management
4. Generate updated health report
