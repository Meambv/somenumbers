<!-- 2025_11_29_@_22-20-44 -->
# First-Login Code Generator

Python script to generate encoded first-login arrays for the MEAM Project Management System.

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## Usage

### Basic Syntax

```bash
python generate_firstlogin_codes.py --level <1|2|3> --aud <audience_id>
```

### Parameters

- `--level`: Access tier level
  - `3` = FULL tier (access levels 0, 1, 2)
  - `2` = RESTRICTED tier (access levels 3, 4, 5)
  - `1` = BASIC tier (access levels 6, 7, 8)

- `--aud`: Cloudflare Access audience ID from JWT (required)

- `--output`: Path to somenumbers.json file (default: `somenumbers.json`)

- `--dry-run`: Generate array but don't update file (for testing)

### Examples

#### Generate FULL Tier First-Login Code

```bash
python generate_firstlogin_codes.py \
  --level 3 \
  --aud "edd14b346f89ff0ed94a4eadeBf7ba2e6b7a81dbf3ce0ba00372333d4c968f38f"
```

Output:
```
📦 Generating first-login array:
   Level: 3 (FULL)
   Worker URL: https://z3c9h1-qs7f5l2p8.johan-351.workers.dev
   Bootstrap PIN: 5329
   Payload: MEAM https://z3c9h1-qs7f5l2p8.johan-351.workers.dev tier3@meam-firstlogin.internal
   Payload length: 98 characters
   Audience ID: edd14b346f89ff0ed94a...7ba2e6b7a81dbf3ce0ba00372333d4c968f38f
   Encoded array length: 98 values
   Key name: firstlogin_level3_edd14b346f89ff0ed94a4eadeBf7ba2e6b7a81dbf3ce0ba00372333d4c968f38f

✅ Updated somenumbers.json
   Added key: firstlogin_level3_edd14b346f89ff0ed94a4eadeBf7ba2e6b7a81dbf3ce0ba00372333d4c968f38f
   Total keys in file: 4

✨ Success!

Next steps:
1. Review the changes: git diff somenumbers.json
2. Commit: git add somenumbers.json && git commit -m 'Add first-login code for level 3'
3. Push: git push
4. Deploy to Cloudflare Pages to update /api/somenumbers endpoint

Bootstrap PIN for this tier: 5329
Access level constraint: accessLevel < 3 (levels 0, 1, 2)
```

#### Generate RESTRICTED Tier First-Login Code

```bash
python generate_firstlogin_codes.py \
  --level 2 \
  --aud "abc123def456..."
```

#### Generate BASIC Tier First-Login Code

```bash
python generate_firstlogin_codes.py \
  --level 1 \
  --aud "xyz789uvw012..."
```

#### Dry Run (Test Without Saving)

```bash
python generate_firstlogin_codes.py \
  --level 3 \
  --aud "test_audience_id" \
  --dry-run
```

Output:
```
🔍 DRY RUN - No files modified

Generated array preview (first 10 values):
[1234567, 2345678, 3456789, 4567890, 5678901, 6789012, 7890123, 8901234, 9012345, 1023456]
```

#### Custom Output Path

```bash
python generate_firstlogin_codes.py \
  --level 3 \
  --aud "edd14b346..." \
  --output ./custom/path/somenumbers.json
```

## How It Works

### 1. Payload Construction

The script constructs a payload in the format:
```
MEAM <worker_url> tier<X>@meam-firstlogin.internal
```

Example for FULL tier:
```
MEAM https://z3c9h1-qs7f5l2p8.johan-351.workers.dev tier3@meam-firstlogin.internal
```

### 2. Encoding Algorithm

Each character in the payload is encoded using:
```python
encoded_value = char_ascii * aud_char_ascii * pin_digit_multiplier
```

Where:
- `char_ascii`: ASCII code of the payload character
- `aud_char_ascii`: ASCII code of the audience ID character (with wrapping)
- `pin_digit_multiplier`: Digit from bootstrap PIN (0 becomes 10)

### 3. Output Format

The encoded array is saved to `somenumbers.json` with the key:
```
firstlogin_level<X>_<audience_id>
```

Example:
```json
{
  "somenumbers": [...],
  "firstlogin_level3_edd14b346f89ff0ed94a4eadeBf7ba2e6b7a81dbf3ce0ba00372333d4c968f38f": [
    1234567, 2345678, 3456789, ...
  ]
}
```

## Tier Configuration

| Level | Tier | Bootstrap PIN | Worker URL | Access Levels |
|-------|------|--------------|------------|---------------|
| 3 | FULL | 5329 | `z3c9h1-qs7f5l2p8` | 0, 1, 2 |
| 2 | RESTRICTED | 5229 | `m4v8k2-rb6n0t3y9` | 3, 4, 5 |
| 1 | BASIC | 5129 | `h7p3w5-xd1q6e4z8` | 6, 7, 8 |

## Extracting Audience ID

### Method 1: Browser Console

1. Log into Cloudflare Access
2. Open browser DevTools (F12)
3. Go to Console tab
4. Run:
```javascript
// Extract from cookie
document.cookie.split('; ').find(row => row.startsWith('CF_Authorization'))

// Or extract from JWT in network request
// 1. Go to Network tab
// 2. Find request to your app
// 3. Look for 'cf-access-jwt-assertion' header
// 4. Copy the JWT
// 5. Decode at jwt.io to see 'aud' claim
```

### Method 2: Network Tab

1. Open DevTools → Network tab
2. Navigate to application
3. Find any request
4. Check Request Headers for `cf-access-jwt-assertion`
5. Copy JWT and decode at https://jwt.io
6. Extract `aud` value from payload

### Method 3: API Response

```javascript
// Call get-auth-headers without PIN
fetch('/api/get-auth-headers')
  .then(r => r.json())
  .then(data => console.log('AUD ID:', data.cloudflareAuth.audId));
```

## Troubleshooting

### Error: "Audience ID seems too short"

**Solution**: Provide the complete audience ID (usually 64+ characters)

```bash
# Wrong
python generate_firstlogin_codes.py --level 3 --aud "edd14b..."

# Correct
python generate_firstlogin_codes.py --level 3 --aud "edd14b346f89ff0ed94a4eadeBf7ba2e6b7a81dbf3ce0ba00372333d4c968f38f"
```

### Error: "Invalid level"

**Solution**: Use 1, 2, or 3

```bash
# Wrong
python generate_firstlogin_codes.py --level 0 --aud "..."

# Correct
python generate_firstlogin_codes.py --level 3 --aud "..."
```

### File Not Found: somenumbers.json

**Solution**: Run from the correct directory or use --output

```bash
# Option 1: Navigate to somenumbers directory
cd d:\somenumbers
python generate_firstlogin_codes.py --level 3 --aud "..."

# Option 2: Specify full path
python generate_firstlogin_codes.py --level 3 --aud "..." --output d:\somenumbers\somenumbers.json
```

## Security Notes

⚠️ **Bootstrap PINs**: Never expose in client code or public repositories

⚠️ **Audience IDs**: Specific to Cloudflare Access application

⚠️ **First-Login Codes**: Only work once per user per tier

⚠️ **somenumbers.json**: Keep in private repository only

## Integration

After generating first-login codes:

1. **Commit to GitHub**:
   ```bash
   git add somenumbers.json
   git commit -m "Add first-login codes"
   git push
   ```

2. **Deploy to Cloudflare Pages** (automatic or manual)

3. **Verify deployment**:
   ```bash
   curl https://your-domain.com/api/somenumbers
   ```

4. **Test decoding**:
   ```bash
   curl "https://your-domain.com/api/get-auth-headers?pin=5329"
   ```

5. **Provision user in users.json**

6. **Send bootstrap PIN to user** via secure channel

## Related Documentation

- [14_firstLoginSystem.md](../readmes/2025_11_29_@_22-20-44/14_firstLoginSystem.md) - Complete first-login flow
- [05_userAccessMatrix.md](../readmes/2025_11_29_@_22-20-44/05_userAccessMatrix.md) - Access levels and tiers
- [02_securityArchitecture.md](../readmes/2025_11_29_@_22-20-44/02_securityArchitecture.md) - Security model

## License

Internal tool for MEAM Project Management System. Not for public distribution.

