# Fix for Gemini JSON Parsing Error

## Problem

Getting error: `Failed to parse Gemini response as JSON: Expecting property name enclosed in double quotes`

This happens when Gemini returns malformed JSON with:
- Markdown code blocks (```json ... ```)
- Trailing commas
- Comments (// or /* */)
- Single quotes instead of double quotes

## Solution Implemented

### 1. **Robust JSON Cleaning** ✅

Added automatic cleaning in `backend/models/intent_interpreter.py`:

```python
# Remove markdown code blocks
if content.startswith("```json"):
    content = content[7:]  # Remove ```json
elif content.startswith("```"):
    content = content[3:]  # Remove ```

if content.endswith("```"):
    content = content[:-3]  # Remove closing ```

# Remove trailing commas (common LLM mistake)
content = re.sub(r',(\s*[}\]])', r'\1', content)

# Remove comments
content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
```

**Handles:**
- ✅ Markdown code blocks (```json or ```)
- ✅ Trailing commas before } or ]
- ✅ Single-line comments (//)
- ✅ Multi-line comments (/* */)
- ✅ Extra whitespace

### 2. **Enhanced Debugging** ✅

Now shows detailed error information:

```
🤖 Gemini Response:
   Raw response: {...first 300 chars...}
   Cleaned JSON: {...first 200 chars...}
   ✅ Parsed successfully
```

**Or if it fails:**
```
❌ JSON parse error: Expecting property name enclosed in double quotes: line 9 column 3
   Full content:
   {actual JSON content shown here}
```

### 3. **Improved Gemini Prompt** ✅

Made the prompt MORE explicit about format:

```
OUTPUT FORMAT - CRITICAL INSTRUCTIONS:
- Return ONLY the JSON object below
- NO markdown formatting (no ```json or ``` blocks)
- NO comments in the JSON
- NO trailing commas
- Use double quotes for all strings
- Ensure all brackets and braces are properly closed
```

## Multi-Layer Protection

```
Gemini Response
      ↓
[Remove Markdown Blocks] ← Remove ``` wrappers
      ↓
[Remove Trailing Commas] ← Fix ,} and ,]
      ↓
[Remove Comments] ← Remove // and /* */
      ↓
[json.loads()] ← Parse cleaned JSON
      ↓
[Detailed Error if Fails] ← Show what went wrong
```

## Common Issues This Fixes

### Issue 1: Markdown Blocks
**Before:**
```
```json
{
  "campaign_goal": "conversion"
}
```
```

**After Cleaning:**
```json
{
  "campaign_goal": "conversion"
}
```

### Issue 2: Trailing Commas
**Before:**
```json
{
  "campaign_goal": "conversion",
  "underlying_assumptions": ["price_sensitive",]
}
```

**After Cleaning:**
```json
{
  "campaign_goal": "conversion",
  "underlying_assumptions": ["price_sensitive"]
}
```

### Issue 3: Comments
**Before:**
```json
{
  "campaign_goal": "conversion", // Main goal
  "target_behavior": "abandoned_cart"
}
```

**After Cleaning:**
```json
{
  "campaign_goal": "conversion",
  "target_behavior": "abandoned_cart"
}
```

## Testing

**Restart your backend:**
```powershell
python run.py
```

**Try your campaign analysis again:**
- The JSON cleaning will handle malformed responses automatically
- You'll see detailed debug output in the backend logs
- If it still fails, you'll see the exact JSON that couldn't be parsed

## What to Check If Still Failing

If you still get JSON parse errors after this fix:

1. **Check backend logs** for:
   ```
   🤖 Gemini Response:
      Raw response: {...}
      Cleaned JSON: {...}
      ❌ JSON parse error: ...
      Full content:
      {the actual problematic JSON}
   ```

2. **Share the "Full content"** - This shows exactly what Gemini returned after cleaning

3. **Check for:**
   - Unescaped quotes inside strings
   - Missing closing brackets
   - Invalid characters
   - Encoding issues

## Expected Behavior

### Before Fix:
```
❌ Frontend error: "Failed to parse Gemini response as JSON"
❌ Backend crash or generic error
❌ No visibility into what went wrong
```

### After Fix:
```
✅ Automatic cleaning of common JSON issues
✅ Detailed debug output showing raw → cleaned → parsed
✅ Specific error messages if parsing still fails
✅ Better Gemini prompt reduces issues
```

## Additional Benefits

- **More robust** - Handles multiple common LLM output issues
- **Better debugging** - See exactly what Gemini returned
- **Self-healing** - Automatically fixes trailing commas and comments
- **Informative errors** - Know exactly what to fix if it still fails

---

**Restart your backend and try again - JSON parsing is now much more robust!** 🚀

