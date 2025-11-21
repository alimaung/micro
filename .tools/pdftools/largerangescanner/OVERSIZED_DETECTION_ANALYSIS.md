# Oversized Page Detection Logic Analysis

## Problem Statement

We need to determine the correct logic for detecting "oversized" pages in PDF documents for microfilm allocation. The definition of "oversized" affects which pages are allocated to 35mm film versus 16mm film.

**Current threshold:** A3 paper size (11.7" × 16.5" or 842 × 1191 points)

**Question:** What makes a page "oversized" relative to A3?

---

## Background

### Physical Context
- **16mm film:** Standard microfilm format for regular documents
- **35mm film:** Used for oversized pages that can't fit on 16mm
- **A3 paper:** 11.7" × 16.5" (297mm × 420mm) - considered the threshold size
- **Goal:** Pages larger than A3 should go to 35mm film for better quality/readability

### Current Implementation

The production code uses **AND logic**:

```python
# A page is oversized if BOTH dimensions exceed A3
is_oversized = (
    (width > 842 AND height > 1191) OR      # Bigger than A3 portrait
    (width > 1191 AND height > 842)          # Bigger than A3 landscape
)
```

**This checks:** "Is the page bigger than A3 in BOTH dimensions simultaneously?"

---

## Three Possible Definitions

### Option 1: Edge-Based (Current Implementation)
**Definition:** A page is oversized if BOTH edges exceed their corresponding A3 dimensions.

```python
def is_oversized_edge_based(width, height):
    """Page is oversized if both dimensions exceed A3 in same orientation."""
    return (
        (width > 842 and height > 1191) or  # Portrait: both exceed A3 portrait
        (width > 1191 and height > 842)      # Landscape: both exceed A3 landscape
    )
```

#### Examples:

| Page Size | Width | Height | Oversized? | Reason |
|-----------|-------|--------|------------|--------|
| A3 Portrait | 842 pts (11.7") | 1191 pts (16.5") | ❌ NO | Exactly A3 |
| A3 Landscape | 1191 pts (16.5") | 842 pts (11.7") | ❌ NO | Exactly A3 |
| Slightly bigger | 850 pts (11.8") | 1200 pts (16.7") | ✅ YES | Both edges exceed |
| Wide banner | 1440 pts (20") | 720 pts (10") | ❌ NO | One edge smaller |
| Tall scroll | 720 pts (10") | 1440 pts (20") | ❌ NO | One edge smaller |
| Large square | 900 pts (12.5") | 900 pts (12.5") | ❌ NO | One edge < 1191 |

**Pros:**
- ✅ Excludes standard A3 pages (both portrait and landscape)
- ✅ Only flags pages that are "truly" larger than A3 in all dimensions

**Cons:**
- ❌ Misses long/narrow documents (20" × 10" banner not flagged)
- ❌ Could miss documents that physically won't fit in A3 frame

---

### Option 2: Area-Based
**Definition:** A page is oversized if its area exceeds A3's area.

```python
def is_oversized_area_based(width, height):
    """Page is oversized if area exceeds A3 area."""
    A3_AREA = 842 * 1191  # = 1,002,822 square points (~193.05 sq inches)
    page_area = width * height
    return page_area > A3_AREA
```

#### Examples:

| Page Size | Width | Height | Area (pts²) | A3 Area | Oversized? | Reason |
|-----------|-------|--------|-------------|---------|------------|--------|
| A3 Portrait | 842 | 1191 | 1,002,822 | 1,002,822 | ❌ NO | Exactly A3 |
| Slightly bigger | 850 | 1200 | 1,020,000 | 1,002,822 | ✅ YES | Area exceeds |
| Wide banner | 1440 | 720 | 1,036,800 | 1,002,822 | ✅ YES | Area exceeds |
| Long thin | 1440 | 360 | 518,400 | 1,002,822 | ❌ NO | Area less |
| Large square | 1100 | 1100 | 1,210,000 | 1,002,822 | ✅ YES | Area exceeds |

**Pros:**
- ✅ Intuitive: "more paper = oversized"
- ✅ Catches most large pages regardless of shape
- ✅ Mathematically clean

**Cons:**
- ❌ Misses very long/narrow documents (20" × 5" has less area than A3)
- ❌ Area doesn't directly relate to filming capability

---

### Option 3: Max-Dimension-Based
**Definition:** A page is oversized if ANY dimension exceeds A3's largest dimension.

```python
def is_oversized_max_dimension(width, height):
    """Page is oversized if maximum dimension exceeds A3's max dimension."""
    A3_MAX_DIMENSION = 1191  # 16.5 inches (longest side of A3)
    max_dimension = max(width, height)
    return max_dimension > A3_MAX_DIMENSION
```

#### Examples:

| Page Size | Width | Height | Max Dim | A3 Max | Oversized? | Reason |
|-----------|-------|--------|---------|--------|------------|--------|
| A3 Portrait | 842 | 1191 | 1191 | 1191 | ❌ NO | Exactly A3 |
| A3 Landscape | 1191 | 842 | 1191 | 1191 | ❌ NO | Exactly A3 |
| Slightly taller | 842 | 1200 | 1200 | 1191 | ✅ YES | Exceeds max |
| Wide banner | 1440 | 720 | 1440 | 1191 | ✅ YES | Exceeds max |
| Tall scroll | 720 | 1440 | 1440 | 1191 | ✅ YES | Exceeds max |
| Long thin | 1440 | 360 | 1440 | 1191 | ✅ YES | Exceeds max |
| Letter landscape | 792 | 612 | 792 | 1191 | ❌ NO | Within bounds |

**Pros:**
- ✅ Physical reality: page won't fit in frame if any dimension too large
- ✅ Catches all long/narrow documents
- ✅ Simple and conservative
- ✅ Orientation-independent

**Cons:**
- ❌ Most aggressive - flags more pages as oversized
- ❌ Could be overly conservative

---

### Option 4: Min-Max-Based (Smart Fit)
**Definition:** A page is oversized if it cannot fit within A3 bounds when optimally rotated.

```python
def is_oversized_smart_fit(width, height):
    """Page is oversized if it can't fit within A3 bounds in any orientation."""
    # Get min and max dimensions (orientation-independent)
    min_dim = min(width, height)
    max_dim = max(width, height)
    
    # A3 bounds: 842 × 1191 (smaller × larger)
    A3_MIN = 842   # 11.7 inches (shorter side)
    A3_MAX = 1191  # 16.5 inches (longer side)
    
    # Page fits if both conditions true:
    # - Shorter dimension ≤ A3 shorter dimension
    # - Longer dimension ≤ A3 longer dimension
    return (min_dim > A3_MIN or max_dim > A3_MAX)
```

#### Examples:

| Page Size | Width | Height | Min | Max | A3 Min/Max | Oversized? | Reason |
|-----------|-------|--------|-----|-----|------------|------------|--------|
| A3 Portrait | 842 | 1191 | 842 | 1191 | 842/1191 | ❌ NO | Perfect fit |
| A3 Landscape | 1191 | 842 | 842 | 1191 | 842/1191 | ❌ NO | Perfect fit |
| Slightly bigger | 850 | 1200 | 850 | 1200 | 842/1191 | ✅ YES | Both exceed |
| Wide banner | 1440 | 720 | 720 | 1440 | 842/1191 | ✅ YES | Max exceeds |
| Tall scroll | 720 | 1440 | 720 | 1440 | 842/1191 | ✅ YES | Max exceeds |
| Long thin | 1440 | 360 | 360 | 1440 | 842/1191 | ✅ YES | Max exceeds |
| Slightly wider | 900 | 1191 | 900 | 1191 | 842/1191 | ✅ YES | Min exceeds |
| Letter portrait | 612 | 792 | 612 | 792 | 842/1191 | ❌ NO | Fits |

**Pros:**
- ✅ Most accurate: "can this physically fit in A3 frame?"
- ✅ Orientation-independent
- ✅ Catches all cases that won't physically fit
- ✅ Logical: checks both dimensions against their respective limits

**Cons:**
- ❌ Slightly more complex logic
- ❌ More aggressive than Option 1

---

## Comparison Summary

### Test Cases Comparison

| Page Dimensions | Option 1<br/>(Edge-Based) | Option 2<br/>(Area-Based) | Option 3<br/>(Max-Dim) | Option 4<br/>(Smart-Fit) |
|-----------------|---------------------------|---------------------------|------------------------|--------------------------|
| 842 × 1191 (A3) | ❌ NO | ❌ NO | ❌ NO | ❌ NO |
| 850 × 1200 | ✅ YES | ✅ YES | ✅ YES | ✅ YES |
| 1440 × 720 (20"×10") | ❌ NO | ✅ YES | ✅ YES | ✅ YES |
| 1440 × 360 (20"×5") | ❌ NO | ❌ NO | ✅ YES | ✅ YES |
| 900 × 900 (12.5"²) | ❌ NO | ✅ YES | ❌ NO | ✅ YES |
| 900 × 1191 | ❌ NO | ✅ YES | ❌ NO | ✅ YES |

### Aggressiveness Ranking
(Most to Least Oversized Pages Detected)

1. **Option 3 (Max-Dimension)** - Most aggressive, catches everything with any dimension > 16.5"
2. **Option 4 (Smart-Fit)** - Catches anything that won't fit in A3 frame
3. **Option 2 (Area-Based)** - Catches pages with more surface area than A3
4. **Option 1 (Edge-Based)** - Least aggressive, only flags "truly" larger pages

---

## Recommendation Decision Tree

### Question 1: What is the physical constraint of microfilming?

**If the filming equipment has a fixed A3-sized frame:**
→ Use **Option 4 (Smart-Fit)** or **Option 3 (Max-Dimension)**

**Reason:** Any page that won't physically fit in the frame needs 35mm, regardless of shape.

### Question 2: Is there flexibility in how pages are filmed?

**If pages can be filmed at angles, scaled, or tiled:**
→ Use **Option 1 (Edge-Based)** (current implementation)

**Reason:** Only truly large pages (bigger in ALL dimensions) need special handling.

### Question 3: Is the concern about document readability?

**If oversized = "too much content to read clearly on 16mm":**
→ Use **Option 2 (Area-Based)**

**Reason:** More surface area = more content = needs larger film format.

---

## Recommended Solution

Based on the microfilm industry and physical constraints:

### **Use Option 4: Smart-Fit Detection**

```python
def is_oversized_page(page) -> bool:
    """
    Check if a page is oversized (won't fit within A3 bounds).
    A page is oversized if it cannot fit within A3 dimensions
    when optimally rotated.
    
    A3 dimensions: 11.7" × 16.5" (842 × 1191 points)
    """
    rect = page.rect
    width = rect.width
    height = rect.height
    
    # Get orientation-independent dimensions
    min_dim = min(width, height)
    max_dim = max(width, height)
    
    # A3 bounds (smaller × larger dimension)
    A3_WIDTH = 842   # 11.7 inches
    A3_HEIGHT = 1191  # 16.5 inches
    
    # Page is oversized if it exceeds A3 in either dimension
    return (min_dim > A3_WIDTH or max_dim > A3_HEIGHT)
```

### Why This Is Best:

1. **Physical Accuracy:** Directly answers "will this fit in A3 frame?"
2. **Catches Edge Cases:** Includes banners, scrolls, and unusual dimensions
3. **Orientation-Independent:** Doesn't matter how page is rotated
4. **Conservative:** Better to flag something as oversized than miss it
5. **Clear Logic:** Easy to explain and understand

### Migration Path:

1. **Update scanner** to use Smart-Fit logic
2. **Run scanner** on production data to compare results
3. **Analyze differences** between current and new logic
4. **Review sample cases** with stakeholders
5. **Update production code** if approved
6. **Document decision** for future reference

---

## Testing Recommendations

### Test Cases to Validate:

```python
test_cases = [
    # (width, height, expected_oversized, description)
    (842, 1191, False, "A3 Portrait - exact"),
    (1191, 842, False, "A3 Landscape - exact"),
    (841, 1190, False, "Just under A3"),
    (843, 1192, True, "Just over A3"),
    (1440, 720, True, "Wide banner (20×10)"),
    (720, 1440, True, "Tall scroll (10×20)"),
    (1440, 360, True, "Very wide banner (20×5)"),
    (900, 900, True, "Square larger than A3 width"),
    (612, 792, False, "Letter size"),
    (792, 1224, True, "Tabloid (11×17)"),
]
```

### Scanner Usage:

```bash
# Run with current logic
python large_range_scanner.py X:\ --output current_logic.json

# Update to new logic, run again
python large_range_scanner.py X:\ --output new_logic.json

# Compare results
python compare_oversized_detection.py current_logic.json new_logic.json
```

---

## Implementation Checklist

- [ ] Update `.tools/pdftools/largerangescanner/large_range_scanner.py`
- [ ] Update `micro/microapp/services/analyze_service.py`
- [ ] Update `übergabe/microexcel/microfilm/document_service.py`
- [ ] Add test cases to validate new logic
- [ ] Run scanner on sample data
- [ ] Compare old vs new results
- [ ] Document any breaking changes
- [ ] Update API documentation if needed
- [ ] Update user documentation

---

## Questions for Stakeholders

1. **Physical Constraint:** What is the actual filming frame size? Is it exactly A3?
2. **Edge Cases:** How should we handle 20" × 10" banners? 35mm or special handling?
3. **Historical Data:** Are there known issues with current detection missing oversized pages?
4. **Tolerance:** Should there be a small tolerance (e.g., A3 + 5%) before flagging as oversized?
5. **Business Rules:** Are there document types that should always go to 35mm regardless of size?

---

## Decision Made

**APPROVED: Smart-Fit Logic (Option 4)**

After analysis and testing, the decision has been made to use **Option 4: Smart-Fit Detection**.

### Final Implementation

```python
def is_oversized_page(page) -> bool:
    """
    Check if a page is oversized (won't fit within A3 bounds).
    A page is oversized if it cannot fit within A3 dimensions when optimally rotated.
    
    A3 dimensions: 11.7" × 16.5" (842 × 1191 points)
    """
    rect = page.rect
    width = rect.width
    height = rect.height
    
    # Get orientation-independent dimensions
    shorter = min(width, height)
    longer = max(width, height)
    
    # A3 bounds: 11.7" × 16.5" (842 × 1191 points)
    A3_WIDTH = 842   # 11.7 inches (shorter side)
    A3_HEIGHT = 1191  # 16.5 inches (longer side)
    
    # Page is oversized if it exceeds A3 in either dimension
    # This can be simplified to:
    return (shorter > A3_WIDTH or longer > A3_HEIGHT)
```

### Simplified Formula

```python
shorter = min(width, height)
longer  = max(width, height)

oversized = (shorter > 11.7") OR (longer > 16.5")
```

### Why This Was Chosen

1. **✅ Physical Accuracy** - Directly answers "will this fit in A3 frame?"
2. **✅ Catches All Edge Cases** - Includes banners (20"×10"), scrolls, and unusual dimensions
3. **✅ Excludes Standard Sizes** - A3 pages (both portrait and landscape) are NOT flagged
4. **✅ Orientation-Independent** - Works regardless of how page is rotated
5. **✅ Simple Logic** - Easy to understand, implement, and explain
6. **✅ Conservative** - Better to flag something as oversized than miss it

### Validation Results

All test cases pass:

| Test Case | Width | Height | Shorter | Longer | Expected | Result | Status |
|-----------|-------|--------|---------|--------|----------|--------|--------|
| A3 Portrait | 842 | 1191 | 842 | 1191 | NO | ❌ NO | ✅ PASS |
| A3 Landscape | 1191 | 842 | 842 | 1191 | NO | ❌ NO | ✅ PASS |
| Just over A3 | 843 | 1192 | 843 | 1192 | YES | ✅ YES | ✅ PASS |
| Wide banner | 1440 | 720 | 720 | 1440 | YES | ✅ YES | ✅ PASS |
| Tall scroll | 720 | 1440 | 720 | 1440 | YES | ✅ YES | ✅ PASS |
| Very wide | 1440 | 360 | 360 | 1440 | YES | ✅ YES | ✅ PASS |
| Slightly wider | 900 | 1191 | 900 | 1191 | YES | ✅ YES | ✅ PASS |
| Large square | 900 | 900 | 900 | 900 | YES | ✅ YES | ✅ PASS |
| Letter | 612 | 792 | 612 | 792 | NO | ❌ NO | ✅ PASS |
| Tabloid | 792 | 1224 | 792 | 1224 | YES | ✅ YES | ✅ PASS |

**All 10 test cases passed! ✅**

### Next Steps

1. ✅ Logic validated and approved
2. ⏳ Update scanners to use Smart-Fit logic
3. ⏳ Run production scan to quantify impact
4. ⏳ Update production code after validation
5. ⏳ Document changes in system documentation

---

## Conclusion

The **Smart-Fit logic (Option 4)** has been approved as the official oversized page detection method. This approach ensures all pages that won't physically fit in an A3 frame are properly handled on 35mm film, while correctly excluding standard A3 pages. The logic is simple, accurate, and catches all edge cases.

**Implementation Formula:**
```python
shorter = min(width, height)
longer = max(width, height)
oversized = (shorter > 842 points) OR (longer > 1191 points)
```

Or in inches:
```python
oversized = (shorter > 11.7") OR (longer > 16.5")
```

