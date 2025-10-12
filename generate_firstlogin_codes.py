#!/usr/bin/env python3
"""
Generate First-Login Encoded Arrays for MEAM Project Management System
=======================================================================

This script generates encoded arrays for first-time user login using bootstrap PINs.

Usage:
    python generate_firstlogin_codes.py --level <1|2|3> --aud <audience_id>

Parameters:
    --level: Access tier level (1=BASIC, 2=RESTRICTED, 3=FULL)
    --aud: Cloudflare Access audience ID from JWT

Example:
    python generate_firstlogin_codes.py --level 3 --aud "edd14b346f89ff0ed94a4eadeBf7ba2e6b7a81dbf3ce0ba00372333d4c968f38f"

Output:
    Updates somenumbers.json with new first-login encoded array
    Commits and pushes to GitHub repository
"""

import json
import argparse
import sys
from pathlib import Path

# Worker URLs by tier level
WORKER_URLS = {
    3: "https://z3c9h1-qs7f5l2p8.johan-351.workers.dev",  # FULL tier
    2: "https://m4v8k2-rb6n0t3y9.johan-351.workers.dev",  # RESTRICTED tier
    1: "https://h7p3w5-xd1q6e4z8.johan-351.workers.dev"   # BASIC tier
}

# Bootstrap PINs by tier level
BOOTSTRAP_PINS = {
    3: "5329",  # FULL tier: accessLevel < 3
    2: "5229",  # RESTRICTED tier: 2 < accessLevel < 6
    1: "5129"   # BASIC tier: accessLevel > 5
}

# Tier names for email marker
TIER_NAMES = {
    3: "tier3",
    2: "tier2",
    1: "tier1"
}

# Base offset for audience character wrapping (matches get-auth-headers.js)
BASE_OFFSET = 13


def encode_payload(payload: str, aud_id: str, pin: str) -> list:
    """
    Encode a payload string using audience ID and PIN.
    
    Encoding formula (must match get-auth-headers.js):
    encoded_value = char_ascii * aud_char_ascii * pin_digit_multiplier
    
    Args:
        payload: String to encode (e.g., "MEAM https://... tier3@meam-firstlogin.internal")
        aud_id: Cloudflare Access audience ID
        pin: 4-digit PIN string
        
    Returns:
        List of encoded integers
    """
    if not aud_id or not pin:
        raise ValueError("Audience ID and PIN are required")
    
    # Ensure PIN is 4 digits
    pin_str = pin.zfill(4)[-4:]
    pin_digits = [int(d) for d in pin_str]
    
    if len(pin_digits) != 4:
        raise ValueError("PIN must be exactly 4 digits")
    
    encoded_array = []
    aud_length = len(aud_id)
    
    for i, char in enumerate(payload):
        # Get character ASCII code
        char_ascii = ord(char)
        
        # Get audience character (with base offset and wrapping)
        aud_pos = BASE_OFFSET + i
        wrapped_index = aud_pos % aud_length
        aud_char = aud_id[wrapped_index]
        aud_ascii = ord(aud_char)
        
        # Get PIN digit multiplier (0 becomes 10)
        pin_digit = pin_digits[i % len(pin_digits)]
        pin_multiplier = 10 if pin_digit == 0 else pin_digit
        
        # Calculate encoded value
        encoded_value = char_ascii * aud_ascii * pin_multiplier
        encoded_array.append(encoded_value)
    
    return encoded_array


def generate_firstlogin_array(level: int, aud_id: str) -> tuple:
    """
    Generate a first-login encoded array for a specific tier level.
    
    Args:
        level: Tier level (1=BASIC, 2=RESTRICTED, 3=FULL)
        aud_id: Cloudflare Access audience ID
        
    Returns:
        Tuple of (key_name, encoded_array)
    """
    if level not in WORKER_URLS:
        raise ValueError(f"Invalid level: {level}. Must be 1, 2, or 3")
    
    worker_url = WORKER_URLS[level]
    bootstrap_pin = BOOTSTRAP_PINS[level]
    tier_name = TIER_NAMES[level]
    
    # Construct the payload
    # Format: "MEAM <worker_url> tier*@meam-firstlogin.internal"
    payload = f"MEAM {worker_url} {tier_name}@meam-firstlogin.internal"
    
    print(f"\n📦 Generating first-login array:")
    print(f"   Level: {level} ({'FULL' if level == 3 else 'RESTRICTED' if level == 2 else 'BASIC'})")
    print(f"   Worker URL: {worker_url}")
    print(f"   Bootstrap PIN: {bootstrap_pin}")
    print(f"   Payload: {payload}")
    print(f"   Payload length: {len(payload)} characters")
    print(f"   Audience ID: {aud_id[:20]}...{aud_id[-20:]}")
    
    # Encode the payload
    encoded_array = encode_payload(payload, aud_id, bootstrap_pin)
    
    # Create key name: firstlogin_level*_<aud_id>
    key_name = f"firstlogin_level{level}_{aud_id}"
    
    print(f"   Encoded array length: {len(encoded_array)} values")
    print(f"   Key name: {key_name}")
    
    return key_name, encoded_array


def update_somenumbers_json(key_name: str, encoded_array: list, somenumbers_path: Path):
    """
    Update somenumbers.json with the new first-login array.
    
    Args:
        key_name: Key name for the encoded array
        encoded_array: Encoded array values
        somenumbers_path: Path to somenumbers.json
    """
    # Load existing somenumbers.json
    if somenumbers_path.exists():
        with open(somenumbers_path, 'r') as f:
            data = json.load(f)
    else:
        data = {"somenumbers": []}
    
    # Add the new first-login array
    data[key_name] = encoded_array
    
    # Save back to file
    with open(somenumbers_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Updated {somenumbers_path}")
    print(f"   Added key: {key_name}")
    print(f"   Total keys in file: {len(data)}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate first-login encoded arrays for MEAM system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate FULL tier first-login code
  python generate_firstlogin_codes.py --level 3 --aud "edd14b346f89..."

  # Generate RESTRICTED tier first-login code
  python generate_firstlogin_codes.py --level 2 --aud "abc123def456..."

  # Generate BASIC tier first-login code
  python generate_firstlogin_codes.py --level 1 --aud "xyz789uvw012..."
        """
    )
    
    parser.add_argument(
        '--level',
        type=int,
        required=True,
        choices=[1, 2, 3],
        help='Access tier level: 1=BASIC (levels 6-8), 2=RESTRICTED (levels 3-5), 3=FULL (levels 0-2)'
    )
    
    parser.add_argument(
        '--aud',
        type=str,
        required=True,
        help='Cloudflare Access audience ID from JWT'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='somenumbers.json',
        help='Path to somenumbers.json file (default: somenumbers.json)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate array but do not update file'
    )
    
    args = parser.parse_args()
    
    # Validate audience ID
    if not args.aud or len(args.aud) < 10:
        print("❌ Error: Audience ID seems too short. Please provide the full audience ID from JWT.")
        sys.exit(1)
    
    try:
        # Generate the first-login array
        key_name, encoded_array = generate_firstlogin_array(args.level, args.aud)
        
        if args.dry_run:
            print("\n🔍 DRY RUN - No files modified")
            print(f"\nGenerated array preview (first 10 values):")
            print(encoded_array[:10])
        else:
            # Update somenumbers.json
            somenumbers_path = Path(args.output)
            update_somenumbers_json(key_name, encoded_array, somenumbers_path)
            
            print(f"\n✨ Success!")
            print(f"\nNext steps:")
            print(f"1. Review the changes: git diff {args.output}")
            print(f"2. Commit: git add {args.output} && git commit -m 'Add first-login code for level {args.level}'")
            print(f"3. Push: git push")
            print(f"4. Deploy to Cloudflare Pages to update /api/somenumbers endpoint")
            print(f"\nBootstrap PIN for this tier: {BOOTSTRAP_PINS[args.level]}")
            print(f"Access level constraint: {get_constraint_description(args.level)}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def get_constraint_description(level: int) -> str:
    """Get human-readable description of access level constraint."""
    if level == 3:
        return "accessLevel < 3 (levels 0, 1, 2)"
    elif level == 2:
        return "2 < accessLevel < 6 (levels 3, 4, 5)"
    elif level == 1:
        return "accessLevel > 5 (levels 6, 7, 8)"
    return "Unknown"


if __name__ == '__main__':
    main()
