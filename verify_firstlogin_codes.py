#!/usr/bin/env python3
#2025_11_30_@_17-20-18
"""
Decode First-Login Arrays to Verify Encoding
"""

import json

# Known audience IDs
AUDIENCE_IDS = {
    'FULL': '2a1cae831a8b85fb7847b7aeedf2075cbe37316002f31ef308ebd5d4e5094e0d',
    'RESTRICTED': 'edc14b0fbb1c63640439b0c948515ddb63d15f6d2b2a7498c1d4f087a4706366',
    'BASIC': '27fbdc72fab0dcccf1ceba4aafe2d72f07e2167ae9a6ee9f67012222672c8ede'
}

# Bootstrap PINs
BOOTSTRAP_PINS = {
    'FULL': '5329',
    'RESTRICTED': '5229',
    'BASIC': '5129'
}

BASE_OFFSET = 13

def decode_payload(encoded_array, aud_id, pin):
    """Decode an encoded array back to the original payload."""
    pin_str = pin.zfill(4)[-4:]
    pin_digits = [int(d) for d in pin_str]
    
    decoded_chars = []
    aud_length = len(aud_id)
    
    for i, encoded_value in enumerate(encoded_array):
        # Get audience character
        aud_pos = BASE_OFFSET + i
        wrapped_index = aud_pos % aud_length
        aud_char = aud_id[wrapped_index]
        aud_ascii = ord(aud_char)
        
        # Get PIN digit multiplier
        pin_digit = pin_digits[i % len(pin_digits)]
        pin_multiplier = 10 if pin_digit == 0 else pin_digit
        
        # Calculate original character ASCII
        char_ascii = encoded_value / (aud_ascii * pin_multiplier)
        
        if not char_ascii.is_integer() or char_ascii < 32 or char_ascii > 126:
            return f"❌ DECODE ERROR at position {i}: Invalid character {char_ascii}"
        
        decoded_chars.append(chr(int(char_ascii)))
    
    return ''.join(decoded_chars)

# Load somenumbers.json
with open('somenumbers.json', 'r') as f:
    data = json.load(f)

print("="*80)
print("FIRST-LOGIN CODE VERIFICATION")
print("="*80)

for tier, aud_id in AUDIENCE_IDS.items():
    pin = BOOTSTRAP_PINS[tier]
    key_name = f"firstlogin_level{'3' if tier == 'FULL' else '2' if tier == 'RESTRICTED' else '1'}_{aud_id}"
    
    print(f"\n{'='*80}")
    print(f"🔍 {tier} TIER")
    print(f"{'='*80}")
    print(f"Audience ID: {aud_id}")
    print(f"Bootstrap PIN: {pin}")
    print(f"Key Name: {key_name}")
    
    if key_name in data:
        encoded_array = data[key_name]
        print(f"Encoded Array Length: {len(encoded_array)} values")
        print(f"First 5 values: {encoded_array[:5]}")
        
        # Decode
        decoded_payload = decode_payload(encoded_array, aud_id, pin)
        
        print(f"\n📤 DECODED PAYLOAD:")
        print(f"   {decoded_payload}")
        
        # Verify format
        if decoded_payload.startswith("MEAM https://"):
            parts = decoded_payload.split()
            if len(parts) >= 3:
                preamble = parts[0]
                worker_url = parts[1]
                email_marker = parts[2]
                
                print(f"\n✅ VERIFICATION:")
                print(f"   Preamble: {preamble} {'✓' if preamble == 'MEAM' else '✗'}")
                print(f"   Worker URL: {worker_url}")
                print(f"   Email Marker: {email_marker}")
                
                # Check email marker format
                expected_tier = f"tier{'3' if tier == 'FULL' else '2' if tier == 'RESTRICTED' else '1'}"
                if email_marker == f"{expected_tier}@meam-firstlogin.internal":
                    print(f"   Email Format: ✓ Correct ({expected_tier}@meam-firstlogin.internal)")
                else:
                    print(f"   Email Format: ✗ Expected {expected_tier}@meam-firstlogin.internal")
        else:
            print(f"\n❌ VERIFICATION FAILED: Payload doesn't start with 'MEAM https://'")
    else:
        print(f"❌ KEY NOT FOUND IN somenumbers.json")

print(f"\n{'='*80}")
print("VERIFICATION COMPLETE")
print(f"{'='*80}\n")
