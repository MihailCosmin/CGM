#!/usr/bin/env python3
"""
Batch CGM Conversion Test
Tests the improved Python CGM converter on all batch test files
Shows before/after comparison of unknown commands
"""
import os
import sys
import subprocess
from pathlib import Path


def run_conversion(cgm_file, output_file):
    """Run CGM conversion using main.py"""
    try:
        result = subprocess.run([
            sys.executable, '../../main.py', cgm_file, output_file
        ], capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Conversion timed out"


def count_unknown_commands(cleartext_file):
    """Count unknown commands in a cleartext file"""
    try:
        with open(cleartext_file, 'r') as f:
            content = f.read()
            return content.count('Unknown command')
    except FileNotFoundError:
        return -1


def analyze_unknown_commands(cleartext_file):
    """Analyze types of unknown commands"""
    commands = {}
    try:
        with open(cleartext_file, 'r') as f:
            for line in f:
                if 'Unknown command' in line:
                    # Extract Class=X, ID=Y
                    if 'Class=' in line and 'ID=' in line:
                        class_part = line.split('Class=')[1].split(',')[0].strip()
                        id_part = line.split('ID=')[1].split()[0].strip()
                        key = f"Class={class_part}, ID={id_part}"
                        commands[key] = commands.get(key, 0) + 1
        return commands
    except FileNotFoundError:
        return {}


def main():
    """Main batch conversion test"""
    print("🔧 CGM Batch Conversion Test")
    print("="*50)
    
    # Find all CGM files
    cgm_files = list(Path('.').glob('*.CGM'))
    if not cgm_files:
        print("❌ No CGM files found in current directory!")
        return
    
    print(f"📂 Found {len(cgm_files)} CGM files")
    print()
    
    total_before = 0
    total_after = 0
    successful_conversions = 0
    
    results = []
    
    for cgm_file in sorted(cgm_files)[:5]:  # Test first 5 files
        print(f"🔄 Processing: {cgm_file.name}")
        
        # Find corresponding cleartext file  
        original_cleartext = f"{cgm_file.stem}cleartext.cgm"
        new_cleartext = f"fixed_{cgm_file.stem}.cgm"
        
        # Count unknown commands in original
        unknown_before = count_unknown_commands(original_cleartext)
        
        # Run conversion
        success, stdout, stderr = run_conversion(str(cgm_file), new_cleartext)
        
        if success:
            unknown_after = count_unknown_commands(new_cleartext)
            successful_conversions += 1
            
            if unknown_before >= 0:
                total_before += unknown_before
                total_after += unknown_after
                improvement = unknown_before - unknown_after
                percentage = (improvement / unknown_before * 100) if unknown_before > 0 else 0
                
                print(f"  ✅ Success: {unknown_before} → {unknown_after} unknown commands")
                print(f"     📈 Improvement: -{improvement} ({percentage:.1f}%)")
                
                results.append({
                    'file': cgm_file.name,
                    'before': unknown_before,
                    'after': unknown_after,
                    'improvement': improvement,
                    'percentage': percentage
                })
            else:
                print(f"  ✅ Success (no original cleartext for comparison)")
        else:
            print(f"  ❌ Failed: {stderr}")
        
        print()
    
    # Summary
    print("="*50)
    print("📊 BATCH CONVERSION SUMMARY")
    print("="*50)
    print(f"Successful conversions: {successful_conversions}/{len(cgm_files[:5])}")
    
    if total_before > 0:
        overall_improvement = total_before - total_after
        overall_percentage = (overall_improvement / total_before * 100)
        
        print(f"Total unknown commands before: {total_before:,}")
        print(f"Total unknown commands after:  {total_after:,}")
        print(f"Overall improvement: -{overall_improvement:,} ({overall_percentage:.1f}%)")
        
        print("\n🏆 BEST IMPROVEMENTS:")
        for result in sorted(results, key=lambda x: x['improvement'], reverse=True)[:3]:
            print(f"  {result['file']}: -{result['improvement']} commands ({result['percentage']:.1f}%)")
    
    # Analyze remaining unknown commands
    if results:
        print(f"\n🔍 REMAINING UNKNOWN COMMANDS (sample from {results[0]['file']}):")
        remaining_commands = analyze_unknown_commands(f"fixed_{results[0]['file'].replace('.CGM', '')}.cgm")
        for cmd, count in sorted(remaining_commands.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {cmd}: {count} occurrences")


if __name__ == "__main__":
    main()