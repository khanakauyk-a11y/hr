# Quick Reference: Hiring Limits

## Hierarchy Rules

```
HR/ADMIN (No Limits)
    │
    └─── Sales Manager (SM)
             ├─ Can hire: Assistant Manager only
             └─ Max: 3 AM
                   │
                   └─── Assistant Manager (AM)
                            ├─ Can hire: AM or RM
                            └─ Max: 1 AM + 2 RM (total 3)
                                  │
                                  └─── Relationship Manager (RM)
                                           ├─ Can hire: RM or SE
                                           └─ Max: 1 RM + 2 SE (total 3)
                                                 │
                                                 └─── Sales Executive (SE)
                                                          ├─ Can hire: SE or Agent
                                                          └─ Max: 1 SE + 2 Agents (total 3)
                                                                │
                                                                └─── Agent
                                                                     └─ Cannot hire
```

## Status Display

| Status | Badge Color | Meaning |
|--------|------------|---------|
| Empty | Gray | No subordinates hired |
| X/Y Hired (< 50%) | Green | Has capacity available |
| X/Y Hired (50-99%) | Orange | Near capacity |
| X/Y Hired (100%) | Red | At full capacity |

## Examples

### Example 1: Sales Manager
- Can hire: **3 Assistant Managers**
- Cannot hire: RM, SE, or Agents
- Display: "Empty" or "2/3 Hired"

### Example 2: Assistant Manager
- Can hire: **1 AM + 2 RM** (total 3 positions)
- Cannot hire: SE or Agents
- Display: "Empty" or "3/3 Hired"

### Example 3: Relationship Manager
- Can hire: **1 RM + 2 SE** (total 3 positions)
- Cannot hire: AM or Agents
- Display: "Empty" or "2/3 Hired"

### Example 4: Sales Executive
- Can hire: **1 SE + 2 Agents** (total 3 positions)
- Cannot hire: AM or RM
- Display: "Empty" or "3/3 Hired"

## Error Messages

When you try to exceed limits, you'll see:
- ✗ "Hiring limit reached: Sales Manager can hire max 3 Assistant Manager(s), currently has 3"
- ✗ "Sales Manager can only hire: Assistant Manager"
- ✗ "Sales Executive cannot hire any subordinates" (for roles with no hiring permission)

## Special Cases

- **HR Manager & HR Executive**: Can hire anyone, no limits
- **Admin roles**: No restrictions
- **Agents**: Cannot hire anyone
