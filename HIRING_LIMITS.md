# Hiring Hierarchy Limits - Simplified

## Summary
Simplified organizational hierarchy with hiring limits enforced.

### Roles Available

1. **Sales Manager (SM)** - Top sales leadership
2. **Assistant Manager (AM)** - Mid-level management
3. **Relationship Manager (RM)** - Client relationship management
4. **Agent** - Front-line sales staff
5. **HR Manager** - Human resources leadership
6. **HR Executive** - HR operations

---

## Hierarchy Structure

```
HR Manager / HR Executive (No Limits)
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
                                           ├─ Can hire: Agents only
                                           └─ Max: 3 Agents
                                                 │
                                                 └─── Agent
                                                      └─ Cannot hire
```

---

## Hiring Limits

| Role | Can Hire | Max Limit | Notes |
|------|----------|-----------|-------|
| **Sales Manager** | Assistant Manager | 3 AM | Top of sales hierarchy |
| **Assistant Manager** | AM, RM | 1 AM + 2 RM (3 total) | Can build mixed teams |
| **Relationship Manager** | Agent | 3 Agents | Manages front-line staff |
| **Agent** | - | 0 | Cannot hire |
| **HR Manager** | Anyone | No limit | Admin role |
| **HR Executive** | Anyone | No limit | Admin role |

---

## Status Display

Hiring capacity is shown with color-coded badges:

| Status | Badge | Description |
|--------|-------|-------------|
| Empty | Gray | No subordinates hired |
| X/Y Hired (< 50%) | Green | Good capacity available |
| X/Y Hired (50-99%) | Orange | Near capacity |
| X/Y Hired (100%) | Red | At full capacity |

---

## Example Scenarios

### Scenario 1: Sales Manager
- **Umar (SM)** wants to hire team
- Can hire: **3 Assistant Managers**
- Cannot hire: RM or Agents directly
- Status: "Empty" → "1/3 Hired" → "2/3 Hired" → "3/3 Hired"

### Scenario 2: Assistant Manager
- **Priya (AM)** reporting to Umar
- Can hire: **1 AM + 2 RM** (total 3)
- Cannot hire: Agents directly
- Possible combinations:
  - 1 AM + 2 RM ✓
  - 0 AM + 2 RM ✓
  - 1 AM + 1 RM ✓
  - 2 AM + 0 RM ✗ (exceeds AM limit)

### Scenario 3: Relationship Manager
- **Raj (RM)** reporting to Priya
- Can hire: **3 Agents**
- Cannot hire: AM, RM, or other roles
- Status: "Empty" → "1/3 Hired" → "2/3 Hired" → "3/3 Hired"

---

## Validation & Error Messages

### Exceeded Limits
```
✗ "Hiring limit reached: Sales Manager can hire max 3 Assistant Manager(s), currently has 3"
```

### Wrong Role Type
```
✗ "Sales Manager can only hire: Assistant Manager"
```

### No Hiring Permission
```
✗ "Agent cannot hire any subordinates"
```

---

## Changes from Previous Version

**Removed Roles:**
- ❌ Senior Sales Manager
- ❌ Assistant Sales Manager
- ❌ Sales Executive
- ❌ Agent Relationship Manager (merged to Relationship Manager)
- ❌ Agent Manager
- ❌ Assistant General Manager
- ❌ Senior Retainer
- ❌ Tele Caller
- ❌ Trainer
- ❌ IT Manager
- ❌ IT Executive
- ❌ IT Graphic Designer

**Updated Hierarchy:**
- SM → AM → RM → Agent (simplified 4-level structure)
- RM now hires Agents directly (no intermediate SE level)
- AM can hire other AMs for lateral expansion

---

## Testing Checklist

- [ ] SM can hire max 3 AM
- [ ] AM can hire 1 AM + 2 RM
- [ ] RM can hire 3 Agents
- [ ] Agent cannot hire anyone
- [ ] HR roles can hire anyone
- [ ] Tree shows "Empty" or "X/Y Hired"
- [ ] Color coding works (gray/green/orange/red)
- [ ] Old roles are no longer available in dropdowns
